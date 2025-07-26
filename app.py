import streamlit as st
import requests
import fitz  # PyMuPDF
import docx
import re
from PIL import Image


def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback to GitHub raw content if local file not found
        github_css_url = "https://raw.githubusercontent.com/engranasawan/PitchPerfect-AI--The-Ultimate-AI-Powered-Freelancer-Proposal-Writer/master/styles.css"
        css_content = requests.get(github_css_url).text
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# === Hugging Face API Setup ===
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-11B-Vision-Instruct"
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}", "Content-Type": "application/json"}

def query_hf_model(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1200,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "do_sample": True
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and result:
            return clean_proposal_output(result[0].get("generated_text", ""))
        elif isinstance(result, dict) and "generated_text" in result:
            return clean_proposal_output(result["generated_text"])
        return ""
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return ""

def clean_proposal_output(text):
    """Remove prompt leakage and clean up formatting"""
    # Remove everything before the actual proposal starts
    start_markers = ["Here is my response:", "Proposal:", "Subject:"]
    for marker in start_markers:
        if marker in text:
            text = text.split(marker)[-1]
    
    # Remove any remaining prompt instructions
    text = re.sub(r'Please note.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'Let me know if.*$', '', text, flags=re.DOTALL)
    
    # Clean up whitespace and formatting
    text = text.strip()
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove excessive newlines
    return text

def extract_text_from_file(uploaded_file):
    ext = uploaded_file.name.split(".")[-1].lower()
    try:
        if ext == "pdf":
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                return "\n".join([page.get_text() for page in doc])
        elif ext == "docx":
            doc = docx.Document(uploaded_file)
            return "\n".join([p.text for p in doc.paragraphs])
        elif ext == "txt":
            return uploaded_file.read().decode("utf-8")
        return ""
    except Exception as e:
        st.error(f"File processing error: {str(e)}")
        return ""

# === Streamlit UI ===
st.set_page_config(
    page_title="🌿 PitchPerfect AI",
    layout="centered",
    page_icon="✍️",
    initial_sidebar_state="collapsed"
)

# Custom CSS
local_css("style.css")  # Create this file with the CSS below

# App Header
st.image("https://i.imgur.com/JQ9w0Vr.png", width=150)  # Replace with your logo
st.markdown("<h1 style='text-align: center; color: #2E8B57;'>🌿 PitchPerfect AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #5F9EA0; font-weight: 300;'>Craft Winning Freelance Proposals</h3>", unsafe_allow_html=True)

# --- Job Description Input ---
with st.expander("📄 STEP 1: Job Details", expanded=True):
    uploaded_file = st.file_uploader("Upload job description (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"], help="Or paste below")
    job_desc = extract_text_from_file(uploaded_file) if uploaded_file else ""
    job_desc = st.text_area("Paste job description here", value=job_desc, height=200, 
                          placeholder="Paste the full job description here...", 
                          label_visibility="collapsed")

# --- Freelancer Info ---
with st.expander("👤 STEP 2: Your Profile", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", placeholder="Your full name")
        email = st.text_input("Email", placeholder="professional@email.com")
        tone = st.selectbox("Proposal Tone", ["Professional", "Persuasive", "Friendly", "Technical"], 
                          help="Select the tone that matches your brand")
    with col2:
        title = st.text_input("Professional Title", placeholder="e.g. AI/ML Engineer")
        linkedin = st.text_input("LinkedIn Profile", placeholder="linkedin.com/in/yourprofile")
        urgency = st.selectbox("Availability", ["Immediately", "Within 48 hours", "Next week"])
    
    skills = st.text_input("Key Skills (comma separated)", placeholder="Python, Deep Learning, Data Analysis")
    experience = st.text_area("Professional Experience", placeholder="Brief summary of your relevant experience", height=80)
    achievements = st.text_area("Key Achievements (optional)", 
                              placeholder="Quantifiable results from past projects", 
                              height=80,
                              help="Example: 'Increased conversion by 30% for Client X'")

# --- Generate Button ---
st.markdown("<div class='generate-container'>", unsafe_allow_html=True)
generate_btn = st.button("✨ Generate My Proposal", type="primary", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

if generate_btn:
    if not job_desc.strip():
        st.warning("Please provide a job description")
    elif not name.strip():
        st.warning("Please enter your name")
    else:
        with st.spinner("🌱 Crafting your perfect proposal..."):
            # Hidden system prompt
            system_prompt = """You are a top-tier freelance proposal writer. 
            Create a professional proposal that includes: 
            1. Subject line
            2. Personalized intro showing understanding of their needs
            3. Your proposed solution with technical details
            4. Your qualifications matching their requirements
            5. Project timeline
            6. Professional closing with contact info
            Format cleanly with line breaks between sections."""
            
            user_prompt = f"""
Create a {tone.lower()} proposal for this job:

**Job Description:**
{job_desc}

**Freelancer Details:**
- Name: {name}
- Title: {title}
- Email: {email}
- LinkedIn: {linkedin}
- Skills: {skills}
- Experience: {experience}
- Achievements: {achievements}
- Availability: {urgency}

Include all contact information at the end.
"""
            proposal = query_hf_model(system_prompt + user_prompt)

        if proposal:
            st.success("✅ Your proposal is ready!")
            st.markdown("<div class='proposal-container'>", unsafe_allow_html=True)
            st.subheader("📝 Your Custom Proposal")
            st.text_area("Proposal", proposal, height=400, label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Download options
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Download as TXT", proposal, file_name=f"proposal_{name.replace(' ', '_')}.txt")
            with col2:
                st.download_button("📄 Download as DOCX", proposal, file_name=f"proposal_{name.replace(' ', '_')}.docx")
        else:
            st.error("Failed to generate proposal. Please try again.")

# --- Tips Section ---
st.markdown("---")
with st.expander("💡 Proposal Writing Tips", expanded=True):
    st.markdown("""
    <div class="tips-container">
    ✨ **Make it personal** - Show you understand their specific needs  
    🌟 **Highlight results** - "Increased conversions by 30%" beats "Worked on conversions"  
    🔍 **Be specific** - "I'll use TensorFlow with LSTM layers" vs "I know AI"  
    ⏱️ **Show urgency** - "I can start immediately and deliver in 2 weeks"  
    📞 **Clear CTA** - "Let's schedule a call Tuesday to discuss details"  
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #7F7F7F; margin-top: 30px;'>🌿 PitchPerfect AI - Helping freelancers win more projects</div>", unsafe_allow_html=True)
