import streamlit as st
import requests
from twilio.rest import Client

# Twilio API Credentials
TWILIO_SID = "ACcb6f19ace56db44d5264360a4576e9ce"
TWILIO_AUTH_TOKEN = "87281ae02aca42b39969a3666aa36668"
TWILIO_PHONE = "+18283581231"

# LocationIQ API Key
LOCATIONIQ_API_KEY = "pk.72fc2356a1b5fe438bd77e6757cc094e"

# Function to fetch nearest police station contact
def get_nearest_police_station(area):
    base_url = f"https://us1.locationiq.com/v1/search.php?key={LOCATIONIQ_API_KEY}&q={area} police station&format=json"
    response = requests.get(base_url)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            station_name = data[0]['display_name']
            lat, lon = data[0]['lat'], data[0]['lon']
            return station_name, lat, lon
        else:
            return None, None, None
    return None, None, None

# Function to send SMS to nearest police station
def send_sms(complaint, station_name):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"🚔 Police Complaint:\n{complaint}\n📍 Location: {station_name}",
            from_=TWILIO_PHONE,
            to="+918015766955"  # Replace with the police station's number 8015844922
        )
        return f"✅ Complaint sent to {station_name}! SMS SID: {message.sid}"
    except Exception as e:
        return f"❌ Error sending SMS: {e}"

# Streamlit UI
st.title("📩 Police Complaint Filing System")

# User inputs their area
user_area = st.text_input("🏠 Enter your area, city, or PIN code:")

if user_area:
    station_name, lat, lon = get_nearest_police_station(user_area)

    if station_name:
        st.success(f"✅ Nearest Police Station: {station_name}")
        st.map(data=[{"lat": float(lat), "lon": float(lon)}])  # Show location on map
    else:
        st.error("⚠️ No police station found! Try another area.")

# Complaint input field
complaint_text = st.text_area("✍️ Describe your complaint in detail:")

# Submit Complaint
if st.button("📩 Submit Complaint & Send SMS"):
    if complaint_text and station_name:
        response = send_sms(complaint_text, station_name)
        st.success(response)
    else:
        st.error("⚠️ Enter a valid area and complaint before submitting.")
##not working properly