import os
import traceback
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class PromptRequest(BaseModel):
    prompt: str
    character_name: str
    setting: str
    tone: str
    style: str

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Loads the homepage (index.html) where users can submit their story details."""
    return templates.TemplateResponse(request=request, name="index.html", context={})

@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...)
):
    """
    Handles form submission, processes the input using AI, generates the comic panels,
    and returns the comic preview page.
    """
    try:
        # Combine user input into a single full prompt
        full_prompt = (
            f"{prompt}\n"
            f"The main character is {character_name}. "
            f"The setting is a {setting}. "
            f"The tone is {tone}. The art style is {style}."
        )

        # Step 1: Generate panel outline
        outline = generate_outline(full_prompt)

        if not isinstance(outline, list) or not all("image_prompt" in panel for panel in outline):
            raise ValueError(f"Invalid outline structure from Gemini response: {outline}")

        # Step 2: Generate story
        full_story = generate_story(outline)

        # Step 3: Generate images
        images = [generate_image(panel["image_prompt"]) for panel in outline]

        # Step 4: Build Layout
        layout = build_comic_layout(images, full_story, outline)

        # Step 5: Export to PDF
        pdf_path = save_pdf(layout)
        web_pdf_path = "/" + pdf_path.replace("\\", "/")  # Make path safe for web

        # Ensure image paths are web-accessible
        for panel in layout:
            if not panel["image_path"].startswith("/"):
                panel["image_path"] = "/" + panel["image_path"].replace("\\", "/")

        return templates.TemplateResponse(request=request, name="comic_preview.html", context={
            "layout": layout,
            "pdf_path": web_pdf_path
        })

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str = ""):
    """Displays a success confirmation page after the comic is downloaded."""
    return templates.TemplateResponse(request=request, name="export_success.html", context={
        "pdf_path": pdf_path
    })

@router.post("/generate-comic/json")
async def generate_comic_json(req: PromptRequest):
    """
    An API route that accepts JSON payloads, triggers comic generation,
    and returns comic layout data and the generated PDF path.
    """
    try:
        full_prompt = (
            f"{req.prompt}\n"
            f"The main character is {req.character_name}. "
            f"The setting is a {req.setting}. "
            f"The tone is {req.tone}. The art style is {req.style}."
        )

        # Step 1: Generate panel outline
        outline = generate_outline(full_prompt)

        if not isinstance(outline, list) or not all("image_prompt" in panel for panel in outline):
            raise ValueError(f"Invalid outline structure from Gemini response: {outline}")

        # Step 2: Generate story
        full_story = generate_story(outline)

        # Step 3: Generate images
        images = [generate_image(panel["image_prompt"]) for panel in outline]

        # Step 4: Build Layout
        layout = build_comic_layout(images, full_story, outline)

        # Step 5: Export to PDF
        pdf_path = save_pdf(layout)
        web_pdf_path = "/" + pdf_path.replace("\\", "/")

        # Format image paths for web
        for panel in layout:
            if not panel["image_path"].startswith("/"):
                panel["image_path"] = "/" + panel["image_path"].replace("\\", "/")

        return {
            "message": "Comic generated successfully",
            "layout": layout,
            "pdf_path": web_pdf_path
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-image")
async def test_image(prompt: str = "A futuristic city at sunset, sci-fi, cinematic, artstation"):
    """A developer utility route to test image generation from a direct prompt."""
    try:
        image_path = generate_image(prompt)
        web_image_path = "/" + image_path.replace("\\", "/")
        return {"message": "Image generated successfully", "path": web_image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
