# TRC-AIcruit – AI-Powered Candidate Screening System

## Overview
TRC-AIcruit is a proof-of-concept application that leverages NVIDIA AI and LLaMA-3 to automate and enhance the candidate screening process. The system analyzes resumes, evaluates candidate fit, and conducts automated assessments to streamline hiring workflows.

## Features

- **Resume Parsing**: Automatically extracts text from PDF resumes
- **AI-Powered Screening**: Uses LLaMA-3 to evaluate candidate fit against job requirements
- **Automated MCQ Generation**: Creates custom assessment questions based on job skills
- **Assessment Scoring**: Automatically scores candidate responses
- **PDF Report Generation**: Creates downloadable assessment reports
- **Multi-step Workflow**: Guided process from job posting to final evaluation

## Technology Stack

- **Frontend**: Streamlit for the interactive web interface
- **AI/ML**: NVIDIA AI endpoints with LLaMA-3 70B model
- **PDF Processing**: pdfplumber for resume text extraction
- **Document Generation**: FPDF for creating assessment reports

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/trc-aicruit.git
   cd trc-aicruit
   ```

2. Create and activate a virtual environment:
   ```
   # Windows
   python -m venv myvenv
   myvenv\Scripts\activate
   
   # Linux/Mac
   python -m venv myvenv
   source myvenv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```
   streamlit run app.py
   ```

2. Access the web interface at http://localhost:8501

3. Follow the guided workflow:
   - Enter job details and requirements
   - Upload candidate resume (PDF format)
   - Review AI-generated screening results
   - Administer MCQ assessment
   - View and download final assessment report

## Project Structure

- `app.py`: Main Streamlit application with UI components
- `cv_parser.py`: PDF resume text extraction functionality
- `openai_llm_utils.py`: Integration with NVIDIA AI endpoints
- `requirements.txt`: Project dependencies

## Dependencies

- streamlit==1.32.0
- pdfplumber==0.10.3
- langchain-nvidia-ai-endpoints==0.0.3
- langchain-core==0.1.27
- fpdf==1.7.2
- python-dotenv==1.0.1

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NVIDIA for providing AI endpoints
- Meta for the LLaMA-3 model
- The Streamlit team for the excellent web framework