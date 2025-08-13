import streamlit as st
from io import StringIO
from docx import Document
import os
import google.generativeai as genai
import PyPDF2
import requests
from dotenv import load_dotenv
load_dotenv
# === Replace with your Gemini API key ===
GEMINI_API_KEY = "AIzaSyAcNpcg-uXN-Nt4qoHxhW2yA3G8GhVQ7nA"

# === Gemini API endpoint ===
GEMINI_API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateText"

# --- Text extraction functions ---
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)

def extract_text(file):
    if file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file)
    elif file.type == "application/pdf":
        return extract_text_from_pdf(file)
    elif file.type.startswith("text/"):
        stringio = StringIO(file.getvalue().decode("utf-8"))
        return stringio.read()
    else:
        return None

# --- Gemini API call ---
def call_gemini_api(prompt_text):
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    data = {
        "model": "models/gemini-2.0-flash",
        "temperature": 0.2,
        "candidate_count": 1,
        "max_output_tokens": 800,
        "prompt": {
            "text": prompt_text
        }
    }
    response = requests.post(GEMINI_API_ENDPOINT, headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        return response_json.get("candidates", [{}])[0].get("output", "No response from Gemini.")
    else:
        return f"Error from Gemini API: {response.status_code} - {response.text}"

# --- Streamlit UI ---
def main():
    st.title("Contract Analyzer with Google Gemini API")

    uploaded_file = st.file_uploader("Upload your contract file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

    if uploaded_file is not None:
        with st.spinner("Extracting text from file..."):
            contract_text = extract_text(uploaded_file)

        if not contract_text:
            st.error("Unsupported file type or unable to extract text.")
            return

        st.subheader("Contract Text Preview")
        st.write(contract_text[:2000] + ("..." if len(contract_text) > 2000 else ""))

        if st.button("Analyze Contract"):
            st.info("Analyzing contract with Google Gemini AI...")

            tasks = {
                "Executive Summary": f"Provide a concise executive summary of this contract:\n\n{contract_text}",
                "Key Obligations": f"List the key obligations from this contract:\n\n{contract_text}",
                "Important Dates / Deadlines": f"Extract all important dates and deadlines mentioned:\n\n{contract_text}",
                "Termination Clauses": f"Highlight the termination clauses in this contract:\n\n{contract_text}",
                "Confidentiality and Non-Compete Clauses": f"Identify confidentiality and non-compete clauses:\n\n{contract_text}",
            }

            results = {}
            for section, prompt in tasks.items():
                with st.spinner(f"Analyzing: {section}"):
                    output = call_gemini_api(prompt)
                    results[section] = output

            for section, output in results.items():
                st.subheader(section)
                st.write(output)

if __name__ == "__main__":
    main()
