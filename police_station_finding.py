import streamlit as st
import requests

# 🔍 OpenStreetMap Nominatim API (No API Key Required)
def get_police_station_osm(area):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"police department near {area}, Tamil Nadu, India",
        "format": "json",
        "limit": 1
    }
    
    response = requests.get(base_url, params=params, headers={"User-Agent": "Mozilla/5.0"})
    
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return data["display_name"], data["lat"], data["lon"]
    return None, None, None

# 🌍 LocationIQ API (Requires Free API Key)
LOCATIONIQ_API_KEY = "pk.72fc2356a1b5fe438bd77e6757cc094e"

def get_police_station_locationiq(area):
    base_url = f"https://us1.locationiq.com/v1/search.php"
    params = {
        "key": LOCATIONIQ_API_KEY,
        "q": f"police station {area}, Tamil Nadu, India",
        "format": "json",
        "limit": 1
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return data["display_name"], data["lat"], data["lon"]
    return None, None, None

# 🌟 Streamlit UI
st.title("🚔 Find Nearest Police Station (Improved)")

# User Input
area = st.text_input("🏠 Enter Your Area, City, or PIN Code:", placeholder="Eg: Tambaram, Chennai, 600119")

if st.button("🔍 Find Police Station"):
    if area:
        # Try OSM First
        station_name, lat, lon = get_police_station_osm(area)

        # If OSM Fails, Try LocationIQ
        if not station_name:
            station_name, lat, lon = get_police_station_locationiq(area)

        # Display Result
        if station_name:
            st.success(f"**🚔 Nearest Police Station: {station_name}**")
            st.write(f"📍 **Latitude:** {lat}, **Longitude:** {lon}")
            st.map(data={"lat": [float(lat)], "lon": [float(lon)]})
        else:
            st.error("⚠️ No police station found for this location. Try another area.")
    else:
        st.warning("⚠️ Please enter a valid area!")

# Footer
st.markdown("---")
st.markdown("📌 **Note:** This uses OpenStreetMap Nominatim API and LocationIQ (5,000 free searches/day).")
##LOCATIONIQ_API_KEY =pk.72fc2356a1b5fe438bd77e6757cc094e