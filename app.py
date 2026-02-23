import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder
import time

# 1. Konfiguration af siden (SEO & Ads fokus)
st.set_page_config(page_title="SEO/Ads Møde-Butler", page_icon="🎯", layout="centered")

st.title("🎯 SEO & Ads Møde-Butler")
st.write("Optag mødet live eller upload en fil for at få et struktureret referat.")

# 2. SIKKERHED: Hent API-nøgle fra Streamlit Secrets
# Dette forhindrer "API key leaked" fejl, da nøglen ikke står i koden.
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ API-nøgle mangler! Gå til 'Manage app' -> 'Settings' -> 'Secrets' og tilføj din nøgle.")
    st.stop()

# 3. Brugergrænseflade: Tabs til Optagelse eller Upload
st.divider()
tab1, tab2 = st.tabs(["🔴 Optag Live", "📁 Upload Fil"])
audio_bytes = None

with tab1:
    st.subheader("Optag direkte")
    st.write("Klik for at starte optagelsen via din mikrofon.")
    # Mikrofon-komponenten
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
    uploaded_file = st.file_uploader("Vælg en fil (mp3, wav, m4a)", type=['mp3', 'wav', 'm4a'])
    if uploaded_file:
        audio_bytes = uploaded_file.getbuffer()
        st.audio(audio_bytes)

# 4. Processering med Gemini
if audio_bytes:
    st.divider()
    if st.button("Generér Referat ✨", type="primary", use_container_width=True):
        with st.spinner("Gemini transskriberer og analyserer mødet..."):
            try:
                # Gem lyden midlertidigt som en fil til upload
                temp_filename = "temp_audio.wav"
                with open(temp_filename, "wb") as f:
                    f.write(audio_bytes)
                
                # Upload til Gemini File API
                audio_file = genai.upload_file(path=temp_filename)
                
                # VIGTIGT: Vent på at Google har færdigbehandlet lyden
                while audio_file.state.name == "PROCESSING":
                    time.sleep(2)
                    audio_file = genai.get_file(audio_file.name)
                
                if audio_file.state.name == "FAILED":
                    st.error("Lydbehandling fejlede hos Google.")
                    st.stop()

                # Vælg model (Flash er lynhurtig til transskribering)
                model = genai.GenerativeModel("gemini-1.5-flash-latest")
                
                # Din skræddersyede SEO/Ads prompt
                prompt = """Du er en specialist i SEO og Google Ads. 
                Baseret på denne lydfil, skal du lave et detaljeret og struktureret referat.
                
                Strukturen SKAL være:
                - Overskrifter for hvert emne (fx Performance overview, Budget, PMax, Tracking)
                - Bulletpoints med specifikke indsigter og tal (fx ROAS, Impression share, konverteringer)
                - En sektion til sidst kaldet 'Action Items' med tjekbokse [ ]
                
                Vær meget opmærksom på tekniske termer som GTM, Enhanced Conversions, Search Console og kampagne-typer.
                """
                
                # Generér indholdet
                response = model.generate_content([audio_file, prompt])
                
                # Vis resultatet
                st.subheader("📝 Dit Mødereferat")
                st.markdown(response.text)
                
                # Download knap til teamet
                st.download_button(
                    label="Hent referat som .txt",
                    data=response.text,
                    file_name="moedereferat.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                # Vi viser fejlen, men uden at afsløre API-nøglen
                st.error(f"Der opstod en fejl: {str(e)}")

# 5. Hjælp til kollegaerne
st.divider()
with st.expander("💡 Tips til bedre referater"):
    st.write("""
    * **Placering:** Læg mobilen/computeren midt på bordet for at fange alle stemmer.
    * **Tydelighed:** Nævn gerne tal og specifikke KPI'er højt, så Gemini fanger dem korrekt.
    * **Længde:** Ved møder over 30 minutter er det bedst at uploade en fil fremfor at optage live.
    """)

