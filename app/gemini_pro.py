import os
import google.generativeai as genai
from dotenv import load_dotenv

AVAILABLE_MODELS = [
    "gemini-1.5-pro",
    "gemini-pro-latest",
    "gemini-2.5-pro",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest"
]

def query_gemini_story(prompt: str) -> str:
    """Queries Gemini API for story generation with automatic model rotation across quota buckets."""
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
                return res.text
        except Exception as e:
            print(f"[INFO] Story Model {model_name} error: {e}. Trying next...")
            last_err = e
            continue

    raise Exception(f"All Gemini models exhausted for story generation: {last_err}")

def generate_fallback_story(outline: list) -> str:
    """Fallback comic narration and dialogue if all AI model quotas are exhausted."""
    panels = []
    for item in outline:
        p_num = item.get("panel", 1)
        p_title = item.get("title", f"Panel {p_num}")
        p_desc = item.get("scene_description", "")
        panels.append(
            f"**Panel {p_num}: {p_title}**\n"
            f"{p_desc}\n"
            f"**CAPTION:** The adventure unfolds with heart and determination.\n"
            f"**NARRATION:** Step by step, the story builds towards its unforgettable conclusion."
        )
    return "\n\n".join(panels)

def generate_story(outline: list) -> str:
    """
    Generates a detailed comic story with narration and character dialogue
    from a list of comic panel outlines using Gemini.

    Args:
        outline (list): A list of dictionaries representing each comic panel's idea.

    Returns:
        str: The generated comic story text.
    """
    formatted_outline = "\n".join([
        f"Panel {item.get('panel', i+1)}: {item.get('title', '')} - {item.get('scene_description', '')}"
        for i, item in enumerate(outline)
    ])

    prompt = f"""
You're an expert comic book writer.

Given the following panel breakdown, write a comic-style story with engaging narration and character dialogues for each panel.

Panel Outline:
{formatted_outline}

Guidelines:
- Use a fun and engaging tone, like an actual comic book.
- Use explicit markers for each panel like '**Panel 1: Title**', '**CAPTION:**', '**NARRATION:**', and character dialogues.
- Keep each panel self-contained but part of a cohesive story.
"""
    try:
        return query_gemini_story(prompt)
    except Exception as e:
        print(f"[WARNING] Story generation failed: {e}. Using structured fallback narration.")
        return generate_fallback_story(outline)
