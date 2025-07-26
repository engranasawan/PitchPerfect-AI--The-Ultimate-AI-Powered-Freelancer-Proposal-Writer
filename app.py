import os
import streamlit as st
import requests
import fitz  # PyMuPDF for PDF parsing
import docx  # For DOCX parsing

# === CONFIG ===
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
HF_TOKEN = st.secrets.get("HF_TOKEN", os.getenv("HF_TOKEN"))
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# === HELPER FUNCTIONS ===
def query_hf_model(prompt: str):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 300, "temperature": 0.7}
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        json_data = response.json()
        if isinstance(json_data, list) and "generated_text" in json_data[0]:
            return json_data[0]["generated_text"]
        elif isinstance(json_data, dict) and "error" in json_data:
            return f"API Error: {json_data['error']}"
        return str(json_data)
    except requests.exceptions.RequestException as e:
        st.error("⚠️ API Request failed.")
        st.exception(e)
        return ""
    except requests.exceptions.JSONDecodeError:
        st.error("⚠️ Invalid JSON response from Hugging Face.")
        return ""

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
    else:
        return ""

# === STREAMLIT UI ===
st.set_page_config(page_title="PitchPerfect AI", layout="centered")
st.title("📝 PitchPerfect AI – Ultimate Proposal Writer for Freelancers")

# --- Job Description Input ---
st.subheader("📄 Job Description")
uploaded_file = st.file_uploader("Upload a job description file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
job_desc = extract_text_from_file(uploaded_file) if uploaded_file else ""
job_desc = st.text_area("Or paste the job description here", value=job_desc, height=200, help="This will be used to tailor your proposal.")

# --- Freelancer Info ---
st.subheader("👤 Your Profile")
name = st.text_input("Your Name", "Jane Doe")
title = st.text_input("Professional Title", "AI/ML Engineer")
skills = st.text_area("Key Skills (comma-separated)", "Python, Deep Learning, NLP, Streamlit")
experience = st.text_area("Brief Experience Summary", "I have 3+ years of experience delivering production-ready AI systems.")
tone = st.selectbox("🎯 Tone of Proposal", ["Professional", "Friendly", "Confident", "Creative"])

# --- Generate Proposal ---
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

        if proposal:
            st.subheader("📬 Your Proposal")
            st.text_area("Proposal", proposal, height=300)
            st.download_button("📥 Download Proposal", proposal, file_name="freelance_proposal.txt")
