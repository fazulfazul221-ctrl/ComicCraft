import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

AVAILABLE_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash"
]

def query_gemini(prompt: str) -> str:
    """Queries Gemini API with automatic model rotation across free-tier quota buckets."""
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key and api_key != "your_gemini_api_key_here":
        genai.configure(api_key=api_key)

    last_err = None
    for model_name in AVAILABLE_MODELS:
        try:
            m = genai.GenerativeModel(model_name)
            res = m.generate_content(prompt)
            if res and res.text:
                return res.text.strip()
        except Exception as e:
            print(f"[INFO] Model {model_name} unavailable or quota reached: {e}. Trying next...")
            last_err = e
            continue

    raise Exception(f"All Gemini models exhausted or unavailable: {last_err}")

def generate_fallback_outline(user_prompt: str) -> list:
    """Fallback 5-panel outline if all AI model quotas are exhausted."""
    return [
        {
            "panel": 1,
            "title": "A New Journey Begins",
            "scene_description": f"The story begins with our hero setting out: {user_prompt[:80]}",
            "image_prompt": f"comic book art, panel 1, {user_prompt}, dramatic lighting, highly detailed"
        },
        {
            "panel": 2,
            "title": "A Shadow on the Horizon",
            "scene_description": "An unexpected challenge or mysterious presence alters the path.",
            "image_prompt": f"comic panel, mystery, {user_prompt}, action perspective, vivid colors"
        },
        {
            "panel": 3,
            "title": "The Decisive Moment",
            "scene_description": "Courage is put to the test in a pivotal confrontation or discovery.",
            "image_prompt": f"comic panel, intense dramatic scene, {user_prompt}, cinematic framing"
        },
        {
            "panel": 4,
            "title": "Overcoming the Odds",
            "scene_description": "Determination shines through as answers begin to unfold.",
            "image_prompt": f"comic panel, triumph, {user_prompt}, dynamic energy, colorful comic art"
        },
        {
            "panel": 5,
            "title": "A Hero's Resolve",
            "scene_description": "The journey reaches a memorable, inspiring turning point.",
            "image_prompt": f"comic panel, final resolution, sunset vista, heroic stance, epic comic illustration"
        }
    ]

def generate_outline(user_prompt: str) -> list:
    """
    Generates a 5-panel comic layout based on the user's story idea using Gemini.

    Args:
        user_prompt (str): The user's comic idea prompt.

    Returns:
        list: A list of dictionaries, one for each panel.
    """
    prompt = f"""
You are a professional AI comic planner.

Your task is to generate a *strictly formatted* JSON array containing 5 panel descriptions for a comic based on the story idea below:

STORY: "{user_prompt}"

Each JSON object must include:
- "panel" (integer, 1 to 5)
- "title" (string)
- "scene_description" (string)
- "image_prompt" (string)

Respond ONLY in this valid JSON format, without any explanations or markdown:
[
  {{
    "panel": 1,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for comic illustration"
  }},
  ...
]
"""
    try:
        output_text = query_gemini(prompt)
        try:
            print("\n[RAW GEMINI RESPONSE]\n", output_text)
        except Exception:
            print("\n[RAW GEMINI RESPONSE]\n", output_text.encode('ascii', 'replace').decode('ascii'))

        # Robust JSON extraction
        clean_text = output_text
        if "```" in clean_text:
            match = re.search(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", clean_text)
            if match:
                clean_text = match.group(1).strip()
            else:
                start = clean_text.find("[")
                end = clean_text.rfind("]")
                if start != -1 and end != -1:
                    clean_text = clean_text[start:end+1]
        elif "[" in clean_text and "]" in clean_text:
            start = clean_text.find("[")
            end = clean_text.rfind("]")
            clean_text = clean_text[start:end+1]

        panel_data = json.loads(clean_text)

        # Validate structure
        if not isinstance(panel_data, list):
            raise ValueError("Gemini response is not a list.")

        for panel in panel_data:
            if not isinstance(panel, dict) or not all(key in panel for key in ("panel", "title", "scene_description", "image_prompt")):
                raise ValueError(f"Invalid panel format or missing keys: {panel}")

        return panel_data

    except Exception as e:
        print(f"[WARNING] Gemini generation failed: {e}. Falling back to structured outline.")
        return generate_fallback_outline(user_prompt)
