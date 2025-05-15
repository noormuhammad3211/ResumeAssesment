from openai import OpenAI
import json
import re

# Initialize the OpenAI client with NVIDIA API endpoint
client = OpenAI(
    base_url = "https://integrate.api.nvidia.com/v1",
    api_key = "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"
)

def evaluate_candidate(job_desc, job_skills, cv_text):
    prompt = f"""
You are an expert recruitment evaluator.

TASK:
1. Score the match between the job and candidate from 0-100.
2. Decide if the candidate is credible to proceed. (yes/no)
3. Justify your decision.

Respond in JSON:
{{
  "score": "...",
  "credible": "...",
  "reason": "..."
}}

JOB DESCRIPTION:
{job_desc}

SKILLS:
{job_skills}

CANDIDATE CV:
{cv_text}
"""
    
    raw_output = ""
    completion = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[{"role":"user","content":prompt}],
        temperature=0.2,
        top_p=0.7,
        stream=True
    )
    
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            raw_output += chunk.choices[0].delta.content
    
    try:
        match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        print("Raw LLM Response: ", raw_output)
        cleaned_text = match.group(0) if match else "{}"
        return json.loads(cleaned_text), raw_output
    except:
        return None, raw_output


def generate_mcqs(job_desc, job_skills, num_mcqs=3):
    prompt = f"""
Generate {num_mcqs} MCQs to evaluate a candidate for this role.

Job:
{job_desc}
Skills:
{job_skills}

Format as JSON list:

  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }},

"""
    
    raw_output = ""
    completion = client.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[{"role":"user","content":prompt}],
        temperature=0.2,
        top_p=0.7,
 
        stream=True
    )
    
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            raw_output += chunk.choices[0].delta.content
    
    try:
        match = re.search(r"\[.*\]", raw_output, re.DOTALL)
        print("Raw LLM Response: ", raw_output)
        cleaned_text = match.group(0) if match else "[]"
        print("Cleaned LLM Response: ", cleaned_text)
        return json.loads(cleaned_text), raw_output
    except:
        return None, raw_output