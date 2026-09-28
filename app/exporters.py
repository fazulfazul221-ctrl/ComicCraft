import os
from datetime import datetime
from fpdf import FPDF

FONT_PATH = "static/fonts/DejaVuSans.ttf"
EXPORT_FOLDER = "static/exports"

class PDF(FPDF):
    pass

def save_pdf(layout: list) -> str:
    """
    This function compiles the full comic into a multi-page PDF file using the FPDF library.
    Each panel’s image and narration are placed neatly on separate pages.
    The final PDF file is saved into the static/exports folder, and the path is returned.
    """
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    font_family = 'Helvetica'
    # Add Unicode font if available
    if os.path.exists(FONT_PATH):
        try:
            pdf.add_font('DejaVu', '', FONT_PATH, uni=True)
            font_family = 'DejaVu'
        except TypeError:
            try:
                pdf.add_font('DejaVu', '', FONT_PATH)
                font_family = 'DejaVu'
            except Exception as e:
                print(f"Warning loading font DejaVu: {e}")
        except Exception as e:
            print(f"Warning loading font DejaVu: {e}")

    pdf.set_font(font_family, '', 12)

    for panel in layout:
        image_path = panel.get('image_path', '')
        story_text = panel.get('text', '')
        panel_num = panel.get('panel', 1)
        panel_title = panel.get('title', f"Panel {panel_num}")

        pdf.add_page()

        # Panel title (no bold)
        pdf.set_font(font_family, '', 14)
        pdf.cell(0, 10, f"Panel {panel_num}: {panel_title}", ln=True, align="C")
        pdf.set_font(font_family, '', 12)

        # Image placement
        y_image = 30
        image_height = 100
        spacing_after_image = 15

        if os.path.exists(image_path):
            pdf.image(image_path, x=10, y=y_image, w=pdf.w - 20, h=image_height)
        else:
            pdf.set_y(y_image)
            pdf.multi_cell(0, 10, f"Image missing: {image_path}")

        # Text placement below image
        pdf.set_y(y_image + image_height + spacing_after_image)
        story_lines = story_text.strip().splitlines()
        # Remove title line like "**Panel 1: Title**" if present
        if story_lines and story_lines[0].strip().lower().startswith("**panel"):
            story_lines = story_lines[1:]
        cleaned_text = "\n".join(story_lines).strip()
        
        # Clean special unicode characters if using default latin-1 Helvetica
        if font_family == 'Helvetica':
            cleaned_text = cleaned_text.encode('latin-1', 'replace').decode('latin-1')

        pdf.multi_cell(0, 8, cleaned_text)

    # Save with timestamp
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    pdf_path = os.path.join(EXPORT_FOLDER, filename)
    pdf.output(pdf_path)

    return pdf_path
