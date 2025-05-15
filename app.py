import streamlit as st
from cv_parser import extract_cv_text
from openai_llm_utils import evaluate_candidate, generate_mcqs
import json
import base64
from fpdf import FPDF
import io
import datetime

# Initialize session state variables
if 'page' not in st.session_state:
    st.session_state.page = 'job_posting'
if 'job_title' not in st.session_state:
    st.session_state.job_title = ''
if 'job_desc' not in st.session_state:
    st.session_state.job_desc = ''
if 'job_skills' not in st.session_state:
    st.session_state.job_skills = ''
if 'cv_text' not in st.session_state:
    st.session_state.cv_text = ''
if 'screening_result' not in st.session_state:
    st.session_state.screening_result = None
if 'mcqs' not in st.session_state:
    st.session_state.mcqs = None
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'score' not in st.session_state:
    st.session_state.score = 0

# Navigation functions
def go_to_page(page):
    st.session_state.page = page

# Function to create downloadable PDF
def create_pdf(job_title, candidate_name, mcqs, answers, score):
    pdf = FPDF()
    pdf.add_page()
    
    # Set up the PDF
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Candidate Assessment Report", ln=True, align="C")
    pdf.ln(5)
    
    # Add date
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True)
    
    # Add job and candidate info
    pdf.set_font("Arial", "B", 12)
    # Sanitize text to ensure it's compatible with latin1 encoding
    safe_job_title = ''.join(c if ord(c) < 128 else '_' for c in job_title)
    safe_candidate_name = ''.join(c if ord(c) < 128 else '_' for c in candidate_name)
    
    pdf.cell(0, 10, f"Position: {safe_job_title}", ln=True)
    pdf.cell(0, 10, f"Candidate: {safe_candidate_name}", ln=True)
    pdf.cell(0, 10, f"Assessment Score: {score}%", ln=True)
    pdf.ln(5)
    
    # Add MCQs and answers
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Assessment Questions", ln=True)
    pdf.ln(5)
    
    for idx, mcq in enumerate(mcqs):
        pdf.set_font("Arial", "B", 11)
        # Sanitize question text
        safe_question = ''.join(c if ord(c) < 128 else '_' for c in mcq['question'])
        pdf.multi_cell(0, 10, f"{idx+1}. {safe_question}")
        
        pdf.set_font("Arial", "", 10)
        for i, option in enumerate(mcq['options']):
            # Sanitize option text
            safe_option = ''.join(c if ord(c) < 128 else '_' for c in option)
            # Use ASCII character instead of Unicode checkmark
            selected = "[X] " if answers.get(f"mcq_{idx}") == option else "[ ] "
            pdf.cell(0, 8, f"{selected}{safe_option}", ln=True)
        
        pdf.set_font("Arial", "B", 10)
        # Sanitize answer text
        safe_answer = ''.join(c if ord(c) < 128 else '_' for c in mcq['answer'])
        pdf.cell(0, 8, f"Correct Answer: {safe_answer}", ln=True)
        pdf.ln(5)
    
    try:
        return pdf.output(dest="S").encode("latin1")
    except UnicodeEncodeError:
        # If encoding still fails, use a more aggressive approach
        return pdf.output(dest="S").encode("latin1", errors="replace")

# Function to create a download link
def get_pdf_download_link(pdf_bytes, filename):
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download Assessment Report</a>'

# Main app title
st.title("🔍 TRC-AIcruit – Candidate Screening POC")

# Job Posting Page
if st.session_state.page == 'job_posting':
    st.header("Step 1: Job Posting")
    st.session_state.job_title = st.text_input("Job Title", value=st.session_state.job_title)
    st.session_state.job_desc = st.text_area("Job Description", value=st.session_state.job_desc)
    st.session_state.job_skills = st.text_input("Required Skills (comma-separated)", value=st.session_state.job_skills)
    
    if st.button("Next: Upload CV") and st.session_state.job_title and st.session_state.job_desc:
        go_to_page('upload_cv')

