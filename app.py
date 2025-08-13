import streamlit as st
from io import StringIO
from docx import Document
import openai
import PyPDF2
import os
from openai import OpenAI
# Set your OpenAI API key here directly
api_key = "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"
client = OpenAI(api_key=api_key)


# --- Text extraction functions ---

def extract_text_from_docx(file):
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)

def extract_text(file) -> str:
    if file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file)
    elif file.type == "application/pdf":
        return extract_text_from_pdf(file)
    elif file.type.startswith("text/"):
        stringio = StringIO(file.getvalue().decode("utf-8"))
        return stringio.read()
    else:
        return None

# --- GPT Contract analysis functions ---

from openai import OpenAI

client = OpenAI(api_key="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")

def summarize(document: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You're an exceptional lawyer skilled at distilling long contracts into short paragraphs that are easy to understand and digest."},
            {"role": "user", "content": f"Provide an executive summary for the following contract: {document}"}
        ]
    )
    return response.choices[0].message.content

def get_obligations(document: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Highlight the key obligations from the following contract: {document}"}
        ]
    )
    return response.choices[0].message.content

def extract_important_dates(document: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Find all important dates and deadlines in this contract: {document}"}
        ]
    )
    return response.choices[0].message.content

def extract_termination_clauses(document: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Highlight the termination clauses in this contract: {document}"}
        ]
    )
    return response.choices[0].message.content

def highlight_confidentiality_noncompete(document: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Identify confidentiality and non-compete clauses in this contract: {document}"}
        ]
    )
    return response.choices[0].message.content


# --- Streamlit UI ---

def main():
    st.title("Contract Analyzer with GPT")

    uploaded_file = st.file_uploader("Upload your contract file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

    if uploaded_file is not None:
        with st.spinner("Extracting text from file..."):
            text = extract_text(uploaded_file)

        if not text:
            st.error("Unsupported file type or unable to extract text.")
            return

        st.subheader("Contract Text Preview")
        st.write(text[:2000] + ("..." if len(text) > 2000 else ""))  # Show first 2000 chars only

        if st.button("Analyze Contract"):
            with st.spinner("Analyzing..."):
                summary = summarize(text)
                obligations = get_obligations(text)
                dates = extract_important_dates(text)
                termination = extract_termination_clauses(text)
                confidentiality = highlight_confidentiality_noncompete(text)

            st.subheader("Executive Summary")
            st.write(summary)

            st.subheader("Key Obligations")
            st.write(obligations)

            st.subheader("Important Dates / Deadlines")
            st.write(dates)

            st.subheader("Termination Clauses")
            st.write(termination)

            st.subheader("Confidentiality and Non-Compete Clauses")
            st.write(confidentiality)

if __name__ == "__main__":
    main()


