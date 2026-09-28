def build_comic_layout(image_paths, full_story, outline):
    """
    This function organizes the generated images and full comic story into a structured layout.
    It matches each image with its corresponding panel story.
    The output is a list of dictionaries containing the panel number, title, image path, text, and scene description.
    """
    # Split the full story into individual panel segments
    if "**Panel" in full_story:
        story_panels = full_story.split("**Panel")
        story_panels = [f"**Panel{panel}" for panel in story_panels if panel.strip()]
    elif "Panel " in full_story:
        story_panels = full_story.split("Panel ")
        story_panels = [f"Panel {panel}" for panel in story_panels if panel.strip()]
    else:
        # Fallback split by double newlines or repeat
        paras = [p for p in full_story.split("\n\n") if p.strip()]
        story_panels = paras if len(paras) >= len(outline) else [full_story] * len(outline)

    # Ensure story_panels length matches outline
    while len(story_panels) < len(outline):
        story_panels.append(f"**Panel {len(story_panels)+1}**\n{full_story}")

    # Build layout panel by panel
    layout = []
    for idx, (image, text, panel_info) in enumerate(zip(image_paths, story_panels, outline), start=1):
        lines = text.strip().splitlines()
        cleaned_text = "\n".join(lines[1:]).strip() if len(lines) > 1 else text.strip()

        layout.append({
            "panel": idx,
            "title": panel_info.get("title", f"Panel {idx}"),
            "image_path": image,
            "text": cleaned_text,  # remove panel title line
            "scene_description": panel_info.get("scene_description", ""),
            "image_prompt": panel_info.get("image_prompt", "")
        })

    return layout
