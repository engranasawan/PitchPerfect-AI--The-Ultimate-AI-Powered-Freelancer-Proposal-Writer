import streamlit as st
import requests
import fitz  # PyMuPDF for PDF
import docx  # for DOCX

# === Hugging Face API Setup ===
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}

def query_hf_model(prompt):
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        result = response.json()
        if isinstance(result, list) and 'generated_text' in result[0]:
            return result[0]['generated_text']
        elif isinstance(result, dict) and "error" in result:
            return f"⚠️ Error from model: {result['error']}"
        else:
            return "⚠️ Unexpected response format."
    except Exception as e:
        return f"❌ Request failed: {str(e)}"

def extract_text_from_file(uploaded_file):
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext == "pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            return "\n".join([page.get_text() for page in doc])
    elif ext == "docx":
        doc = docx.Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif ext == "txt":
        return uploaded_file.read().decode("utf-8")
    return ""

# === Streamlit UI ===
st.set_page_config(page_title="Freelancer Proposal Writer", layout="centered")
st.title("📝 PitchPerfect AI-The Ultimate AI Powered Proposal Writer for Freelancers")

# --- Job Description Input ---
st.subheader("📄 Job Description")
uploaded_file = st.file_uploader("Upload a job description file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
job_desc = ""

if uploaded_file:
    job_desc = extract_text_from_file(uploaded_file)

job_desc = st.text_area("Or paste the job description here", value=job_desc, height=200, help="This will be used to tailor your proposal.")

# --- Freelancer Info ---
st.subheader("👤 Your Profile")
name = st.text_input("Your Name", "Jane Doe")
title = st.text_input("Professional Title", "AI/ML Engineer")
skills = st.text_area("Key Skills (comma-separated)", "Python, Deep Learning, NLP, Streamlit")
experience = st.text_area("Brief Experience Summary", "I have 3+ years of experience delivering production-ready AI systems.")

tone = st.selectbox("🎯 Tone of Proposal", ["Professional", "Friendly", "Confident", "Creative"])

# --- Generate Button ---
if st.button("🚀 Generate Proposal"):
    if not job_desc.strip():
        st.warning("Please provide a job description.")
    else:
        with st.spinner("Generating proposal..."):
            prompt = f"""
Write a freelance proposal for the following job post:

Job Description:
{job_desc}

Freelancer Details:
Name: {name}
Title: {title}
Skills: {skills}
Experience: {experience}
Tone: {tone}

Make it persuasive, clear, and aligned with the tone.
"""
            proposal = query_hf_model(prompt)

        st.subheader("📬 Your Proposal")
        st.text_area("Proposal", proposal, height=300)
        st.download_button("📥 Download Proposal", proposal, file_name="freelance_proposal.txt")
