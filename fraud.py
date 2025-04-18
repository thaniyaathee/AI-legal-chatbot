import streamlit as st
import ollama
from transformers import pipeline
import whisper
import requests
import fitz  # PyMuPDF for PDF extraction
import pytesseract  # OCR for extracting text from images
from PIL import Image  # Image processing
from langdetect import detect
from twilio.rest import Client

# 🌍 LocationIQ API (Free for 5000 requests/day)
LOCATIONIQ_API_KEY = "pk.72fc2356a1b5fe438bd77e6757cc094e"

# 🔍 OpenStreetMap API (No API Key Required)
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# 🎙 Load Whisper ASR Model for Speech Recognition
whisper_model = whisper.load_model("base")

# ⚖ Load Hugging Face Legal-BERT Model
legal_qa = pipeline("question-answering", model="nlpaueb/legal-bert-base-uncased")

# ✅ Set Tesseract path (Fix for Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ Load Hugging Face Summarization Model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# ✅ Twilio Credentials (Update These)
TWILIO_SID = "your_twilio_account_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE = "+1XXXXXXXXXX"  # Must be a Twilio **long code** (not a short code)
RECEIVER_PHONE = "+91XXXXXXXXXX"  # Ensure this number is **verified** on Twilio

# 🏛️ Sidebar Navigation
st.sidebar.title("🚔 Legal & Police Assistance")
page = st.sidebar.radio(
    "Select a Service",
    ["📜 Chat with AI", "🚔 Nearest Police Station", "📑 Document Checking", "🚨 Emergency Help / Complaint"]
)

# ✅ Function to Detect Language
def detect_language(text):
    try:
        lang = detect(text)
        return lang if lang in ["en", "ta"] else "en"  # Default to English if unsure
    except:
        return "en"

# --------------------------- 🚨 EMERGENCY HELP / COMPLAINT TO POLICE --------------------------------
if page == "🚨 Emergency Help / Complaint":
    st.title("📩 Police Complaint SMS System")

    # ✅ Function to Send SMS (Fixed for Twilio Long Code)
    def send_sms(complaint):
        try:
            client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"🚨 Police Complaint: {complaint}",
                from_=TWILIO_PHONE,  # Ensure this is a Twilio **long code**
                to=RECEIVER_PHONE  # Ensure this number is **verified** on Twilio
            )
            return f"✅ SMS sent successfully! Message SID: {message.sid}"
        except Exception as e:
            return f"❌ Error: {e}"

    # 📝 User Complaint Input
    complaint_text = st.text_area("Describe your complaint in detail:")

    # 🚨 Submit Complaint Button
    if st.button("🚨 Submit Complaint & Send SMS"):
        if complaint_text:
            response = send_sms(complaint_text)
            st.success(response)
        else:
            st.error("⚠️ Please enter a complaint before submitting!")

# --------------------------- ⚖ CHAT WITH AI --------------------------------
elif page == "📜 Chat with AI":
    st.title("⚖ AI-Powered Legal Chatbot")

    # 🏛️ Choose Perspective (Lawyer or Judge)
    perspective = st.radio("Choose AI Perspective:", ["Lawyer", "Judge"])

    # 🔊 Choose Input Mode
    query_type = st.radio("Select Input Mode:", ["Text", "Voice"])
    user_query = None

    if query_type == "Text":
        user_query = st.text_area("💬 Ask your legal question...")

    elif query_type == "Voice":
        uploaded_file = st.file_uploader("🎙 Upload Voice Query (WAV, MP3, M4A)", type=["wav", "mp3", "m4a"])
        if uploaded_file:
            with open("temp_audio.wav", "wb") as f:
                f.write(uploaded_file.read())
            user_query = whisper_model.transcribe("temp_audio.wav")["text"]
            st.success(f"📝 Transcribed Text: {user_query}")

    # ✅ Function to Get AI Response in the Correct Language
    def get_ai_response(query, perspective):
        detected_lang = detect_language(query)
        role_prompt = "தமிழில் பதிலளிக்கவும்: " if detected_lang == "ta" else f"Answer in English as a {perspective.lower()}: "

        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": role_prompt + query}]
        )
        return response["message"]["content"]

    # ✅ Function to Get Legal Reference (Using Legal-BERT)
    def get_legal_reference(query):
        context = "Legal cases and precedents data."
        return legal_qa(question=query, context=context)["answer"]

    # ✅ Submit Button
    if st.button("Submit Query"):
        if user_query:
            with st.spinner("🧠 Thinking..."):
                ai_response = get_ai_response(user_query, perspective)
                legal_reference = get_legal_reference(user_query)

            # 💬 Display AI Response
            st.subheader("🤖 AI Response")
            st.write(ai_response)

            # 📜 Display Legal Reference
            st.subheader("📜 Legal Reference")
            st.write(legal_reference)
        else:
            st.warning("⚠️ Please enter a query before submitting!")

# --------------------------- 📑 DOCUMENT CHECKING --------------------------------
elif page == "📑 Document Checking":
    st.title("📑 AI-Powered Document Verification")

    uploaded_file = st.file_uploader("📂 Upload a PDF, JPG, or PNG document", type=["pdf", "jpg", "png"])

    def extract_text_from_pdf(uploaded_file):
        text = ""
        try:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in doc:
                text += page.get_text("text") + "\n"
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"
        return text.strip()

    def extract_text_from_image(uploaded_file):
        try:
            image = Image.open(uploaded_file)
            text = pytesseract.image_to_string(image)
        except Exception as e:
            return f"Error extracting text from image: {str(e)}"
        return text.strip()

    def generate_summary(document_text):
        if not document_text:
            return "⚠️ No text found in the document to summarize."
        try:
            summary_result = summarizer(document_text[:4000], max_length=200, min_length=50, do_sample=False)
            return summary_result[0]['summary_text']
        except Exception as e:
            return f"⚠️ Error generating summary: {str(e)}"

    if uploaded_file:
        document_text = extract_text_from_pdf(uploaded_file) if uploaded_file.type == "application/pdf" else extract_text_from_image(uploaded_file)
        st.subheader("📄 Extracted Text Preview")
        st.text_area("Extracted Text", document_text[:1000] + "...", height=200)

        st.subheader("📑 Document Summary")
        summary = generate_summary(document_text)
        st.info(summary)

# --------------------------- 📌 FOOTER --------------------------------
st.markdown("---")
st.markdown("📌 **Note:** AI is for informational purposes only and not a substitute for legal advice.")
