import streamlit as st
import google.generativeai as genai

# Sæt siden op
st.set_page_config(page_title="SEO/Ads Møde-Butler", page_icon="🎯")
st.title("🎯 Møde-transskribering til SEO & Ads")

# API nøgle (Gør den fast eller lad kollegaer taste deres egen)
API_KEY = "AIzaSyDPlf38XCJjWCYGceLUnp99WP8Jh6_Fxjs"
genai.configure(api_key=API_KEY)

uploaded_file = st.file_uploader("Upload din mødeoptagelse", type=['wav', 'mp3', 'm4a'])

if uploaded_file:
    if st.button("Generér Referat ✨"):
        with st.spinner("Analyserer... Gemini læser din lydfil."):
            # Gem midlertidigt
            with open("temp.wav", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Gemini logik
            model = genai.GenerativeModel("gemini-1.5-flash")
            audio_api_file = genai.upload_file(path="temp.wav")
            
            prompt = "Lav et struktureret referat med fokus på SEO, Ads, ROAS og Action Items."
            response = model.generate_content([audio_api_file, prompt])
            
            st.success("Referat færdigt!")
            st.markdown(response.text)