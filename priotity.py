import streamlit as st
import faiss
import pickle
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from langchain.llms import LlamaCpp
from twilio.rest import Client

# ✅ Load Llama Model (Local)
LLAMA_PATH = "models/llama-3.1.gguf"  # Path to your local Llama model
llm = LlamaCpp(model_path=LLAMA_PATH, max_tokens=512)

# ✅ Load & Process Legal Document (Word File with IPC Sections)
DATA_FILE = "D:\personal(T)\genetrix_hackathon\priority.docx"

def load_rag_data():
    loader = UnstructuredFileLoader(DATA_FILE)
    data = loader.load()
    
    # Split text into smaller chunks for embedding
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(data)
    
    # Create embeddings using HuggingFace (Open-source)
    embeddings = HuggingFaceEmbeddings()
    vectorstore = FAISS.from_documents(texts, embeddings)
    
    return vectorstore

# ✅ Load or Train RAG Model
if os.path.exists("ipc_vectorstore.pkl"):
    with open("ipc_vectorstore.pkl", "rb") as f:
        vectorstore = pickle.load(f)
else:
    vectorstore = load_rag_data()
    with open("ipc_vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)

# ✅ Function to Retrieve IPC Section from User Complaint
def get_ipc_section(complaint):
    results = vectorstore.similarity_search(complaint, k=1)
    return results[0].page_content if results else "No matching IPC section found."

# ✅ Function to Classify Complaint Urgency
def classify_urgency(ipc_section):
    high_urgency = ["302", "307", "363", "376"]
    medium_urgency = ["392", "498A", "420"]
    
    for sec in high_urgency:
        if sec in ipc_section:
            return "🚨 High Urgency - Immediate police action required."
    for sec in medium_urgency:
        if sec in ipc_section:
            return "⚠ Medium Urgency - Action needed, but not immediate."
    return "🟢 Low Urgency - Can be addressed later."

# ✅ Function to Send Complaint via Twilio
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE = "+1234567890"
RECEIVER_PHONE = "+919876543210"  # Police station number

def send_sms(complaint, urgency, ipc_section):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message_body = f"🚔 Complaint Received: {complaint}\n\n📜 IPC Section: {ipc_section}\n⚠ Urgency: {urgency}"
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE,
            to=RECEIVER_PHONE
        )
        return f"✅ SMS Sent Successfully! Message SID: {message.sid}"
    except Exception as e:
        return f"❌ Error: {e}"

# ✅ Streamlit UI
st.title("🚔 AI-Powered Police Complaint System")

# Complaint Input
complaint_text = st.text_area("📌 Describe your complaint:")

if st.button("🔍 Analyze Complaint & Send SMS"):
    if complaint_text:
        # Retrieve IPC Section
        ipc_section = get_ipc_section(complaint_text)
        # Classify Urgency
        urgency_level = classify_urgency(ipc_section)
        # Display Results
        st.write(f"📜 **Identified IPC Section:** {ipc_section}")
        st.write(f"⚠ **Urgency Level:** {urgency_level}")
        # Send SMS
        response = send_sms(complaint_text, urgency_level, ipc_section)
        st.success(response)
    else:
        st.error("❌ Please enter a complaint before submitting.")
