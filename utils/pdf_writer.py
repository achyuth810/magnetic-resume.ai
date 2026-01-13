# utils/pdf_writer.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
import re

def _wrap_line(text, font_name, font_size, max_width):
    """Wrap a single long line into multiple lines that fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if stringWidth(test, font_name, font_size) <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def _is_section_title(line: str) -> bool:
    # ALL CAPS section titles like SUMMARY, EXPERIENCE, SKILLS, EDUCATION, CERTIFICATIONS
    s = line.strip()
    return bool(s) and s == s.upper() and len(s) <= 40 and re.match(r"^[A-Z0-9 &/,-]+$", s)

def _is_bullet(line: str) -> bool:
    return line.lstrip().startswith(('-', '•', '*'))
def write_resume_pdf(text, out_path, title="TAILORED RESUME", template="ATS_CLASSIC"):
    ...

    """
    Writes ATS-friendly PDF with improved organization:
    - Larger bold name at top
    - Contact info in smaller font
    - Section titles in bold with extra spacing
    - Indented hyphen bullets with wrapping
    - Consistent line spacing and page breaks
    - Subheadings (e.g., in skills) detected and bolded if short all-caps after colon or similar
    """
    c = canvas.Canvas(out_path, pagesize=LETTER)
    width, height = LETTER

    left = 0.75 * inch
    right = 0.75 * inch
    top = 0.75 * inch
    bottom = 0.75 * inch

    usable_w = width - left - right
    y = height - top

    # Fonts and sizes
    BODY_FONT = "Times-Roman"
    BOLD_FONT = "Times-Bold"
    BODY_SIZE = 11
    NAME_SIZE = 18
    CONTACT_SIZE = 10
    SECTION_SIZE = 12
    SUBHEADING_SIZE = 11

    # Indents
    BULLET_INDENT = 0.25 * inch
    BULLET_WIDTH = stringWidth('- ', BODY_FONT, BODY_SIZE)  # Width of bullet prefix

    def new_page():
        nonlocal y
        c.showPage()
        y = height - top

    def draw_wrapped_lines(lines, font_name=BODY_FONT, font_size=BODY_SIZE, indent=0, extra_gap=0, is_bullet=False):
        nonlocal y
        line_height = font_size * 1.2
        for i, wline in enumerate(lines):
            if y - line_height < bottom:
                new_page()
            c.setFont(font_name, font_size)
            x_pos = left + indent
            if is_bullet and i == 0:
                # Draw bullet separately
                c.drawString(x_pos, y, '-')
                x_pos += BULLET_WIDTH
                wline = wline.lstrip()[2:].strip() if wline.startswith('- ') else wline  # Strip prefix if present
            c.drawString(x_pos, y, wline)
            y -= line_height
        if extra_gap:
            y -= extra_gap

    # Normalize input text
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    lines_in = text.split("\n")

    is_first_line = True
    prev_was_section = False
    in_skills = False

    for raw in lines_in:
        line = raw.rstrip()

        # Skip empty lines but add spacing
        if not line.strip():
            y -= BODY_SIZE * 0.5
            if y < bottom:
                new_page()
            continue

        # Normalize bullets to '- '
        if _is_bullet(line):
            line = '- ' + line.lstrip('•*- ').strip()

        # Name (first line, assume it's the name)
        if is_first_line:
            wrapped = _wrap_line(line, BOLD_FONT, NAME_SIZE, usable_w)
            draw_wrapped_lines(wrapped, BOLD_FONT, NAME_SIZE, extra_gap=BODY_SIZE * 0.5)
            is_first_line = False
            continue

        # Contact info (second line, assume after name)
        if '|' in line and '@' in line:  # Heuristic for contact with pipes
            wrapped = _wrap_line(line, BODY_FONT, CONTACT_SIZE, usable_w)
            draw_wrapped_lines(wrapped, BODY_FONT, CONTACT_SIZE, extra_gap=BODY_SIZE * 1.0)
            continue

        # Section title
        if _is_section_title(line):
            if 'TECHNICAL SKILLS' in line.upper():
                in_skills = True
            else:
                in_skills = False
            y -= BODY_SIZE * 0.8  # Extra space before section
            if y < bottom:
                new_page()
            wrapped = _wrap_line(line.strip(), BOLD_FONT, SECTION_SIZE, usable_w)
            draw_wrapped_lines(wrapped, BOLD_FONT, SECTION_SIZE, extra_gap=BODY_SIZE * 0.3)
            prev_was_section = True
            continue

        # Job headers (e.g., Company, Date, Role, Location) - bold if short and after section or job
        if prev_was_section or (len(line.strip()) < 50 and not _is_bullet(line) and re.search(r'\d{4}', line)):
            font = BOLD_FONT if ' - ' in line or re.match(r'^[A-Z][a-z]+ \d{4} - ', line) else BODY_FONT
            size = SUBHEADING_SIZE if font == BOLD_FONT else BODY_SIZE
            wrapped = _wrap_line(line, font, size, usable_w)
            draw_wrapped_lines(wrapped, font, size, extra_gap=BODY_SIZE * 0.2 if font == BOLD_FONT else 0)
            prev_was_section = False
            continue

        # Skills subheadings (e.g., "• Category: list" treated as bold category)
        if in_skills and ':' in line and _is_bullet(line):
            # Split into category and list
            parts = line.split(':', 1)
            if len(parts) == 2:
                category = parts[0].lstrip('- ').strip() + ':'
                list_text = parts[1].strip()
                # Draw bold category
                wrapped_cat = _wrap_line(category, BOLD_FONT, SUBHEADING_SIZE, usable_w - BULLET_INDENT)
                draw_wrapped_lines(wrapped_cat, BOLD_FONT, SUBHEADING_SIZE, indent=BULLET_INDENT, extra_gap=0)
                # Draw list as normal, wrapped
                wrapped_list = _wrap_line(list_text, BODY_FONT, BODY_SIZE, usable_w - BULLET_INDENT * 2)
                draw_wrapped_lines(wrapped_list, BODY_FONT, BODY_SIZE, indent=BULLET_INDENT * 2, extra_gap=BODY_SIZE * 0.3)
                continue

        # Regular bullets with indent
        if _is_bullet(line):
            max_w = usable_w - BULLET_INDENT - BULLET_WIDTH
            wrapped = _wrap_line(line, BODY_FONT, BODY_SIZE, max_w)
            draw_wrapped_lines(wrapped, BODY_FONT, BODY_SIZE, indent=BULLET_INDENT, is_bullet=True, extra_gap=BODY_SIZE * 0.1)
            prev_was_section = False
            continue

        # Default: paragraphs or other lines, wrapped
        wrapped = _wrap_line(line, BODY_FONT, BODY_SIZE, usable_w)
        draw_wrapped_lines(wrapped, BODY_FONT, BODY_SIZE, extra_gap=BODY_SIZE * 0.2)
        prev_was_section = False

    c.save()