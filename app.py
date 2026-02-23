import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# 1. Konfiguration
st.set_page_config(page_title="SEO/Ads Møde-Butler", page_icon="🎯")
st.title("🎯 SEO & Ads Møde-Butler")

# 2. SIKKERHED: Hent nøglen fra Streamlit Secrets
# Vi skriver ALDRIG nøglen herinde igen
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API-nøgle mangler i Streamlit Secrets!")
    st.stop()

# 3. Mikrofon & Upload
st.subheader("Optag eller upload")
audio_record = mic_recorder(start_prompt="🔴 Start optagelse", stop_prompt="⏹️ Stop")
uploaded_file = st.file_uploader("Eller upload fil", type=['wav', 'mp3', 'm4a'])

audio_data = None
if audio_record:
    audio_data = audio_record['bytes']
elif uploaded_file:
    audio_data = uploaded_file.getbuffer()

# 4. Gemini 3.1 Pro logik
if audio_data:
    if st.button("Generér Referat ✨"):
        with st.spinner("Analyserer med Gemini 3.1 Pro..."):
            with open("temp.wav", "wb") as f:
                f.write(audio_data)
            
            # Vi bruger den nyeste model du så i AI Studio
            model = genai.GenerativeModel("gemini-3.1-pro-preview")
            audio_file = genai.upload_file(path="temp.wav")
            
            prompt = "Lav et SEO/Ads mødereferat med Performance, Budget og Action Items."
            response = model.generate_content([audio_file, prompt])
            
            st.markdown(response.text)
