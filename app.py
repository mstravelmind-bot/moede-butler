import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import time

# 1. Konfiguration af siden
st.set_page_config(page_title="SEO/Ads Møde-Butler", page_icon="🎯")
st.title("🎯 SEO & Ads Møde-Butler")

# 2. Sikkerhed: Hent API-nøgle fra Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ API-nøgle mangler! Gå til Settings -> Secrets i Streamlit og tilføj GEMINI_API_KEY")
    st.stop()

# 3. Brugergrænseflade: Optagelse og Upload
st.write("Optag mødet live eller upload en lydfil for at få et struktureret referat.")
st.divider()

tab1, tab2 = st.tabs(["🔴 Optag Live", "📁 Upload Fil"])
audio_bytes = None

with tab1:
    st.subheader("Optag direkte")
    audio_record = mic_recorder(
        start_prompt="🔴 Start optagelse",
        stop_prompt="⏹️ Stop og gem",
        just_once=False,
        use_container_width=True,
        key="recorder"
    )
    if audio_record:
        audio_bytes = audio_record['bytes']
        st.audio(audio_bytes, format="audio/wav")

with tab2:
    st.subheader("Upload lydfil")
    uploaded_file = st.file_uploader("Vælg fil (mp3, wav, m4a)", type=['mp3', 'wav', 'm4a'])
    if uploaded_file:
        audio_bytes = uploaded_file.getbuffer()
        st.audio(audio_bytes)

# 4. Behandling af lyd med Gemini
if audio_bytes:
    st.divider()
    if st.button("Generér Referat ✨", type="primary", use_container_width=True):
        with st.spinner("Gemini transskriberer og analyserer mødet..."):
            try:
                # Gem lyden midlertidigt
                temp_filename = "temp_audio.wav"
                with open(temp_filename, "wb") as f:
                    f.write(audio_bytes)
                
                # Upload til Gemini API
                st.info("Uploader fil til AI-server...")
                audio_file = genai.upload_file(path=temp_filename)
                
                # Vent på at filen er færdigbehandlet af Google
                while audio_file.state.name == "PROCESSING":
                    time.sleep(2)
                    audio_file = genai.get_file(audio_file.name)
                
                if audio_file.state.name == "FAILED":
                    st.error("Lydbehandling fejlede hos Google.")
                    st.stop()

                # Vælg model og kør prompt
                # Du kan ændre "gemini-1.5-flash" til "gemini-3.1-pro-preview" herunder
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                prompt = """Du er en specialist i SEO og Google Ads. 
                Lav et detaljeret og struktureret referat af dette møde.
                
                Brug denne struktur:
                - Overskrifter for hvert emne (fx Performance overview, Budget, Tracking)
                - Bulletpoints med specifikke indsigter og tal (fx ROAS, Impression share)
                - En sektion til sidst med 'Action Items' med [ ] tjekbokse.
                
                Vær teknisk præcis omkring Google Ads og SEO termer."""
                
                response = model.generate_content([audio_file, prompt])
                
                # Vis resultatet
                st.subheader("📝 Mødereferat")
                st.markdown(response.text)
                
                # Download knap
                st.download_button(
                    label="Download som .txt",
                    data=response.text,
                    file_name="moedereferat.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Der opstod en fejl under processeringen: {e}")

# Instruktion
with st.expander("Brugsanvisning"):
    st.write("Husk at give browseren adgang til din mikrofon. Ved meget lange møder anbefales upload af fil.")
