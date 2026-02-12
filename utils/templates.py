# utils/templates.py
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

def get_all_templates():
    base_styles = getSampleStyleSheet()

    BASE = {
        "font_name": "Helvetica",
        "bold_font": "Helvetica-Bold",
        "name_font_size": 22,
        "header_font_size": 13,
        "body_font_size": 10.5,
        "small_font_size": 9.5,
        "line_spacing": 13.8,           # leading
        "section_spacing": 22,
        "item_spacing": 7,
        "left_margin": 60,
        "right_margin": 60,
        "top_margin": 60,
        "bottom_margin": 60,
        "name_alignment": TA_CENTER,
        "contact_alignment": TA_CENTER,
        "section_color": colors.black,
        "accent_color": colors.black,
        "text_color": colors.black,
        "bullet_char": "•",
        "bullet_indent": 18,
        "date_alignment": TA_RIGHT,
        "max_line_length": 85,          # helps alignment.py with text wrapping
    }

    templates = {
        "ATS_CLASSIC": {
            **BASE,
            "display_name": "ATS Classic",
            "section_color": colors.black,
            "accent_color": colors.black,
        },

        "ATS_BLUE": {
            **BASE,
            "display_name": "ATS Blue",
            "section_color": colors.HexColor("#0A66C2"),   # LinkedIn blue - safe for most ATS
            "accent_color": colors.HexColor("#0A66C2"),
        },

        "ATS_MINIMAL": {
            **BASE,
            "display_name": "ATS Minimal",
            "name_font_size": 20,
            "header_font_size": 12,
            "body_font_size": 10,
            "section_spacing": 18,
            "accent_color": colors.black,
        },

        "ATS_MODERN": {
            **BASE,
            "display_name": "ATS Modern",
            "name_font_size": 24,
            "header_font_size": 13.5,
            "section_color": colors.HexColor("#1E3A8A"),
            "accent_color": colors.HexColor("#1E3A8A"),
            "bullet_char": "➤",
        },
    }

    # Add pre-built ParagraphStyles for easy use in your PDF writer
    for name, config in templates.items():
        styles = {}
        
        styles["Name"] = ParagraphStyle(
            "Name",
            parent=base_styles["Normal"],
            fontName=config["bold_font"],
            fontSize=config["name_font_size"],
            leading=config["name_font_size"] + 6,
            alignment=config["name_alignment"],
            spaceAfter=10,
        )

        styles["Contact"] = ParagraphStyle(
            "Contact",
            parent=base_styles["Normal"],
            fontName=config["font_name"],
            fontSize=config["small_font_size"] + 0.5,
            alignment=config["contact_alignment"],
            spaceAfter=22,
        )

        styles["SectionHeader"] = ParagraphStyle(
            "SectionHeader",
            parent=base_styles["Normal"],
            fontName=config["bold_font"],
            fontSize=config["header_font_size"],
            textColor=config["section_color"],
            spaceAfter=12,
            leading=16,
        )

        styles["Body"] = ParagraphStyle(
            "Body",
            parent=base_styles["Normal"],
            fontName=config["font_name"],
            fontSize=config["body_font_size"],
            leading=config["line_spacing"],
            spaceAfter=config["item_spacing"],
            alignment=TA_LEFT,
        )

        styles["Bullet"] = ParagraphStyle(
            "Bullet",
            parent=base_styles["Normal"],
            fontName=config["font_name"],
            fontSize=config["body_font_size"],
            leftIndent=config["bullet_indent"],
            bulletText=config["bullet_char"] + " ",
            leading=config["line_spacing"],
            spaceAfter=config["item_spacing"],
        )

        styles["Date"] = ParagraphStyle(
            "Date",
            parent=base_styles["Normal"],
            fontName=config["font_name"],
            fontSize=config["small_font_size"],
            alignment=config["date_alignment"],
        )

        config["styles"] = styles

    return templates


# For easy import
PDF_TEMPLATES = get_all_templates()


def get_template(template_name="ATS_CLASSIC"):
    """Helper function your alignment.py and PDF writer can use"""
    return PDF_TEMPLATES.get(template_name, PDF_TEMPLATES["ATS_CLASSIC"])