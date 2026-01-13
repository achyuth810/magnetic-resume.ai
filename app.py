# app.py
from flask import Flask, render_template, request, send_file, session
import os
import re
import tempfile

from dotenv import load_dotenv
import google.generativeai as genai

from utils.pdf_reader import extract_text_from_pdf
from utils.docx_reader import extract_text_from_docx
from utils.alignment import alignment_facts
from utils.pdf_writer import write_resume_pdf
from utils.docx_writer import write_resume_docx

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")  # change later

# Gemini
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY missing. Put it in .env as GOOGLE_API_KEY=...")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("models/gemini-flash-latest")


def extract_resume_text(file_storage):
    name = (file_storage.filename or "").lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_storage)
    if name.endswith(".docx"):
        return extract_text_from_docx(file_storage)
    raise ValueError("Unsupported file type. Upload PDF or DOCX.")


def clean_output(text: str) -> str:
    """Strong cleanup: remove markdown, tables, stray symbols."""
    if not text:
        return ""

    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)  # headings
    text = text.replace("**", "").replace("__", "").replace("`", "")
    text = re.sub(r"^\s*\|.*\|\s*$", "", text, flags=re.MULTILINE)  # remove table rows

    # bullets -> hyphen
    text = re.sub(r"^\s*[•*]\s+", "- ", text, flags=re.MULTILINE)

    # collapse extra blank lines
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def confidence_label(delta: int) -> str:
    if delta >= 12:
        return "High"
    if delta >= 5:
        return "Medium"
    return "Low"


def safe_filename(base: str) -> str:
    base = (base or "guest").strip().lower()
    base = re.sub(r"[^a-z0-9_-]+", "_", base)
    return base[:40] or "guest"


@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    before_score = after_score = delta = None
    confidence = None
    error = None

    if request.method == "POST":
        jd_text = (request.form.get("jd") or "").strip()
        resume_file = request.files.get("resume_file")

        display_name = (request.form.get("display_name") or "").strip()
        name_slug = safe_filename(display_name) if display_name else "guest"

        template = request.form.get("template", "ATS_CLASSIC")  # <-- NEW
        if template not in ("ATS_CLASSIC", "ATS_BLUE"):
            template = "ATS_CLASSIC"

        if not jd_text:
            error = "Please paste the Job Description."
        elif not resume_file or not resume_file.filename:
            error = "Please upload a PDF or DOCX resume."
        else:
            try:
                resume_text = extract_resume_text(resume_file)

                before_alignment = alignment_facts(resume_text, jd_text)
                before_score = before_alignment["score"]

                prompt = f"""
You are a resume enhancer.

STRICT RULES:
- Do NOT add fake experience
- Do NOT add new companies, tools, skills, certifications
- Do NOT change dates, titles, locations
- Output must be PLAIN TEXT ONLY (no markdown, no **, no ##, no tables)

FORMATTING RULES:
- Use ALL CAPS for section titles (SUMMARY, EXPERIENCE, EDUCATION, SKILLS, CERTIFICATIONS)
- Use hyphen (-) for bullets
- One blank line between sections

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

TASK:
Rewrite the resume to better align to the job description while staying truthful.
"""
                response = model.generate_content(prompt)
                output = clean_output(response.text or "")

                after_alignment = alignment_facts(output, jd_text)
                after_score = after_alignment["score"]

                delta = after_score - before_score
                confidence = confidence_label(delta)

                # store for download routes
                session["last_output"] = output
                session["name_slug"] = name_slug
                session["template"] = template  # <-- NEW

            except Exception as e:
                error = f"Error: {str(e)}"

    return render_template(
        "index.html",
        error=error,
        output=output,
        before_score=before_score,
        after_score=after_score,
        delta=delta,
        confidence=confidence
    )


@app.route("/download/pdf")
def download_pdf():
    text = session.get("last_output")
    if not text:
        return "Nothing to download. Run tailoring first.", 400

    name_slug = session.get("name_slug", "guest")
    template = session.get("template", "ATS_CLASSIC")

    filename = f"{name_slug}.pdf"

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.close()

    # Pass template into your writer
    write_resume_pdf(text, tmp.name, title="TAILORED RESUME", template=template)

    return send_file(tmp.name, as_attachment=True, download_name=filename)


@app.route("/download/docx")
def download_docx():
    text = session.get("last_output")
    if not text:
        return "Nothing to download. Run tailoring first.", 400

    name_slug = session.get("name_slug", "guest")
    template = session.get("template", "ATS_CLASSIC")

    filename = f"{name_slug}.docx"

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    tmp.close()

    # Pass template into your writer
    write_resume_docx(text, tmp.name, title="TAILORED RESUME", template=template)

    return send_file(tmp.name, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(debug=True)