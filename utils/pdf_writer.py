# utils/pdf_writer.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from utils.templates import get_template


def write_resume_pdf(text: str, output_path: str, title: str = "TAILORED RESUME", template: str = "ATS_CLASSIC"):
    config = get_template(template)
    styles = config["styles"]

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=config["left_margin"],
        rightMargin=config["right_margin"],
        topMargin=config["top_margin"],
        bottomMargin=config["bottom_margin"]
    )

    story = []

    # Split text into sections (assuming Gemini outputs in ALL CAPS sections)
    sections = text.split("\n\n")
    
    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue

        lines = section.split("\n")
        header = lines[0].strip()

        # Section Header
        if header.isupper() and len(header) > 3:  # e.g., EXPERIENCE, SKILLS
            story.append(Paragraph(header, styles["SectionHeader"]))
            story.append(Spacer(1, config["section_spacing"] - 8))
            
            # Body content (bullets or paragraphs)
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("- ") or line.startswith("• "):
                    clean_line = line[2:].strip()
                    story.append(Paragraph(clean_line, styles["Bullet"]))
                elif line:
                    story.append(Paragraph(line, styles["Body"]))
            
            story.append(Spacer(1, config["section_spacing"]))

        # Name (first line of whole resume)
        elif i == 0 and not header.isupper():
            story.append(Paragraph(header.upper(), styles["Name"]))
            story.append(Spacer(1, 12))

        # Contact line (usually second line)
        elif i == 1 and "@" in header or any(char.isdigit() for char in header):
            story.append(Paragraph(header, styles["Contact"]))
            story.append(Spacer(1, 28))

        # Normal paragraphs / bullets
        else:
            for line in lines:
                line = line.strip()
                if line.startswith("- ") or line.startswith("• "):
                    clean_line = line[2:].strip()
                    story.append(Paragraph(clean_line, styles["Bullet"]))
                elif line:
                    story.append(Paragraph(line, styles["Body"]))

    doc.build(story)