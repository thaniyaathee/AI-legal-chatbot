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

# ✅ Twilio Credentials (Replace with actual credentials)
TWILIO_SID = "ACcb6f19ace56db44d5264360a4576e9ce"
TWILIO_AUTH_TOKEN = "87281ae02aca42b39969a3666aa36668"
TWILIO_PHONE = "+18283581231"
RECEIVER_PHONE = "+918015766955"  # Ensure this number is verified on Twilio

# 🏛 Sidebar Navigation
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

# --------------------------- ⚖ CHAT WITH AI --------------------------------
if page == "📜 Chat with AI":
    st.title("⚖ AI-Powered Legal Chatbot")

    # 🏛 Choose Perspective (Lawyer or Judge)
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
            st.warning("⚠ Please enter a query before submitting!")

# --------------------------- 🚔 NEAREST POLICE STATION --------------------------------
elif page == "🚔 Nearest Police Station":
    st.title("🚔 Find Your Nearest Police Station")

    # 🏠 User Input
    area = st.text_input("🏠 Enter Your Area, City, or PIN Code:", placeholder="Eg: Tambaram, Chennai, 600119")

    # ✅ Function to Fetch Police Station
    def get_police_station(area):
        params = {"q": f"police station {area}, Tamil Nadu, India", "format": "json", "limit": 1}
        response = requests.get(NOMINATIM_URL, params=params, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return data["display_name"], data["lat"], data["lon"]
        return None, None, None

    # 🔍 Find Police Station
    if st.button("🔍 Find Nearest Police Station"):
        if area:
            station_name, lat, lon = get_police_station(area)

            if station_name:
                st.success(f"🚔 Nearest Police Station: {station_name}")
                st.write(f"📍 *Latitude:* {lat}, *Longitude:* {lon}")
                st.map(data={"lat": [float(lat)], "lon": [float(lon)]})
            else:
                st.error("⚠ No police station found for this location. Try another area.")
        else:
            st.warning("⚠ Please enter a valid area!")

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
            return "⚠ No text found in the document to summarize."
        try:
            summary_result = summarizer(document_text[:4000], max_length=200, min_length=50, do_sample=False)
            return summary_result[0]['summary_text']
        except Exception as e:
            return f"⚠ Error generating summary: {str(e)}"

    if uploaded_file:
        document_text = extract_text_from_pdf(uploaded_file) if uploaded_file.type == "application/pdf" else extract_text_from_image(uploaded_file)
        st.subheader("📄 Extracted Text Preview")
        st.text_area("Extracted Text", document_text[:1000] + "...", height=200)
        st.subheader("📑 Document Summary")
        summary = generate_summary(document_text)
        st.info(summary)

# --------------------------- 🚨 EMERGENCY HELP / COMPLAINT --------------------------------
elif page == "🚨 Emergency Help / Complaint":
    st.title("📩 Police Complaint SMS System")

    def send_sms(complaint):
        try:
            client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(body=f"Complaint Received: {complaint}", from_=TWILIO_PHONE, to=RECEIVER_PHONE)
            return f"✅ SMS sent successfully! Message SID: {message.sid}"
        except Exception as e:
            return f"❌ Error: {e}"

    complaint_text = st.text_area("Describe your complaint in detail:")
    if st.button("Submit Complaint & Send SMS"):
        if complaint_text:
            response = send_sms(complaint_text)
            st.success(response)
        else:
            st.error("⚠ Please enter a complaint before submitting!")
elif page == "🎤 Talk with AI":
    st.title("🎤 AI-Powered Speech-to-Speech Assistant")

    # 🔹 Initialize Offline Text-to-Speech Engine (Fixed)
    def text_to_speech(text):
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)  # Adjust speech speed
        engine.say(text)
        engine.runAndWait()

    # ✅ AI Function (Generate AI Answer)
    def generate_ai_response(prompt):
        try:
            response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
            return response["message"]["content"]
        except Exception as e:
            return f"⚠ AI Error: {str(e)}"

    # ✅ Speech-to-Text Function (Recognize Speech)
    def recognize_speech():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Speak Now...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                text = recognizer.recognize_google(audio).strip().lower()
                return text
            except sr.WaitTimeoutError:
                return "❌ No voice detected. Try again."
            except sr.UnknownValueError:
                return "❌ Could not understand the speech."
            except sr.RequestError:
                return "❌ Speech recognition service unavailable."

    # ✅ General AI Assistant Logic
    def process_user_input(user_input):
        user_input = user_input.lower()

        # Greetings & Small Talk
        if user_input in ["hi", "hello", "hey"]:
            return "👋 Hello! How can I assist you today?"
        elif "how are you" in user_input:
            return "😊 I'm doing great! How can I help you?"
        elif "bye" in user_input:
            return "👋 Goodbye! Stay safe!"

        # If it's a general query, send it to Llama 3
        return generate_ai_response(user_input)

    # 🎤 Continuous Voice Interaction
    def start_conversation():
        while True:
            user_input = recognize_speech()
            if not user_input or "❌" in user_input:
                continue  # Keep listening if no valid speech is detected

            st.write(f"🎤 Recognized Speech: {user_input}")

            if "bye" in user_input.lower():
                text_to_speech("Goodbye! Have a great day!")
                st.success("👋 Conversation Ended.")
                break

            with st.spinner("Thinking..."):
                ai_response = process_user_input(user_input)
                st.write(f"🤖 AI Answer: {ai_response}")

            # Speak AI response
            text_to_speech(ai_response)

    st.subheader("🎤 Speak Your Query (Say 'bye' to exit)")
    if st.button("🎙 Start Conversation"):
        start_conversation()

    st.sidebar.header("⚡ Features")
    st.sidebar.write("✅ Interactive AI Chatbot")
    st.sidebar.write("✅ Voice-controlled Assistant")
    st.sidebar.write("✅ Offline Text-to-Speech (TTS)")
    st.sidebar.write("✅ Uses Open-Source AI (Llama 3)")
####st.markdown("📌 *Note:* AI is for informational purposes only and not a substitute for legal advice.")
