# utils/docx_writer.py
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import re

def _is_section_title(line: str) -> bool:
    s = line.strip()
    return bool(s) and s == s.upper() and len(s) <= 40 and re.match(r"^[A-Z0-9 &/,-]+$", s)

def _is_bullet(line: str) -> bool:
    return line.lstrip().startswith(('-', '•', '*'))

def write_resume_docx(text, out_path, title="TAILORED RESUME", template="ATS_CLASSIC"):
    ...
    """
    Writes ATS-friendly DOCX with improved organization:
    - Larger bold name at top
    - Contact info in smaller font, centered or left-aligned
    - Section titles in bold with extra spacing
    - Bolded job/role subheadings
    - Indented hyphen bullets (no list style to keep ATS-safe)
    - Skills categories bolded if with colon
    - Consistent spacing
    """
    doc = Document()

    # Set default style
    default_style = doc.styles['Normal']
    default_style.font.name = 'Calibri'
    default_style.font.size = Pt(11)

    # Margins (0.75 inches)
    section = doc.sections[0]
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)

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
            doc.add_paragraph("")  # Adds a blank paragraph for spacing
            continue

        # Normalize bullets to '- '
        if _is_bullet(line):
            line = '- ' + line.lstrip('•*- ').strip()

        # Name (first line, assume it's the name)
        if is_first_line:
            p = doc.add_paragraph()
            p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT  # Or CENTER if preferred
            r = p.add_run(line.strip())
            r.bold = True
            r.font.size = Pt(18)
            is_first_line = False
            continue

        # Contact info (second line, assume after name with pipes and email)
        if '|' in line and '@' in line:
            p = doc.add_paragraph()
            p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT  # Or CENTER
            r = p.add_run(line.strip())
            r.font.size = Pt(10)
            continue

        # Section title
        if _is_section_title(line):
            if 'TECHNICAL SKILLS' in line.upper():
                in_skills = True
            else:
                in_skills = False
            p = doc.add_paragraph("")  # Extra space before section
            p = doc.add_paragraph()
            r = p.add_run(line.strip())
            r.bold = True
            r.font.size = Pt(12)
            prev_was_section = True
            continue

        # Job subheadings (e.g., Company, Date, Role, Location) - bold if short and contains dates
        if prev_was_section or (len(line.strip()) < 50 and not _is_bullet(line) and re.search(r'\d{4}', line)):
            font_bold = True if ' - ' in line or re.match(r'^[A-Z][a-z]+ \d{4} - ', line) else False
            size = Pt(11) if font_bold else Pt(11)
            p = doc.add_paragraph()
            r = p.add_run(line.strip())
            if font_bold:
                r.bold = True
            r.font.size = size
            prev_was_section = False
            continue

        # Skills subheadings (e.g., "• Category: list" - bold category, then list)
        if in_skills and ':' in line and _is_bullet(line):
            # Split into category and list
            parts = line.split(':', 1)
            if len(parts) == 2:
                category = parts[0].lstrip('- ').strip() + ':'
                list_text = parts[1].strip()
                # Bold category
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.25)  # Indent like bullet
                r = p.add_run(category)
                r.bold = True
                r.font.size = Pt(11)
                # Add list text in same paragraph or next
                r = p.add_run(' ' + list_text)
                r.bold = False
                r.font.size = Pt(11)
                continue

        # Bullets with indent (manual, no actual list for ATS)
        if _is_bullet(line):
            content = line.lstrip('- ').strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.first_line_indent = Inches(-0.25)  # Hanging indent for bullet
            r = p.add_run('- ' + content)
            r.font.size = Pt(11)
            prev_was_section = False
            continue

        # Default: regular paragraph
        p = doc.add_paragraph()
        r = p.add_run(line.strip())
        r.font.size = Pt(11)
        prev_was_section = False

    doc.save(out_path)