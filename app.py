import streamlit as st
import requests
import fitz  # PyMuPDF
import docx
import re
from PIL import Image
from io import BytesIO
import time

# ========== CONSTANTS ==========
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-11B-Vision-Instruct"
LOGO_URL = "https://raw.githubusercontent.com/engranasawan/PitchPerfect-AI--The-Ultimate-AI-Powered-Freelancer-Proposal-Writer/master/logo.png"
GRADIENT = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
DARK_BG = "#121212"
CARD_BG = "#1e1e1e"
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#9678d3"  # Lavender accent

# ========== CUSTOM CSS ==========
def load_css():
    st.markdown(f"""
    <style>
    /* Main styling */
    .stApp {{
        background-color: {DARK_BG};
        color: {TEXT_COLOR};
    }}
    
    /* Header styling */
    .header {{
        background: {GRADIENT};
        padding: 2rem;
        border-radius: 0 0 20px 20px;
        color: white;
        margin-bottom: 2rem;
    }}
    
    /* Card styling */
    .card, .stExpander {{
        background: {CARD_BG} !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        border: none !important;
    }}
    
    /* Button styling */
    .stButton>button {{
        background: {GRADIENT} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3) !important;
    }}
    
    /* Input fields - Fixed dark mode styling */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea {{
        background-color: {CARD_BG} !important;
        color: {TEXT_COLOR} !important;
        border-radius: 12px !important;
        border: 1px solid #333 !important;
        padding: 10px 15px !important;
    }}
    
    /* Placeholder text color */
    .stTextInput input::placeholder, 
    .stTextArea textarea::placeholder {{
        color: #aaa !important;
        opacity: 1 !important;
    }}
    
    /* Proposal container */
    .proposal-container {{
        background: {CARD_BG};
        border-radius: 15px;
        padding: 2rem;
        border-left: 5px solid {ACCENT_COLOR};
    }}
    
    /* Tips styling */
    .tips-container {{
        background: #2a2342;  /* Dark lavender */
        border-radius: 15px;
        padding: 1.5rem;
        border-left: 5px solid {ACCENT_COLOR};
    }}
    
    /* Footer styling */
    .footer {{
        text-align: center;
        margin-top: 3rem;
        color: #aaa;
        font-size: 0.9rem;
    }}
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6, p, div {{
        color: {TEXT_COLOR} !important;
    }}
    
    /* Select dropdowns */
    .stSelectbox>div>div>select {{
        background-color: {CARD_BG} !important;
        color: {TEXT_COLOR} !important;
        border: 1px solid #333 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ========== HELPER FUNCTIONS ==========
def load_logo(width=120):
    try:
        response = requests.get(LOGO_URL, timeout=5)
        logo = Image.open(BytesIO(response.content))
        st.image(logo, width=width)
    except:
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:1rem;">
            <svg width="{width}" height="{width}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="{ACCENT_COLOR}" stroke-width="2"/>
                <path d="M2 17L12 22L22 17" stroke="{ACCENT_COLOR}" stroke-width="2"/>
                <path d="M2 12L12 17L22 12" stroke="{ACCENT_COLOR}" stroke-width="2"/>
            </svg>
        </div>
        """, unsafe_allow_html=True)

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
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"},
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return clean_proposal_output(result[0].get("generated_text", "")) if isinstance(result, list) else ""
    except Exception as e:
        st.error(f"Error generating proposal: {str(e)}")
        return ""

def clean_proposal_output(text):
    text = re.sub(r'^.*?(?=Subject:|\nDear|Proposal:)', '', text, flags=re.DOTALL)
    text = re.sub(r'(Please note:|Let me know if).*$', '', text, flags=re.DOTALL)
    return re.sub(r'\n\s*\n', '\n\n', text.strip())

def extract_text_from_file(uploaded_file):
    if not uploaded_file:
        return ""
    
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
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
    return ""

