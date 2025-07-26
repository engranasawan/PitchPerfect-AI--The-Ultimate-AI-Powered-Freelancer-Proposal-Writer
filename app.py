import streamlit as st
import requests
import fitz  # PyMuPDF
import docx
import os
import textwrap

# === Hugging Face API Setup ===
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-70B-Instruct"
headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}", "Content-Type": "application/json"}

def query_hf_model(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1200,
            "temperature": 0.65,
            "top_p": 0.9,
            "repetition_penalty": 1.1
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and result:
            return result[0].get("generated_text", "")
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"]
        else:
            st.error(f"Unexpected response format: {result}")
            return ""
    except requests.exceptions.RequestException as e:
        st.error(f"API Request Failed: {str(e)}")
        return ""
    except ValueError:
        st.error("Invalid JSON response from API")
        return ""

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

# === Proposal Template Formatter ===
def format_proposal(proposal_text):
    formatted = ""
    for line in proposal_text.split('\n'):
        if line.startswith('**') and line.endswith('**'):
            formatted += f"\n{line}\n"
        elif line.strip() == '':
            formatted += '\n'
        else:
            formatted += textwrap.fill(line, width=80) + '\n\n'
    return formatted

# === Streamlit UI ===
st.set_page_config(
    page_title="🚀 PitchPerfect AI - Ultimate Proposal Writer",
    layout="centered",
    page_icon="💼"
)

st.title("🚀 PitchPerfect AI - Ultimate Proposal Writer")
st.markdown("### Generate Winning Freelance Proposals in Seconds")

# --- Job Description Input ---
with st.expander("📄 Job Details", expanded=True):
    uploaded_file = st.file_uploader("Upload job description (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    job_desc = extract_text_from_file(uploaded_file) if uploaded_file else ""
    job_desc = st.text_area("Or paste job description here", value=job_desc, height=200, placeholder="Paste full job description here...")

# --- Freelancer Info ---
with st.expander("👤 Your Profile", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Name", "Jane Doe")
        title = st.text_input("Professional Title", "AI/ML Engineer")
    with col2:
        tone = st.selectbox("Tone", ["Professional", "Confident", "Friendly", "Expert"])
        urgency = st.selectbox("Project Urgency", ["Standard", "Urgent", "ASAP"])
    
    skills = st.text_input("Key Skills (comma separated)", "Python, Deep Learning, TensorFlow, Fraud Detection")
    experience = st.text_area("Experience Summary", "3+ years building fraud detection systems for e-commerce platforms", height=80)
    
    # Achievement repository
    achievements = st.text_area("Key Achievements (optional)", 
                              "Reduced fake seller incidents by 87% for XYZ Platform, Developed real-time fraud detection for ABC Marketplace",
                              height=80,
                              help="Mention quantifiable results from past projects")

# --- Generate Button ---
generate_btn = st.button("✨ Generate Proposal", type="primary", use_container_width=True)

if generate_btn:
    if not job_desc.strip():
        st.warning("Please provide a job description")
    else:
        with st.spinner("Crafting your winning proposal..."):
            # Enhanced prompt with strategic guidance
            prompt = f"""
You are a world-class freelance proposal writer with 10+ years of experience. 
Create an exceptional proposal for this job that will stand out from competitors. 
Use {tone.lower()} tone and address the client's pain points directly.

**Job Description:**
{job_desc}

**Freelancer Profile:**
- Name: {name}
- Title: {title}
- Core Skills: {skills}
- Experience: {experience}
- Key Achievements: {achievements}
- Project Urgency: {urgency}

**Create proposal with this structure:**
1. **Catchy Subject Line** (15 words max)
2. **Opening Hook** - Show deep understanding of their problem
3. **Proposed Solution** - Specific approach with technical details
4. **Why Choose Me** - Match each requirement to your skills/achievements
5. **Project Timeline** - Phased delivery plan
6. **Call to Action** - Clear next steps

**Critical Requirements:**
- Start with "Subject: [Your Subject Line]"
- Address ALL client requirements from job description
- Include 3 SPECIFIC technical details about implementation
- Mention {achievements if achievements else 'relevant experience'} with results
- Add urgency indicator: "I can start [immediately/within 24 hours]"
- End with powerful CTA: "Let's schedule a call to discuss implementation details"
- Keep under 500 words
"""
            proposal = query_hf_model(prompt)
            formatted_proposal = format_proposal(proposal) if proposal else ""

        if formatted_proposal:
            st.success("✅ Proposal Generated - Customize as needed")
            
            # Enhanced display with tabs
            tab1, tab2 = st.tabs(["Proposal Preview", "Prompt Details"])
            with tab1:
                st.subheader("📝 Your Proposal")
                st.text_area("Proposal", formatted_proposal, height=400, label_visibility="collapsed")
                st.download_button("💾 Download Proposal", formatted_proposal, file_name="winning_proposal.txt")
            
            with tab2:
                st.subheader("🧠 Generation Prompt")
                st.code(prompt, language="text")
        else:
            st.error("Failed to generate proposal. Please try again.")

# Add tips section
st.markdown("---")
st.markdown("### 💡 Tips for Winning Proposals")
st.markdown("""
1. **Quantify achievements** - Use numbers to demonstrate impact  
2. **Address pain points** - Show you understand their specific challenges  
3. **Include technical specifics** - Demonstrate expertise through implementation details  
4. **Add urgency** - Mention immediate availability  
5. **Personalize** - Reference specific requirements from their job description  
""")