# CV Upload Page
elif st.session_state.page == 'upload_cv':
    st.header("Step 2: Upload CV")
    uploaded_file = st.file_uploader("Upload CV (PDF)", type="pdf")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back"):
            go_to_page('job_posting')
    
    with col2:
        if uploaded_file:
            st.session_state.cv_text = extract_cv_text(uploaded_file)
            st.success("✅ CV Text Extracted Successfully")
            if st.button("Next: AI Screening"):
                go_to_page('ai_screening')

# AI Screening Page
elif st.session_state.page == 'ai_screening':
    st.header("Step 3: AI Screening")
    
    if not st.session_state.screening_result:
        with st.spinner("Running LLaMA-3 evaluation..."):
            result_json, raw_response = evaluate_candidate(
                st.session_state.job_desc, 
                st.session_state.job_skills, 
                st.session_state.cv_text
            )
            st.session_state.screening_result = result_json
    
    if st.session_state.screening_result:
        st.metric("Fit Score", f"{st.session_state.screening_result['score']}%")
        st.success(f"Credible: {st.session_state.screening_result['credible'].upper()}")
        st.write(f"Reason: {st.session_state.screening_result['reason']}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                st.session_state.screening_result = None
                go_to_page('upload_cv')
        
        with col2:
            if st.session_state.screening_result.get("credible", "").lower() == "yes":
                if st.button("Next: MCQ Assessment"):
                    go_to_page('mcq_assessment')
    else:
        st.error("Failed to parse LLM response.")
        if st.button("← Back"):
            go_to_page('upload_cv')

# MCQ Assessment Page
elif st.session_state.page == 'mcq_assessment':
    st.header("Step 4: MCQ Assessment")
    
    if not st.session_state.mcqs:
        with st.spinner("Generating MCQs..."):
            mcqs, raw_mcqs = generate_mcqs(st.session_state.job_desc, st.session_state.job_skills, 5)  # Generate 5 MCQs
            st.session_state.mcqs = mcqs
    
    if st.session_state.mcqs:
        with st.form("mcq_form"):
            for idx, mcq in enumerate(st.session_state.mcqs):
                st.session_state.answers[f"mcq_{idx}"] = st.radio(
                    f"{idx+1}. {mcq['question']}", 
                    mcq['options'], 
                    key=f"mcq_{idx}"
                )
            
            submitted = st.form_submit_button("Submit Answers")
            if submitted:
                go_to_page('results')
        
        if st.button("← Back"):
            st.session_state.mcqs = None
            go_to_page('ai_screening')
    else:
        st.error("Failed to generate MCQs.")
        if st.button("← Back"):
            go_to_page('ai_screening')

# Results Page
elif st.session_state.page == 'results':
    st.header("Assessment Results")
    
    # Calculate score
    correct_answers = 0
    for idx, mcq in enumerate(st.session_state.mcqs):
        if st.session_state.answers.get(f"mcq_{idx}") == mcq['answer']:
            correct_answers += 1
    
    total_questions = len(st.session_state.mcqs)
    st.session_state.score = int((correct_answers / total_questions) * 100)
    
    # Display score
    st.metric("Your Score", f"{st.session_state.score}%")
    
    # Show answers
    st.subheader("Your Answers")
    for idx, mcq in enumerate(st.session_state.mcqs):
        selected = st.session_state.answers.get(f"mcq_{idx}")
        correct = mcq['answer']
        is_correct = selected == correct
        
        st.write(f"**{idx+1}. {mcq['question']}**")
        st.write(f"Your answer: {selected} {'✅' if is_correct else '❌'}")
        if not is_correct:
            st.write(f"Correct answer: {correct}")
        st.write("---")
    
    # Generate PDF report
    candidate_name = "Candidate"  # In a real app, you'd collect this
    pdf_bytes = create_pdf(
        st.session_state.job_title,
        candidate_name,
        st.session_state.mcqs,
        st.session_state.answers,
        st.session_state.score
    )
    
    # Create download link
    st.markdown(
        get_pdf_download_link(pdf_bytes, "assessment_report.pdf"), 
        unsafe_allow_html=True
    )
    
    # Navigation
    if st.button("Start New Assessment"):
        # Reset session state
        st.session_state.page = 'job_posting'
        st.session_state.screening_result = None
        st.session_state.mcqs = None
        st.session_state.answers = {}
        st.session_state.score = 0
        st.experimental_rerun()
