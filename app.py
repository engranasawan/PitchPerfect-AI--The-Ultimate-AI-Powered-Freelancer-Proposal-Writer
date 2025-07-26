import streamlit as st
import requests
import fitz  # PyMuPDF
import docx

# === Hugging Face API Setup ===
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-11B-Vision-Instruct"
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}", "Content-Type": "application/json"}


def query_hf_model(prompt, max_tokens=400, temperature=0.3):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_tokens, "temperature": temperature}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    try:
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list):
            return result[0].get("generated_text", "❌ No proposal generated.")
        if isinstance(result, dict) and "error" in result:
            st.error(f"❌ API Error: {result['error']}")
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
    if ext == "docx":
        doc_obj = docx.Document(uploaded_file)
        return "\n".join([p.text for p in doc_obj.paragraphs])
    if ext == "txt":
        return uploaded_file.read().decode("utf-8")
    return ""


# === Streamlit UI ===
st.set_page_config(page_title="PitchPerfect AI", layout="wide")
st.title("📝 PitchPerfect AI — World’s Best Proposal Writer")

# --- Job Description Input ---
st.subheader("1. 📄 Job Description")
uploaded_file = st.file_uploader("Upload job description (PDF, DOCX, TXT)", type=["pdf","docx","txt"])
job_desc = extract_text_from_file(uploaded_file) if uploaded_file else ""
job_desc = st.text_area("Or paste job description here", value=job_desc, height=200)

# --- Freelancer Info ---
st.subheader("2. 👤 Your Profile & Preferences")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name", "Jane Doe")
    title = st.text_input("Title", "AI/ML Engineer")
    experience = st.text_area("Experience Summary", "3+ years delivering AI/ML solutions")
with col2:
    skills = st.text_area("Key Skills (comma-separated)", "Python, Deep Learning, TensorFlow")
    tone = st.selectbox("Tone", ["Professional", "Confident", "Friendly", "Persuasive"])
    length = st.slider("Proposal Length (approx. words)", 200, 800, 400)

# --- Generate Button ---
if st.button("🚀 Generate Proposal"):
    if not job_desc.strip():
        st.warning("Please provide a job description.")
    else:
        with st.spinner("Crafting your winning proposal..."):
            # Enhanced prompt template
            prompt = f"""
You are an expert freelance proposal writer. Given the following job description and freelancer profile, generate a compelling proposal with these sections:
1. Personalized Greeting
2. Executive Summary (highlight your fit)
3. Proposed Approach (3-5 bullet points)
4. Key Deliverables & Timeline
5. Why Me? (unique value, results)
6. Call to Action

Job Description:
{job_desc}

Freelancer Profile:
Name: {name}
Title: {title}
Skills: {skills}
Experience: {experience}
Tone: {tone}
Target Word Count: {length}
"""
            proposal = query_hf_model(prompt, max_tokens=int(length*1.5/0.75), temperature=0.25)
        if proposal:
            st.subheader("📬 Your Proposal")
            st.text_area("Proposal", proposal, height=400)
            st.download_button("📥 Download Proposal", proposal, file_name="proposal.txt")
