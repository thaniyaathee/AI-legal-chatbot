import streamlit as st
import fitz  # PyMuPDF for PDF extraction
import pytesseract  # OCR for extracting text from images
from PIL import Image  # Image processing
import docx  # For extracting text from Word documents
import ollama  # Use locally installed Mistral model
import io
import re

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text("text") + "\n"
    return text.strip()

# Function to extract text from image (JPG, PNG)
def extract_text_from_image(uploaded_file):
    image = Image.open(uploaded_file)
    text = pytesseract.image_to_string(image)  # Extract text using OCR
    return text.strip()

# Function to extract text from Word Document (.docx)
def extract_text_from_word(uploaded_file):
    text = ""
    doc = docx.Document(uploaded_file)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text.strip()

# Function to check document fraud
def check_fraud(text):
    fraud_keywords = ["fake", "unauthorized", "invalid", "forged", "counterfeit"]
    for word in fraud_keywords:
        if word in text.lower():
            return "❌ This document appears to be fraudulent!"
    return "✅ This document seems legitimate."

# Function to generate answers using Local Mistral Model (Ollama)
def answer_question(question, document_text):
    prompt = f"Document: {document_text[:3000]}\n\nUser Question: {question}\nAnswer:"
    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# Streamlit UI
st.set_page_config(page_title="📜 AI Legal Document Assistant", layout="wide")
st.title("📜 AI-Powered Legal Document Chatbot")

# Sidebar File Upload
st.sidebar.header("Upload Your Legal Document")
uploaded_file = st.sidebar.file_uploader("Upload a PDF, JPG, PNG, or DOCX document", type=["pdf", "jpg", "png", "docx"])

if uploaded_file:
    document_text = ""

    # Determine file type and extract text accordingly
    if uploaded_file.type == "application/pdf":
        document_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type in ["image/jpeg", "image/png"]:
        document_text = extract_text_from_image(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        document_text = extract_text_from_word(uploaded_file)

    # Display Extracted Text
    st.write("### 📄 Extracted Text Preview:")
    st.text_area("Extracted Text", document_text[:1000] + "...", height=200)

    # Fraud detection
    st.write("### 🔍 Fraud Detection:")
    fraud_result = check_fraud(document_text)
    if "fraudulent" in fraud_result:
        st.error(fraud_result)
    else:
        st.success(fraud_result)

    # Summarization
    st.write("### 📑 Document Summary:")
    summary = answer_question("Summarize this document.", document_text)
    st.info(summary)

    # Q&A
    st.write("### 🤖 Ask Your Legal Question:")
    user_question = st.text_input("Enter your question:")
    if user_question:
        answer = answer_question(user_question, document_text)
        st.success(answer)

# Footer
st.markdown("---")
st.markdown("📌 **Note:** This AI tool is for informational purposes only and not a substitute for legal advice.")
##working well.
