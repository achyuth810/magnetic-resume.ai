# utils/templates.py
from reportlab.lib import colors

PDF_TEMPLATES = {
    "ATS_CLASSIC": {
        "font": "Helvetica",
        "header_font": "Helvetica-Bold",
        "name_size": 18,
        "section_size": 12,
        "body_size": 10.5,
        "line_gap": 14,
        "margin_left": 54,
        "margin_right": 54,
        "margin_top": 54,
        "margin_bottom": 54,
        "section_color": colors.black,
    },
    "ATS_BLUE": {
        "font": "Helvetica",
        "header_font": "Helvetica-Bold",
        "name_size": 18,
        "section_size": 12,
        "body_size": 10.5,
        "line_gap": 14,
        "margin_left": 54,
        "margin_right": 54,
        "margin_top": 54,
        "margin_bottom": 54,
        "section_color": colors.HexColor("#0A66C2"),  # LinkedIn blue
    },
}