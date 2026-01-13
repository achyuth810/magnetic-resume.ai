import re

SECTION_TITLES = [
    "PROFILE",
    "PROFESSIONAL EXPERIENCE",
    "EDUCATION",
    "PROJECTS",
    "TECHNICAL SKILLS",
    "CERTIFICATIONS"
]

def clean_resume_output(text: str) -> str:
    if not text:
        return text

    # 1. Remove markdown artifacts completely
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"-{3,}", "", text)

    # 2. Normalize bullets
    text = re.sub(r"^\s*[\*\-\u2022]\s+", "• ", text, flags=re.MULTILINE)

    # 3. Fix glued dates/locations (USANov → USA | Nov)
    text = re.sub(
        r"([A-Za-z])([A-Z][a-z]{2}\s\d{4})",
        r"\1 | \2",
        text
    )

    # 4. Force clean section headers
    for section in SECTION_TITLES:
        text = re.sub(
            rf"\b{section}\b",
            f"\n\n{section}\n",
            text,
            flags=re.IGNORECASE
        )

    # 5. Collapse excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 6. Trim trailing spaces
    text = "\n".join(line.rstrip() for line in text.splitlines())

    return text.strip()