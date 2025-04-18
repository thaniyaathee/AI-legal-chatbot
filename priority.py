import streamlit as st
from transformers import pipeline
from twilio.rest import Client

# ✅ Replace with your actual Twilio credentials
TWILIO_SID = "ACcb6f19ace56db44d5264360a4576e9ce"
TWILIO_AUTH_TOKEN = "87281ae02aca42b39969a3666aa36668"
TWILIO_PHONE = "+18283581231"# Your Twilio phone number
POLICE_PHONE = "+918015766955"  # Police Station's phone number

# ✅ Load Pre-trained Model for Text Classification
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# ✅ IPC Sections & Urgency Mapping
ipc_sections = {
    "High Urgency": ["302 (Murder)", "376 (Rape)", "307 (Attempt to Murder)", "395 (Dacoity)", "121 (Waging War)"],
    "Medium Urgency": ["379 (Theft)", "354 (Outraging Modesty of Women)", "420 (Cheating)", "506 (Criminal Intimidation)"],
    "Low Urgency": ["323 (Simple Hurt)", "427 (Mischief)", "509 (Word/Gesture to Insult Women)"],
}

# ✅ Classify Complaint Based on Urgency
def classify_urgency(complaint):
    categories = ["High Urgency", "Medium Urgency", "Low Urgency"]
    result = classifier(complaint, candidate_labels=categories)

    urgency_level = result["labels"][0]  # Highest confidence label
    urgency_scores = {label: round(score, 2) for label, score in zip(result["labels"], result["scores"])}

    # Retrieve IPC Sections based on classification
    related_ipc_sections = ipc_sections.get(urgency_level, ["Unknown"])

    return urgency_level, related_ipc_sections, urgency_scores

# ✅ Send Complaint via SMS (Twilio) with Debugging
def send_sms(complaint, urgency, ipc_details, urgency_scores):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message_body = (
            f"🚨 New Complaint Filed:\n"
            f"{complaint}\n\n"
            f"⚖ IPC Sections: {', '.join(ipc_details)}\n"
            f"🔴 Urgency Level: {urgency}\n"
            f"📊 Scores: {urgency_scores}\n"
        )

        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE,
            to=POLICE_PHONE
        )

        # ✅ Debugging: Log Twilio response
        st.write(f"📩 Twilio Response: {message.sid}")

        return f"✅ Complaint sent successfully! Message SID: {message.sid}"
    except Exception as e:
        st.error(f"❌ Error sending complaint: {str(e)}")
        return f"❌ Error sending complaint: {str(e)}"

# ✅ Streamlit UI
st.title("🚔 AI-Powered Police Complaint Classifier")
st.write("🔹 Automatically classifies complaints based on **IPC Sections** and **Urgency Level**.")

# ✅ User Input (Complaint)
complaint_text = st.text_area("📜 Describe your complaint:")

if st.button("🚨 Check Urgency Level & Send SMS"):
    if complaint_text:
        urgency, ipc_details, urgency_scores = classify_urgency(complaint_text)

        # Display Urgency Level
        if urgency == "High Urgency":
            st.error(f"🚨 Urgency: {urgency} - Immediate action needed!")
        elif urgency == "Medium Urgency":
            st.warning(f"⚠ Urgency: {urgency} - Action required soon.")
        else:
            st.success(f"🟢 Urgency: {urgency} - Can be handled later.")

        st.write(f"⚖ **Relevant IPC Sections:** {', '.join(ipc_details)}")
        st.write(f"📊 **Urgency Scores:** {urgency_scores}")

        # ✅ Send SMS to Police Station
        response = send_sms(complaint_text, urgency, ipc_details, urgency_scores)
        st.success(response)
    else:
        st.error("❌ Please enter a complaint before submitting.")

st.markdown("---")
st.write("🔹 **Uses Open-Source AI (Hugging Face) for IPC-Based Complaint Classification & SMS Filing**")



##A man forcibly entered my house and tried to attack me.