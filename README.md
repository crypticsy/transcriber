# 🎙️ Audio Transcription & Report Generator

A Streamlit web application that transcribes audio files and generates customized reports by answering your questions based on the transcription. Perfect for meeting notes, interviews, lectures, and more!

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system ([Download here](https://ffmpeg.org/download.html))
- Google Gemini API key ([Get one FREE here](https://makersuite.google.com/app/apikey))

### Local Installation

1. **Clone or download this repository**

2. **Install FFmpeg** (required for audio processing):
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Note: First run will download the Whisper model (~140MB for base model)

4. **Set up your Gemini API key** (optional - can also enter in UI):

   **Option A: Using secrets file (recommended for local development)**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   Then edit `.streamlit/secrets.toml` and add your Gemini API key.

   **Option B: Enter API key in the app**
   You can enter your API key directly in the sidebar when running the app.

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** to `http://localhost:8501`

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Transcription by [OpenAI Whisper](https://github.com/openai/whisper) (open-source)
- Report generation by [Google Gemini AI](https://ai.google.dev/)