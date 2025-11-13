import streamlit as st
import whisper
import google.generativeai as genai
from pathlib import Path
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="Audio Transcription & Report Generator",
    page_icon="🎙️",
    layout="wide"
)

# Title and description
st.title("🎙️ Audio Transcription & Report Generator")
st.markdown("""
This app transcribes audio files and generates reports by answering your custom questions based on the transcription.
""")

# Get API key from secrets
try:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if api_key:
        genai.configure(api_key=api_key)
except:
    api_key = ""

# Model selection
st.markdown("### ⚙️ Model Settings")
col_model1, col_model2 = st.columns([1, 1])

with col_model1:
    transcription_model = st.selectbox(
        "🎧 Transcription Model",
        ["base", "small", "medium", "large"],
        help="Whisper model size (base is faster, large is more accurate)"
    )

with col_model2:
    # Map display names to actual model names
    model_options = {
        "Gemini 2.5 Flash (Fast)": "models/gemini-2.5-flash",
        "Gemini 2.5 Pro (High Quality)": "models/gemini-2.5-pro",
        "Gemini 2.0 Flash (Stable)": "models/gemini-2.0-flash"
    }
    selected_model_name = st.selectbox(
        "🤖 Report Generation Model",
        list(model_options.keys()),
        help="Gemini model for generating the report"
    )
    report_model = model_options[selected_model_name]

st.divider()

# Load default prompt
def load_default_prompt():
    prompt_file = Path("default_prompt.txt")
    if prompt_file.exists():
        return prompt_file.read_text()
    else:
        return """Please analyze the following transcription and answer these questions:

1. What is the main topic or subject of this audio?
2. What are the key points or main ideas discussed?
3. Are there any action items or tasks mentioned?
4. What is the overall tone or sentiment of the conversation?
5. Are there any important dates, numbers, or names mentioned?
6. What are the main conclusions or takeaways?

Please provide clear and concise answers to each question based on the transcription."""

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("1️⃣ Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
        help="Supported formats: WAV, MP3, M4A, OGG, FLAC (max 25MB)"
    )

    if uploaded_file:
        st.audio(uploaded_file)
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.json(file_details)

with col2:
    st.header("2️⃣ Customize Questions")
    prompt_template = st.text_area(
        "Edit the questions/prompt below:",
        value=load_default_prompt(),
        height=300,
        help="Customize the questions you want answered based on the transcription"
    )

    # Option to save custom prompt
    if st.button("💾 Save as Default Prompt"):
        try:
            with open("default_prompt.txt", "w") as f:
                f.write(prompt_template)
            st.success("✅ Prompt saved as default!")
        except Exception as e:
            st.error(f"Error saving prompt: {str(e)}")

# Process button
st.divider()
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    process_button = st.button("🚀 Generate Report", type="primary", use_container_width=True)

# Initialize session state for caching
if 'transcription_cache' not in st.session_state:
    st.session_state['transcription_cache'] = {}

# Processing
if process_button:
    if not uploaded_file:
        st.error("❌ Please upload an audio file.")
    else:
        try:
            # Create cache key based on file content and model
            file_hash = hash(uploaded_file.getvalue())
            cache_key = f"{file_hash}_{transcription_model}"

            # Check if transcription exists in cache
            if cache_key in st.session_state['transcription_cache']:
                transcript = st.session_state['transcription_cache'][cache_key]
                st.info("✅ Using cached transcription")
            else:
                # Step 1: Transcribe audio using local Whisper
                with st.spinner(f"🎧 Transcribing audio with Whisper ({transcription_model})... This may take a moment."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name

                    # Load Whisper model (cached after first load)
                    @st.cache_resource
                    def load_whisper_model(model_name):
                        return whisper.load_model(model_name)

                    model = load_whisper_model(transcription_model)

                    # Transcribe using local Whisper
                    result = model.transcribe(tmp_file_path)
                    transcript = result["text"]

                    # Clean up temp file
                    os.unlink(tmp_file_path)

                    # Cache the transcription
                    st.session_state['transcription_cache'][cache_key] = transcript

                st.success("✅ Transcription completed!")

            # Display transcription
            st.header("📄 Transcription")
            with st.expander("View Full Transcription", expanded=True):
                st.text_area("Transcribed Text", value=transcript, height=200, disabled=True)
                st.download_button(
                    "⬇️ Download Transcription",
                    data=transcript,
                    file_name=f"{Path(uploaded_file.name).stem}_transcription.txt",
                    mime="text/plain"
                )

            # Step 2: Generate report using Gemini
            if not api_key:
                st.warning("⚠️ Gemini API key not provided. Transcription completed, but report generation requires an API key.")
            else:
                # Create cache key for report
                report_cache_key = f"{cache_key}_{report_model}_{hash(prompt_template)}"

                # Check if report exists in cache
                if 'report_cache' not in st.session_state:
                    st.session_state['report_cache'] = {}

                if report_cache_key in st.session_state['report_cache']:
                    report = st.session_state['report_cache'][report_cache_key]
                    st.info("✅ Using cached report")
                else:
                    with st.spinner("📝 Generating report with Gemini AI..."):
                        # Create the full prompt
                        full_prompt = f"""{prompt_template}

---

TRANSCRIPTION:
{transcript}"""

                        # Generate report using Gemini
                        model = genai.GenerativeModel(report_model)
                        response = model.generate_content(full_prompt)
                        report = response.text

                        # Cache the report
                        st.session_state['report_cache'][report_cache_key] = report

                    st.success("✅ Report generated!")

                # Display report
                st.header("📊 Generated Report")
                with st.expander("View Full Report", expanded=True):
                    st.markdown(report)
                    st.download_button(
                        "⬇️ Download Report",
                        data=report,
                        file_name=f"{Path(uploaded_file.name).stem}_report.txt",
                        mime="text/plain"
                    )

                # Store in session state for later access
                st.session_state['last_report'] = report

            # Store transcription in session state
            st.session_state['last_transcription'] = transcript

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.exception(e)
