import streamlit as st
import ollama
from transformers import pipeline
import whisper
import os
from langdetect import detect

# Load Whisper model for voice input
whisper_model = whisper.load_model("base")

# Load Hugging Face Legal-BERT model for legal references
legal_qa = pipeline("question-answering", model="nlpaueb/legal-bert-base-uncased")

# Streamlit UI setup
st.set_page_config(page_title="AI Legal Chatbot", layout="wide")
st.title("⚖ AI-Powered Lawyer & Judge Assistant")

# Sidebar settings
st.sidebar.header("Chatbot Settings")
perspective = st.sidebar.radio("Select Perspective:", ["Lawyer", "Judge"])
st.sidebar.info("This chatbot provides legal insights from both a *lawyer's* and *judge's* perspective.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input (Text or Voice)
query_type = st.radio("Choose Input Mode:", ["Text", "Voice"])
user_query = None

if query_type == "Text":
    user_query = st.chat_input("Ask your legal question...")

elif query_type == "Voice":
    uploaded_file = st.file_uploader("Upload Voice Query", type=["wav", "mp3", "m4a"])
    if uploaded_file:
        audio_path = "temp_audio.wav"
        with open(audio_path, "wb") as f:
            f.write(uploaded_file.read())
        user_query = whisper_model.transcribe(audio_path)["text"]
        st.success(f"Transcribed Text: {user_query}")

# Function to detect language
def detect_language(text):
    try:
        lang = detect(text)
        return lang if lang in ["en", "ta"] else "en"  # Default to English if unsure
    except:
        return "en"

# Function to get AI response
def get_ai_response(query, perspective, lang):
    if lang == "ta":
        role_prompt = "தமிழில் பதிலளிக்கவும். "  # Answer in Tamil
    else:
        role_prompt = "Answer in English as a lawyer: " if perspective == "Lawyer" else "Answer in English as a judge: "

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": role_prompt + query}]
    )
    return response["message"]["content"]

# Function to get legal reference using Legal-BERT
def get_legal_reference(query, lang):
    context = "Legal cases and precedents data." if lang == "en" else "சட்ட வழக்குகள் மற்றும் முன்னோடிகள் பற்றிய தகவல்."
    return legal_qa(question=query, context=context)["answer"]

# Process user query
if user_query:
    # Detect language
    detected_lang = detect_language(user_query)

    # Append user input to chat history
    st.session_state.messages.append({"role": "user", "content": f"*You:* {user_query}"})

    # Display user query in chat
    with st.chat_message("user"):
        st.markdown(f"*You:* {user_query}")

    # Generate AI response
    with st.spinner("Generating response..."):
        ai_response = get_ai_response(user_query, perspective, detected_lang)
        legal_reference = get_legal_reference(user_query, detected_lang)

    # Append AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": f"*AI Response:*\n{ai_response}"})
    st.session_state.messages.append({"role": "assistant", "content": f"📜 Legal Reference:\n{legal_reference}"})

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(f"*AI Response:*\n{ai_response}")

    # Display Legal Reference
    with st.chat_message("assistant"):
        st.markdown(f"📜 Legal Reference:\n{legal_reference}")

# Footer
st.markdown("---")
st.markdown("📌 *Note:* This AI is for informational purposes only and not a substitute for legal advice.")
##திருட்டுக்கு என்ன தண்டனை?
##ok
##cd "D:\personal(T)\genetrix_hackathon"