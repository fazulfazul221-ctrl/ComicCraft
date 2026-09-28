import os
import re
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

pipe = None

def sanitize_filename(prompt: str) -> str:
    """Sanitize the prompt into a safe, valid filename."""
    # Remove non-alphanumeric characters and replace spaces with underscores
    clean = re.sub(r'[^a-zA-Z0-9_\- ]', '', prompt)
    clean = re.sub(r'\s+', '_', clean.strip())
    # Keep first 40 chars to avoid excessively long filenames
    clean = clean[:40].strip('_')
    if not clean:
        clean = "panel_image"
    return f"{clean}.png"

def get_pipeline():
    """Lazily load StableDiffusionPipeline when needed."""
    global pipe
    if pipe is not None:
        return pipe

    # Only attempt 4GB model download if specifically enabled or local weights exist
    if os.getenv("ENABLE_SD_DOWNLOAD", "0") != "1":
        return None

    try:
        import torch
        from diffusers import StableDiffusionPipeline

        model_id = "runwayml/stable-diffusion-v1-5"
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
            use_safetensors=True
        )
        pipe = pipe.to(device)
        return pipe
    except Exception as e:
        print(f"⚠️ Could not load StableDiffusionPipeline ({e}). Using comic panel renderer.")
        return None

def create_fallback_image(prompt: str, target_path: str):
    """Generates an aesthetic comic-style panel image when local SD pipeline is unavailable."""
    width, height = 512, 512
    # Create comic panel background
    img = Image.new("RGB", (width, height), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)

    # Comic border
    border_color = (25, 30, 45)
    border_width = 8
    draw.rectangle([border_width, border_width, width - border_width, height - border_width], outline=border_color, width=border_width)
    
    # Inner comic panel box with gradient/accent header
    draw.rectangle([border_width + 4, border_width + 4, width - border_width - 4, 70], fill=(41, 128, 185))

    # Header text
    try:
        font_header = ImageFont.truetype("static/fonts/DejaVuSans.ttf", 22)
        font_body = ImageFont.truetype("static/fonts/DejaVuSans.ttf", 16)
        font_small = ImageFont.truetype("static/fonts/DejaVuSans.ttf", 13)
    except Exception:
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((border_width + 16, border_width + 14), "COMICCRAFT ILLUSTRATION", fill=(255, 255, 255), font=font_header)

    # Prompt text display in panel
    import textwrap
    lines = textwrap.wrap(prompt, width=45)
    y_text = 100
    draw.text((30, y_text), "Scene Prompt:", fill=(100, 110, 120), font=font_small)
    y_text += 25
    for line in lines[:8]:
        draw.text((30, y_text), line, fill=(33, 37, 41), font=font_body)
        y_text += 26

    # Bottom comic action banner
    draw.rectangle([border_width + 4, height - 70, width - border_width - 4, height - border_width - 4], fill=(235, 240, 245))
    draw.text((30, height - 55), "AI Comic Story Panel - Visual Scene", fill=(70, 80, 95), font=font_small)

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    img.save(target_path)
    return target_path

def generate_image(prompt: str, filename: str = None) -> str:
    """
    Generate a comic‑style image for *prompt*.
    Uses a local Stable Diffusion pipeline when available, otherwise falls back to
    the Hugging Face Inference API (requires ``HF_API_KEY``), and finally to the
    simple placeholder renderer.
    Returns the absolute path of the saved PNG file.
    """
    if not filename:
        filename = sanitize_filename(prompt)

    path = f"static/panels/{filename}"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # 1️⃣ Try local pipeline -------------------------------------------------
    pipeline = get_pipeline()
    if pipeline:
        try:
            image = pipeline(prompt).images[0]
            image.save(path)
            return path
        except Exception as e:
            print(f"[ERROR] Diffusion inference failed ({e}). Trying Hugging Face API.")

    # 2 - Hugging Face Inference API ----------------------------------------
    hf_api_key = os.getenv("HF_API_KEY")
    hf_model = os.getenv("HF_DIFFUSION_MODEL", "stabilityai/stable-diffusion-3-medium-diffusers")
    if hf_api_key:
        try:
            import requests
            headers = {"Authorization": f"Bearer {hf_api_key}"}
            json_payload = {"inputs": prompt}
            api_url = f"https://router.huggingface.co/hf-inference/models/{hf_model}"
            print(f"[INFO] Calling HF Inference API: {hf_model}")
            response = requests.post(
                api_url,
                headers=headers,
                json=json_payload,
                timeout=180,
            )
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            if "image" in content_type:
                with open(path, "wb") as f:
                    f.write(response.content)
                print(f"[OK] Image saved: {path} ({len(response.content)} bytes)")
                return path
            else:
                print(f"[ERROR] HF API returned non-image: {response.text[:200]}")
        except Exception as e:
            print(f"[ERROR] Hugging Face API failed ({e}). Using fallback renderer.")

    # 3️⃣ Simple fallback renderer ------------------------------------------
    create_fallback_image(prompt, path)
    return path
