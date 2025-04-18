import pandas as pd
import streamlit as st

# Load CSV file with encoding fix
@st.cache_data
def load_data():
    csv_file = "D:\personal(T)\genetrix_hackathon\Police_Station_Location_Contact_Number.csv"  # Update with your actual file name
    return pd.read_csv(csv_file, encoding="ISO-8859-1")

# Load data
df = load_data()

# Streamlit UI
st.title("🚔 Police Station Contact Finder")

# Sidebar Search
st.sidebar.header("🔍 Search for Police Contacts")
district_filter = st.sidebar.text_input("Enter District Name (Required to Show Data):")
station_filter = st.sidebar.text_input("Enter Police Station Name (Optional):")

# Apply search conditions
if district_filter:
    filtered_df = df[df["City Name"].str.contains(district_filter, case=False, na=False)]

    if station_filter:
        filtered_df = filtered_df[filtered_df["Police Station Name"].str.contains(station_filter, case=False, na=False)]
    
    if not filtered_df.empty:
        st.write(f"Showing {len(filtered_df)} result(s):")
        st.table(filtered_df)
    else:
        st.warning("No matching police stations found.")
else:
    st.warning("Enter a District Name to view police contact details.")
