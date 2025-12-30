import streamlit as st
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="AI Travel Planner", page_icon="🗺️")
st.title("🗺️ AI Travel Planner")

# --- AUTO-LOAD KEY ---
# This checks if the secret file exists
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.sidebar.success("API Key loaded automatically! 🟢")
else:
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")

# Sidebar Inputs
with st.sidebar:
    st.header("Trip Details")
    destination = st.text_input("Destination", placeholder="e.g., Paris")
    days = st.slider("Days", 1, 14, 3)
    budget = st.select_slider("Budget", options=["Cheap", "Moderate", "Luxury"])

# --- UNIVERSAL MODEL FINDER ---
def find_best_model(api_key):
    genai.configure(api_key=api_key)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name or 'pro' in m.name:
                    return genai.GenerativeModel(m.name)
        return None
    except:
        return None

# --- MAIN APP ---
if st.button("Plan Trip"):
    if not api_key:
        st.error("No API Key found. Please check your secrets.toml file.")
    elif not destination:
        st.warning("Please enter a destination.")
    else:
        with st.spinner("Plotting your course..."):
            model = find_best_model(api_key)
            if model:
                prompt = f"""
                Plan a {days}-day trip to {destination} on a {budget} budget.
                1. Daily itinerary with costs.
                2. AT THE END: List 5 main locations exactly like this:
                   MAP: Location Name, Latitude, Longitude
                """
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    
                    # Map Logic
                    map_points = []
                    for line in response.text.split('\n'):
                        if line.strip().startswith("MAP:"):
                            parts = line.split(',')
                            if len(parts) == 3:
                                try:
                                    map_points.append({'lat': float(parts[1]), 'lon': float(parts[2])})
                                except: continue
                    if map_points:
                        st.map(pd.DataFrame(map_points))
                except Exception as e:
                    st.error(f"Error: {e}")