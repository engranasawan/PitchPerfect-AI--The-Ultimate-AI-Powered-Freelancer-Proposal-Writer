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
CSS_URL = "https://raw.githubusercontent.com/engranasawan/PitchPerfect-AI--The-Ultimate-AI-Powered-Freelancer-Proposal-Writer/master/styles.css"
LOGO_URL = "https://raw.githubusercontent.com/engranasawan/PitchPerfect-AI--The-Ultimate-AI-Powered-Freelancer-Proposal-Writer/main/logo.png"
FALLBACK_LOGO = "https://i.imgur.com/JQ9w0Vr.png"

# ========== HELPER FUNCTIONS ==========
def load_css():
    """Load CSS from GitHub with local fallback"""
    try:
        # Try GitHub first
        response = requests.get(CSS_URL, timeout=5)
        if response.status_code == 200:
            st.markdown(f"<style>{response.text}</style>", unsafe_allow_html=True)
            return
    except:
        pass
    
    # Local fallback
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        st.warning("Couldn't load custom styles")

def load_logo(width=150):
    """Load logo with multiple fallback options"""
    try:
        response = requests.get(LOGO_URL, timeout=5)
        if response.status_code == 200:
            logo = Image.open(BytesIO(response.content))
            st.image(logo, width=width)
            return True
    except:
        pass
    
    try:
        st.image(FALLBACK_LOGO, width=width)
        return True
    except:
        st.markdown("<h1 style='text-align:center;'>PitchPerfect AI</h1>", unsafe_allow_html=True)
        return False

def query_hf_model(prompt):
    """Query Hugging Face model with robust error handling"""
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
        start_time = time.time()
        with st.spinner("Generating proposal..."):
            response = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"},
                json=payload,
                timeout=60
            )
        
        if response.status_code == 503:  # Model loading
            raise Exception("Model is loading, please try again in 30-60 seconds")
        
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list):
            return clean_proposal_output(result[0].get("generated_text", ""))
        return clean_proposal_output(result.get("generated_text", ""))
    
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return ""
    except Exception as e:
        st.error(f"Generation error: {str(e)}")
        return ""

def clean_proposal_output(text):
    """Clean and format the proposal output"""
    if not text:
        return ""
    
    # Remove prompt leakage
    text = re.sub(r'^.*?(?=Subject:|\nDear|Proposal:)', '', text, flags=re.DOTALL)
    # Remove meta comments
    text = re.sub(r'(Please note:|Let me know if).*$', '', text, flags=re.DOTALL)
    # Normalize whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text.strip())
    return text

def extract_text_from_file(uploaded_file):
    """Extract text from PDF, DOCX, or TXT files"""
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
    # Configure page
    st.set_page_config(
        page_title="PitchPerfect AI",
        page_icon="✍️",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Load styling
    load_css()
    
    # Header Section
    col1, col2 = st.columns([1, 3])
    with col1:
        load_logo(width=100)
    with col2:
        st.markdown("<h1 style='margin-bottom:0;color:#4a8fe7'>PitchPerfect AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='margin-top:0;color:#a1c4fd'>Ultimate Proposal Writer</p>", unsafe_allow_html=True)
    
    # Job Description Section
    with st.expander("📄 STEP 1: Job Details", expanded=True):
        uploaded_file = st.file_uploader(
            "Upload job description (PDF/DOCX/TXT)", 
            type=["pdf", "docx", "txt"],
            help="Supported formats: PDF, Word, or plain text"
        )
        job_desc = st.text_area(
            "Or paste job description here",
            value=extract_text_from_file(uploaded_file) if uploaded_file else "",
            height=200,
            placeholder="Paste the job description here...",
            label_visibility="collapsed"
        )
    
    # Freelancer Profile Section
    with st.expander("👤 STEP 2: Your Profile", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="Your full name")
            email = st.text_input("Email", placeholder="professional@email.com")
            tone = st.selectbox(
                "Proposal Tone", 
                ["Professional", "Persuasive", "Friendly", "Technical"],
                help="Select the tone that matches your personal brand"
            )
        with col2:
            title = st.text_input("Professional Title", placeholder="e.g. AI/ML Engineer")
            linkedin = st.text_input("LinkedIn Profile", placeholder="linkedin.com/in/yourprofile")
            urgency = st.selectbox("Availability", ["Immediately", "Within 48 hours", "Next week"])
        
        skills = st.text_input(
            "Key Skills (comma separated)", 
            placeholder="Python, Deep Learning, Data Analysis"
        )
        experience = st.text_area(
            "Professional Experience", 
            placeholder="Brief summary of your relevant experience", 
            height=80
        )
        achievements = st.text_area(
            "Key Achievements", 
            placeholder="Quantifiable results from past projects (e.g., 'Increased conversion by 30%')", 
            height=80
        )
    
    # Generate Button
    if st.button("✨ Generate My Proposal", type="primary", use_container_width=True):
        if not job_desc.strip():
            st.warning("Please provide a job description")
        elif not name.strip():
            st.warning("Please enter your name")
        else:
            with st.spinner("Crafting your perfect proposal..."):
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
                with st.container(border=True):
                    st.subheader("📝 Your Proposal")
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
                        file_name=f"proposal_{name.replace(' ', '_')}.txt"
                    )
                with col2:
                    st.download_button(
                        "📄 Download as DOCX",
                        proposal,
                        file_name=f"proposal_{name.replace(' ', '_')}.docx"
                    )
            else:
                st.error("Failed to generate proposal. Please try again.")
    
    # Tips Section
    st.markdown("---")
    with st.expander("💡 Proposal Writing Tips", expanded=True):
        st.markdown("""
        <div style='background-color:#1a3a4e;padding:1rem;border-radius:8px;border-left:4px solid #3a5a78'>
        ✨ **Make it personal** - Show you understand their specific needs  
        🌟 **Highlight results** - "Increased conversions by 30%" beats "Worked on conversions"  
        🔍 **Be specific** - "I'll use TensorFlow with LSTM layers" vs "I know AI"  
        ⏱️ **Show urgency** - "I can start immediately and deliver in 2 weeks"  
        📞 **Clear CTA** - "Let's schedule a call Tuesday to discuss details"  
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#7F7F7F;margin-top:1rem'>"
        "🌿 PitchPerfect AI - Helping freelancers win more projects"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
