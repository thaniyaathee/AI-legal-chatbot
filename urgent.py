import re
import torch
import streamlit as st
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from twilio.rest import Client  # Import Twilio

# Load Pretrained LLM Model for Sentiment Analysis
model_name = "distilbert-base-uncased-finetuned-sst-2-english"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Twilio API Credentials (replace with your own)
TWILIO_ACCOUNT_SID = "ACcb6f19ace56db44d5264360a4576e9ce"
TWILIO_AUTH_TOKEN = "87281ae02aca42b39969a3666aa36668"
TWILIO_PHONE_NUMBER = "+18283581231"  # Your Twilio number
POLICE_STATION_NUMBER = "+918015766955"  # Replace with actual police station number

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Weighted Keywords for Urgency Detection
keyword_weights = {
    "help": 1, "important": 2, "urgent": 3, "critical": 4, "danger": 5,
    "attack": 7, "threat": 6, "assault": 8, "emergency": 9, "ASAP": 10
}

# Urgency Levels with Colors
urgency_levels = [
    (1, 3, "Low Priority", "#A7F3D0", "General Inquiry - No Immediate Action Needed"),
    (4, 6, "Medium Priority", "#FDE68A", "Moderate Concern - Review Required"),
    (7, 10, "High Priority", "#FCA5A5", "Emergency - Immediate Police Action Needed")
]

# Function to check and weight urgent keywords
def check_urgent_keywords(text):
    words = text.lower().split()
    return sum(keyword_weights[word] for word in words if word in keyword_weights)

# Function to analyze sentiment using LLM
def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment_score = probs[0][1].item() * 5  # Adjusted weight for sentiment
    return sentiment_score

# Function to calculate urgency score dynamically
def predict_urgency(text):
    keyword_score = check_urgent_keywords(text)  # Weighted keyword score
    sentiment_score = analyze_sentiment(text)  # Sentiment analysis
    text_length_factor = max(1, len(text.split()) / 20)  # Normalize urgency based on text length
    
    raw_score = (keyword_score + sentiment_score) / text_length_factor
    scaled_score = min(10, max(1, int(raw_score)))  # Scale between 1-10
    
    for min_val, max_val, level, color, action in urgency_levels:
        if min_val <= scaled_score <= max_val:
            return {"Urgency Score": scaled_score, "Urgency Level": level, "Color": color, "Action": action}
    
    return {"Urgency Score": scaled_score, "Urgency Level": "Unknown", "Color": "#FFFFFF", "Action": "Review Required"}

# Function to send SMS to the police station
def send_sms_to_police(complaint, urgency_level):
    message_body = f"New Police Complaint:\nUrgency: {urgency_level}\nDetails: {complaint}"
    message = client.messages.create(
        body=message_body,
        from_=TWILIO_PHONE_NUMBER,
        to=POLICE_STATION_NUMBER  # Change this number dynamically if needed
    )
    return message.sid

# Streamlit Chatbot UI
st.title("Police Complaint Registration Chatbot")
st.write("This chatbot categorizes the urgency of complaints and advises victims on the next steps.")

user_input = st.text_area("Describe your complaint:")

if st.button("Register Complaint"):
    if user_input:
        result = predict_urgency(user_input)
        st.markdown(f"### Urgency Level: {result['Urgency Level']}")
        st.markdown(f"#### Urgency Score: {result['Urgency Score']}")
        st.markdown(f"#### Suggested Action: {result['Action']}")
        st.markdown(f'<div style="background-color:{result["Color"]};padding:10px;border-radius:5px;">Urgency Level: {result["Urgency Level"]}</div>', unsafe_allow_html=True)

        # If the urgency is high, send SMS to the police
        if result["Urgency Level"] == "High Priority":
            sms_status = send_sms_to_police(user_input, result["Urgency Level"])
            st.success(f"🚨 Complaint sent to the police station (Reference ID: {sms_status})")
        else:
            st.info("✅ Complaint registered but no immediate police action required.")
    else:
        st.warning("Please enter a complaint to analyze.")