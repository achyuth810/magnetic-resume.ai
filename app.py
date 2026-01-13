from flask import Flask, render_template, request
import os
import google.generativeai as genai
from dotenv import load_dotenv
from utils.formatter import clean_resume_output

from utils.pdf_reader import extract_text_from_pdf
from utils.docx_reader import extract_text_from_docx
from utils.alignment import alignment_facts

#-------------------------------
# LOAD ENV FIRST
#--------------------------------
load_dotenv()



# --------------------------------
# CONFIGURE GEMINI
# --------------------------------
genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY")
    
)

model = genai.GenerativeModel("models/gemini-flash-latest")


# --------------------------------
# FLASK APP
# --------------------------------
app = Flask(__name__)

def extract_resume_text(file_storage):
    filename = (file_storage.filename or "").lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_storage)

    if filename.endswith(".docx"):
        return extract_text_from_docx(file_storage)

    raise ValueError("Unsupported file type. Upload a PDF or DOCX.")

@app.route("/", methods=["GET", "POST"])
def index():
    output = None

    before_score = None
    after_score = None
    delta = None
    confidence = None

    if request.method == "POST":
        jd_text = request.form.get("jd")
        resume_file = request.files.get("resume_file")

        if not resume_file or resume_file.filename == "":
            output = "❌ No resume file uploaded. Please upload a PDF, Docx File."
        else:
            try:
                # 1️⃣ Extract resume text
                resume_text = extract_resume_text(resume_file)

                # 2️⃣ BEFORE alignment (original resume)
                before_alignment = alignment_facts(resume_text, jd_text)
                before_score = before_alignment["score"]

                # 3️⃣ Gemini tailoring
                prompt = f"""
You are an ATS-alignment resume enhancer.

STRICT RULES:
- DO NOT add fake experience
- DO NOT add new companies, tools, or skills
- DO NOT change dates, titles, or locations
- DO NOT use markdown formatting
- DO NOT use **, ##, *, or _
- Output must be plain text only

FORMATTING RULES:
- Use ALL CAPS for section titles
- Use hyphen (-) for bullet points
- One blank line between sections

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

TASK:
Rewrite the resume so it aligns better with the job description.
"""

                response = model.generate_content(prompt)
                output = response.text

                # 4️⃣ AFTER alignment (tailored resume)
                after_alignment = alignment_facts(output, jd_text)
                after_score = after_alignment["score"]

                # 5️⃣ Delta improvement
                delta = after_score - before_score

                # 6️⃣ Confidence band
                if after_score >= 85:
                    confidence = "High"
                elif after_score >= 70:
                    confidence = "Medium"
                else:
                    confidence = "Low"

            except Exception as e:
                output = f"❌ Error processing resume: {str(e)}"

    return render_template(
        "index.html",
        output=output,
        before_score=before_score,
        after_score=after_score,
        delta=delta,
        confidence=confidence
    )


if __name__ == "__main__":
    app.run(debug=True)