# ========== STREAMLIT UI ==========
def main():
    st.set_page_config(
        page_title="PitchPerfect AI",
        page_icon="💎",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    load_css()
    
    # Header Section
    st.markdown(f"""
    <div class="header">
        <div style="display:flex; align-items:center; justify-content:center; gap:1rem; margin-bottom:1rem;">
            {load_logo(width=80)}
            <h1 style="margin:0; color:white;">PitchPerfect AI</h1>
        </div>
        <p style="text-align:center; margin:0; font-size:1.1rem; opacity:0.9;">
        Craft proposals that win projects
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Job Description Card
    with st.expander("📋 Job Details", expanded=True):
        uploaded_file = st.file_uploader(
            "Upload job description (PDF/DOCX/TXT)", 
            type=["pdf", "docx", "txt"],
            label_visibility="collapsed"
        )
        job_desc = st.text_area(
            "Or paste job description here",
            value=extract_text_from_file(uploaded_file) if uploaded_file else "",
            height=200,
            placeholder="Paste the job description here...",
            label_visibility="collapsed"
        )
    
    # Freelancer Profile Card
    with st.expander("👤 Your Profile", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="Your full name")
            email = st.text_input("Email", placeholder="professional@email.com")
            tone = st.selectbox("Proposal Tone", ["Professional", "Persuasive", "Friendly", "Technical"])
        with col2:
            title = st.text_input("Professional Title", placeholder="e.g. AI/ML Engineer")
            linkedin = st.text_input("LinkedIn Profile", placeholder="linkedin.com/in/yourprofile")
            urgency = st.selectbox("Availability", ["Immediately", "Within 48 hours", "Next week"])
        
        skills = st.text_input("Key Skills (comma separated)", placeholder="Python, Deep Learning, Data Analysis")
        experience = st.text_area("Professional Experience", placeholder="Brief summary of your relevant experience", height=80)
        achievements = st.text_area("Key Achievements", placeholder="Quantifiable results from past projects", height=80)
    
    # Generate Button
    if st.button("✨ Generate My Proposal", type="primary", use_container_width=True):
        if not job_desc.strip():
            st.warning("Please provide a job description")
        elif not name.strip():
            st.warning("Please enter your name")
        else:
            with st.spinner("✨ Crafting your perfect proposal..."):
                prompt = f"""Create a {tone.lower()} proposal for this job:

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

Structure with:
1. Clear subject line
2. Personalized introduction
3. Technical solution approach
4. Relevant qualifications
5. Project timeline
6. Professional closing with contact info"""
                
                proposal = query_hf_model(prompt)
            
            if proposal:
                st.success("✅ Proposal Generated!")
                with st.container():
                    st.markdown("""
                    <div class="proposal-container">
                        <h3 style="margin-top:0;">📝 Your Proposal</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    st.text_area(
                        "Proposal Content", 
                        proposal, 
                        height=400,
                        label_visibility="collapsed"
                    )
                
                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Download as TXT",
                        proposal,
                        file_name=f"proposal_{name.replace(' ', '_')}.txt",
                        use_container_width=True
                    )
                with col2:
                    st.download_button(
                        "📄 Download as DOCX",
                        proposal,
                        file_name=f"proposal_{name.replace(' ', '_')}.docx",
                        use_container_width=True
                    )
    
    # Tips Section
    st.markdown("---")
    with st.expander("💡 Proposal Writing Tips", expanded=True):
        st.markdown("""
        <div class="tips-container">
            <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:1rem;">
                <div>
                    <h4 style="margin:0 0 0.5rem 0; color:{ACCENT_COLOR};">✨ Be Personal</h4>
                    <p style="margin:0;">Show you understand their specific needs</p>
                </div>
                <div>
                    <h4 style="margin:0 0 0.5rem 0; color:{ACCENT_COLOR};">📈 Show Results</h4>
                    <p style="margin:0;">"Increased conversions by 30%"</p>
                </div>
                <div>
                    <h4 style="margin:0 0 0.5rem 0; color:{ACCENT_COLOR};">⏱️ Create Urgency</h4>
                    <p style="margin:0;">"I can start immediately"</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>💎 PitchPerfect AI - Helping freelancers win more projects</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
