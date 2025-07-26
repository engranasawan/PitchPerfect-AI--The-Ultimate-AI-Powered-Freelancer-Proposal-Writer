import streamlit as st
import requests
import fitz  # PyMuPDF
import docx
import os
import re

# === Hugging Face API Setup ===
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-11B-Vision-Instruct"
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}", "Content-Type": "application/json"}

def query_hf_model(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 500, "temperature": 0.7, "top_p": 0.9}
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and result[0].get("generated_text"):
            return result[0]["generated_text"].strip()
        elif isinstance(result, dict) and "error" in result:
            st.error(f"❌ Hugging Face Error: {result['error']}")
            return ""
        return ""
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        st.code(response.text, language="text")
        return ""

def extract_text_from_file(uploaded_file):
    try:
        ext = uploaded_file.name.split(".")[-1].lower()
        if ext == "pdf":
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                return "\n".join([page.get_text() for page in doc])
        elif ext == "docx":
            doc = docx.Document(uploaded_file)
            return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        elif ext == "txt":
            return uploaded_file.read().decode("utf-8")
        return ""
    except Exception as e:
        st.error(f"❌ File Processing Error: {e}")
        return ""

def match_skills(job_desc, freelancer_skills):
    job_keywords = re.findall(r'\b\w+\b', job_desc.lower())
    freelancer_skills_list = [skill.strip().lower() for skill in freelancer_skills.split(",")]
    matched_skills = [skill for skill in freelancer_skills_list if skill in job_keywords]
    return matched_skills if matched_skills else freelancer_skills_list

# === Streamlit UI ===
st.set_page_config(page_title="Freelancer Proposal Writer", layout="wide")
st.title("📝 PitchPerfect AI — Ultimate Proposal Writer for Freelancers")
st.markdown("Generate compelling, tailored freelance proposals to win your dream projects!")

# --- Job Description Input ---
st.subheader("📄 Job Description")
uploaded_file = st.file_uploader("Upload a job description file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
job_desc = extract_text_from_file(uploaded_file) if uploaded_file else ""
job_desc = st.text_area("Or paste the job description here", value=job_desc, height=250, placeholder="Paste the full job description...")

# --- Freelancer Info ---
st.subheader("👤 Your Profile")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Your Name", "Jane Doe")
    title = st.text_input("Professional Title", "AI/ML Engineer")
with col2:
    skills = st.text_area("Key Skills (comma-separated)", "Python, Deep Learning, NLP, Streamlit, TensorFlow, PyTorch")
    experience = st.text_area("Brief Experience Summary", "I have 3+ years of experience delivering production-ready AI systems.")

tone = st.selectbox("🎯 Tone of Proposal", ["Professional", "Confident", "Friendly", "Creative"], help="Choose the tone that best matches your style and the client's expectations.")

# --- Generate Button ---
if st.button("🚀 Generate Proposal", type="primary"):
    if not job_desc.strip():
        st.warning("Please provide a job description.")
    elif not name.strip() or not title.strip() or not skills.strip() or not experience.strip():
        st.warning("Please complete all profile fields.")
    else:
        with st.spinner("Crafting your perfect proposal..."):
            # Match skills to job description
            matched_skills = match_skills(job_desc, skills)
            skills_str = ", ".join(matched_skills).title()

            # Define tone-specific instructions
            tone_instructions = {
                "Professional": "Use a formal, polished tone with precise language. Focus on expertise and reliability.",
                "Confident": "Emphasize confidence and proven success with bold, assertive language.",
                "Friendly": "Adopt a warm, approachable tone while maintaining professionalism.",
                "Creative": "Use engaging, imaginative language to stand out while addressing client needs."
            }

            prompt = f"""
You are an expert freelance proposal writer tasked with creating a highly persuasive, tailored proposal for a freelance job. Write a proposal in a {tone.lower()} tone that addresses the client's needs, showcases the freelancer's expertise, and positions them as the ideal candidate. Follow this structure:

1. **Introduction**: Greet the client, express enthusiasm for the project, and briefly summarize the project goal.
2. **Proposed Solution**: Outline a clear, step-by-step approach to meet the client's requirements, incorporating relevant skills and technologies.
3. **Qualifications**: Highlight the freelancer's relevant experience, skills, and achievements, emphasizing alignment with the job description.
4. **Timeline and Deliverables**: Provide a realistic timeline and key deliverables.
5. **Closing and Call-to-Action**: Reiterate enthusiasm, invite further discussion, and provide contact details.

Ensure the proposal is concise (300-400 words), professional, and tailored to the job description. Avoid generic phrases and focus on specific, actionable insights.

**Job Description**:
{job_desc}

**Freelancer Profile**:
- Name: {name}
- Title: {title}
- Skills: {skills_str}
- Experience: {experience}

**Tone Instructions**: {tone_instructions[tone]}
"""
            proposal = query_hf_model(prompt)

        if proposal:
            st.subheader("📬 Your Proposal")
            st.markdown(proposal)
            st.download_button("📥 Download Proposal", proposal, file_name="freelance_proposal.md", mime="text/markdown")
        else:
            st.error("Failed to generate proposal. Please try again.")
