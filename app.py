import streamlit as st
from google import genai
from pypdf import PdfReader
from dotenv import load_dotenv
import os


# =========================
# CONFIGURATION
# =========================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="HireLens | AI Resume Analyzer",
    page_icon="🎯",
    layout="wide"
)


# =========================
# GEMINI CLIENT
# =========================

client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)


# =========================
# CUSTOM DESIGN
# =========================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0f172a, #172554);
}

.hero {
    text-align: center;
    padding: 30px 10px 20px 10px;
}

.hero h1 {
    font-size: 52px;
    font-weight: 800;
    color: white;
    margin-bottom: 5px;
}

.hero p {
    color: #cbd5e1;
    font-size: 19px;
}

.section {
    background: rgba(255,255,255,0.06);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.1);
}

</style>
""", unsafe_allow_html=True)


# =========================
# HEADER
# =========================

st.markdown("""
<div class="hero">

<h1>🎯 HireLens</h1>

<p>
AI-Powered Resume & Job Match Analyzer
</p>

</div>
""", unsafe_allow_html=True)


# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.header("⚙️ How HireLens Works")

    st.markdown("""
    **1️⃣ Upload Resume**

    Upload your resume as a PDF.

    **2️⃣ Add Job Description**

    Paste the job description you're targeting.

    **3️⃣ Analyze**

    HireLens uses AI to evaluate the match.

    **4️⃣ Improve**

    Get personalized suggestions for your resume.
    """)

    st.divider()

    st.caption(
        "HireLens • AI Career Assistant"
    )


# =========================
# API STATUS
# =========================

if not API_KEY:

    st.error(
        "⚠️ Gemini API key not detected. "
        "Please check your .env file."
    )

else:

    st.success(
        "🟢 AI Engine Connected"
    )


# =========================
# INPUT AREA
# =========================

left, right = st.columns(2)


with left:

    st.subheader("📄 Upload Resume")

    resume_file = st.file_uploader(
        "Upload your resume PDF",
        type=["pdf"]
    )


with right:

    st.subheader("💼 Job Description")

    job_description = st.text_area(
        "Paste the job description",
        height=250,
        placeholder=(
            "Example: We are looking for a "
            "Software Engineer with Python, "
            "SQL, Git and cloud experience..."
        )
    )


# =========================
# RESUME EXTRACTION
# =========================

resume_text = ""


if resume_file:

    try:

        reader = PdfReader(resume_file)

        for page in reader.pages:

            extracted = page.extract_text()

            if extracted:
                resume_text += extracted

        st.success(
            "✅ Resume uploaded successfully!"
        )

    except Exception as error:

        st.error(
            f"Could not read the PDF: {error}"
        )


# =========================
# ANALYSIS
# =========================

st.divider()


if st.button(
    "🚀 Analyze Resume",
    type="primary",
    use_container_width=True
):

    if not resume_file:

        st.warning(
            "Please upload a resume first."
        )

    elif not job_description.strip():

        st.warning(
            "Please paste a job description."
        )

    elif not client:

        st.error(
            "Gemini AI is not connected."
        )

    else:

        with st.spinner(
            "🧠 HireLens is analyzing your resume..."
        ):

            try:

                prompt = f"""
You are an expert technical recruiter and
AI-powered resume analyst.

Analyze this resume against the provided
job description.

====================
RESUME
====================

{resume_text}

====================
JOB DESCRIPTION
====================

{job_description}

====================
REQUIRED OUTPUT
====================

Give the analysis in the following format:

MATCH SCORE
Give an estimated percentage from 0 to 100.

MATCH SUMMARY
Explain the overall compatibility in 3-4 sentences.

DETECTED SKILLS
List the technical and professional skills
found in the resume.

MISSING SKILLS
List important skills from the job description
that are missing or weak in the resume.

IMPORTANT KEYWORDS
List 8-12 relevant keywords that could improve
the resume's alignment with the job.

RESUME IMPROVEMENTS
Give 5 specific improvements.

PROJECT SUGGESTIONS
Suggest 2 practical projects that would strengthen
the candidate's profile for this role.

FINAL ADVICE
Give a short actionable conclusion.
"""

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )

                result = response.text

                st.success(
                    "🎉 Resume analysis completed!"
                )

                st.divider()

                st.subheader(
                    "📊 HireLens AI Analysis"
                )

                import re

                score_match = re.search(r"MATCH SCORE\s*.*?(\d{1,3})%", result, re.IGNORECASE)

                if score_match:
                    score = int(score_match.group(1))

                    st.markdown("### 🎯 Resume–Job Match")

                    col1, col2 = st.columns([1, 3])

                    with col1:
                        st.metric(
            label="Match Score",
            value=f"{score}%"
        )

                    with col2:
                        st.progress(
            min(score, 100) / 100
        )

                    st.divider()

                st.markdown(result)

            except Exception as error:

                st.error(
                    f"AI analysis failed: {error}"
                )


# =========================
# FOOTER
# =========================

st.divider()

st.caption(
    "HireLens — AI-powered resume intelligence "
    "for smarter career preparation."
)
