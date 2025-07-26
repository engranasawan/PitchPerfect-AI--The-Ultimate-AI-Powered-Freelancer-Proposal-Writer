import streamlit as st
import requests
import fitz  # PyMuPDF
import docx
import os

# === Hugging Face API Setup ===
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}", "Content-Type": "application/json"}

def query_hf_model(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 300, "temperature": 0.7}
    }
    response = requests.post(API_URL, headers=headers, json=payload)

    try:
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list):
            return result[0].get("generated_text", "❌ No proposal generated.")
        elif isinstance(result, dict) and "error" in result:
            st.error(f"❌ Hugging Face Error: {result['error']}")
            return ""
        return result
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        st.code(response.text, language="text")
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
    return ""

# === Streamlit UI ===
st.set_page_config(page_title="Freelancer Proposal Writer", layout="centered")
st.title("📝 PitchPerfect AI — Ultimate Proposal Writer for Freelancers")

# --- Job Description Input ---
st.subheader("📄 Job Description")
uploaded_file = st.file_uploader("Upload a job description file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
job_desc = extract_text_from_file(uploaded_file) if uploaded_file else ""

job_desc = st.text_area("Or paste the job description here", value=job_desc, height=200)

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
You are a highly experienced freelance proposal writer.

Write a compelling freelance proposal in a {tone.lower()} tone for the following job:

Job Description:
{job_desc}

Freelancer Profile:
Name: {name}
Title: {title}
Skills: {skills}
Experience: {experience}

Make it persuasive, clear, and tailored to the client’s needs.
"""
            proposal = query_hf_model(prompt)

        if proposal:
            st.subheader("📬 Your Proposal")
            st.text_area("Proposal", proposal, height=300)
            st.download_button("📥 Download Proposal", proposal, file_name="freelance_proposal.txt")
