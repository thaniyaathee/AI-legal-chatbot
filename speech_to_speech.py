import streamlit as st
import speech_recognition as sr
import ollama  # Use open-source Llama 3 model
import pyttsx3  # Offline TTS

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

# 🔹 Streamlit UI
st.set_page_config(page_title="🎤 AI Speech Assistant", layout="wide")
st.title("🎤 AI-Powered Speech-to-Speech Assistant")

st.subheader("🎤 Speak Your Query (Say 'bye' to exit)")
if st.button("🎙 Start Conversation"):
    start_conversation()    

st.sidebar.header("⚡ Features")
st.sidebar.write("✅ Interactive AI Chatbot")
st.sidebar.write("✅ Voice-controlled Assistant")
st.sidebar.write("✅ Offline Text-to-Speech (TTS)")
st.sidebar.write("✅ Uses Open-Source AI (Llama 3)")
