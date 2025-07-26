import streamlit as st
from llama_cpp import Llama
import os
import fitz  # PyMuPDF for PDF reading
import docx  # python-docx for DOCX reading

MODEL_PATH = "models/phi-1.5.Q4_K_M.gguf"

# -----------------------
# Load Model
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        st.error(f"Model not found at {MODEL_PATH}. Please download it manually.")
        return None
    return Llama(model_path=MODEL_PATH, n_ctx=2048)

llm = load_model()

# -----------------------
# Streamlit UI
st.set_page_config(page_title="Freelancer Proposal Writer", layout="centered")
st.title("📝PitchPerfect AI- The Ultimate AI Powered Freelancer Proposal Writer")

# Job description input
st.subheader("📄 Job Description")
uploaded_file = st.file_uploader("Upload Job Description (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
job_desc = ""

if uploaded_file:
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext == "pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            job_desc = "\n".join([page.get_text() for page in doc])
    elif ext == "docx":
        doc = docx.Document(uploaded_file)
        job_desc = "\n".join([p.text for p in doc.paragraphs])
    elif ext == "txt":
        job_desc = uploaded_file.read().decode("utf-8")
else:
    job_desc = st.text_area("Or Paste Job Description Below", height=200)

# Freelancer profile input
st.subheader("👤 Your Info")
name = st.text_input("Your Name", "Jane Doe")
title = st.text_input("Your Title", "AI Freelancer")
skills = st.text_area("Skills (comma-separated)", "Python, Deep Learning, Streamlit, LLMs")
experience = st.text_area("Brief Experience Summary", "I have over 3 years of experience building AI-powered applications.")

tone = st.selectbox("🗣️ Tone of Voice", ["Professional", "Friendly", "Confident", "Creative"])

# Generate button
if st.button("🚀 Generate Proposal") and llm:
    with st.spinner("Generating your proposal..."):
        prompt = f"""
Write a freelance proposal with the following information:
Job Description: {job_desc}
Name: {name}
Title: {title}
Skills: {skills}
Experience: {experience}
Tone: {tone}
Make it concise, personalized, and persuasive.
"""
        output = llm(prompt, max_tokens=512, stop=["</s>"])
        proposal = output["choices"][0]["text"].strip()

    st.subheader("📬 Generated Proposal")
    st.text_area("Your Proposal", proposal, height=300)

    st.download_button("📥 Download Proposal", proposal, file_name="proposal.txt")
