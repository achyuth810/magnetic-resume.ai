from docx import Document

def extract_text_from_docx(file_storage) -> str:
    """
    Extract plain text from a .docx FileStorage object (Flask upload).
    """
    doc = Document(file_storage)
    lines = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
    return "\n".join(lines)