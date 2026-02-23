import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# 1. Konfiguration af siden
st.set_page_config(page_title="SEO/Ads Møde-Butler", page_icon="🎯", layout="centered")

st.title("🎯 SEO & Ads Møde-Butler")
st.write("Optag mødet live eller upload en fil for at få et struktureret referat.")

# 2. Sikkerhed: Hent API-nøgle fra Streamlit Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Fejl: API-nøgle ikke fundet. Tilføj GEMINI_API_KEY i Streamlit Settings -> Secrets.")
    st.stop()

# 3. Brugergrænseflade: Optagelse og Upload
st.divider()
tab1, tab2 = st.tabs(["🔴 Optag Live", "📁 Upload Fil"])

audio_bytes = None

with tab1:
    st.subheader("Optag direkte")
    st.write("Klik på knappen for at starte optagelsen via din mikrofon.")
    # Mikrofon-komponenten
    audio_record = mic_recorder(
        start_prompt="🔴 Start optagelse",
        stop_prompt="⏹️ Stop optagelse",
        just_once=False,
        use_container_width=True,
        key="recorder"
    )
    if audio_record:
        audio_bytes = audio_record['bytes']
        st.audio(audio_bytes, format="audio/wav")

with tab2:
    st.subheader("Upload lydfil")
    uploaded_file = st.file_uploader("Vælg en lydfil (mp3, wav, m4a)", type=['mp3', 'wav', 'm4a'])
    if uploaded_file:
        audio_bytes = uploaded_file.getbuffer()
        st.audio(audio_bytes)

# 4. Processering med Gemini
if audio_bytes:
    st.divider()
    if st.button("Generér Referat ✨", type="primary", use_container_width=True):
        with st.spinner("Gemini transskriberer og analyserer mødet..."):
            try:
                # Gem lyden midlertidigt som en fil
                with open("temp_meeting_audio.wav", "wb") as f:
                    f.write(audio_bytes)
                
                # Initialiser Gemini modellen (1.5 Flash er hurtig og god til lyd)
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                
                # Upload filen til Googles AI-servere
                audio_api_file = genai.upload_file(path="temp_meeting_audio.wav")
                
                # Din skræddersyede SEO/Ads prompt
                prompt = """Du er en specialist i SEO og Google Ads. 
                Baseret på denne lydfil, skal du lave et detaljeret og struktureret referat.
                
                Strukturen SKAL være præcis som dette eksempel:
                
                - Overskrifter for hvert emne (fx Performance overview, Budget-strategi, PMax, Enhanced Conversions)
                - Bulletpoints med specifikke indsigter, tal og KPI'er (fx ROAS, Impression share, konverteringer)
                - En klar sektion til sidst kaldet 'Action Items' med tjekbokse [ ]
                
                Vær meget opmærksom på tekniske detaljer omkring tracking, GTM, scripts og kampagneoptimeringer.
                """
                
                # Generér indholdet
                response = model.generate_content([audio_api_file, prompt])
                
                # Vis resultatet
                st.subheader("📝 Færdigt Referat")
                st.markdown(response.text)
                
                # Mulighed for at downloade resultatet
                st.download_button(
                    label="Hent referat som tekstfil",
                    data=response.text,
                    file_name="moedereferat.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Der opstod en fejl under processeringen: {e}")

# 5. Instruktion til teamet
st.divider()
with st.expander("💡 Sådan bruger I værktøjet"):
    st.write("""
    1. **Optagelse:** Sørg for at give browseren lov til at bruge mikrofonen.
    2. **Længde:** Ved meget lange møder (over 30 min) anbefales det at uploade en fil i stedet for at optage live.
    3. **Sikkerhed:** Optagelsen gemmes kun midlertidigt under analysen og slettes derefter.
    """)

