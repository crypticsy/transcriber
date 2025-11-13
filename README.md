# 🎙️ Audio Transcription & Report Generator

A Streamlit web application that transcribes audio files and generates customized reports by answering your questions based on the transcription. Perfect for meeting notes, interviews, lectures, and more!

## ✨ Features

- 🎧 **Free Audio Transcription**: Uses OpenAI Whisper locally (no API costs!) - Supports WAV, MP3, M4A, OGG, and FLAC formats (up to 25MB)
- 📝 **Customizable Questions**: Edit the prompt to ask specific questions about your audio
- 🤖 **AI-Powered Reports**: Uses Google Gemini AI to generate detailed, intelligent reports
- 💾 **Save & Download**: Save custom prompts and download both transcriptions and reports
- ☁️ **Cloud Ready**: Optimized for deployment on Streamlit Cloud
- 💰 **Cost-Effective**: Free transcription + Gemini's generous free tier (15 requests/minute)

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

## ☁️ Deploying to Streamlit Cloud

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository, branch, and `app.py` as the main file
   - Click "Deploy"

3. **Add your Gemini API key to Streamlit Cloud Secrets** (optional for transcription-only):
   - In your app dashboard, click the three dots menu
   - Select "Settings"
   - Go to "Secrets" section
   - Add your Gemini API key:
     ```toml
     GEMINI_API_KEY = "your-api-key-here"
     ```
   - Click "Save"

   **Note**: The app will transcribe audio even without an API key. The API key is only needed for report generation.

## 📖 How to Use

1. **Upload an audio file** (WAV, MP3, M4A, OGG, or FLAC)
2. **Select transcription model** (base is faster, medium/large are more accurate)
3. **Customize the questions** you want answered (optional)
4. **Enter your Gemini API Key** in the sidebar (only needed for report generation)
5. **Click "Generate Report"** and wait for the results
6. **Download** the transcription and/or report as needed

## 🎨 Customizing Questions

The app comes with default questions, but you can customize them to fit your needs:

1. Edit the text area in the "Customize Questions" section
2. Click "Save as Default Prompt" to save your custom questions
3. Your custom prompt will be saved in `default_prompt.txt`

### Example Custom Prompts

**For Meeting Notes:**
```
Based on this meeting transcription:
1. What were the main decisions made?
2. What action items were assigned and to whom?
3. What are the next steps and deadlines?
4. Were there any concerns or blockers raised?
```

**For Interviews:**
```
Analyze this interview and provide:
1. A brief summary of the candidate's background
2. Key strengths demonstrated
3. Areas of concern or weakness
4. Overall recommendation
```

**For Lectures:**
```
From this lecture transcription:
1. What is the main topic?
2. What are the key concepts explained?
3. What examples or case studies were used?
4. What are the main takeaways for students?
```

## 💰 Cost Considerations

This app is designed to be cost-effective:

### Transcription (FREE!)
- Uses **local Whisper model** - completely free
- No API calls for transcription
- Runs on your CPU/GPU

### Report Generation (Gemini AI)
- **Gemini 1.5 Flash** (recommended): FREE tier includes 15 requests/minute, 1M requests/day
- **Gemini 1.5 Pro**: FREE tier includes 2 requests/minute
- Paid tiers start at $0.075 per 1M input characters

**Total cost for most use cases: $0.00** (within free tier limits)

## 🔧 Configuration

### Changing Models

You can select different models in the sidebar:

**Transcription (Local Whisper)**:
- **base** (fastest, ~140MB) - Good for clear audio
- **small** (~460MB) - Better accuracy
- **medium** (~1.5GB) - High accuracy
- **large** (~2.9GB) - Best accuracy

**Report Generation (Gemini)**:
- **gemini-1.5-flash** (recommended) - Fast and free
- **gemini-1.5-pro** - More capable, slower
- **gemini-pro** - Previous generation

### File Size Limits

The maximum upload size is 25MB, configured in `.streamlit/config.toml`. You can adjust this, but keep in mind Streamlit Cloud's limitations.

## 📁 Project Structure

```
audio-transcriber/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── default_prompt.txt              # Default questions template
├── .streamlit/
│   ├── config.toml                 # App configuration
│   └── secrets.toml.example        # Example secrets file
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## 🛠️ Troubleshooting

### FFmpeg not found error
- Make sure FFmpeg is installed on your system
- Verify installation: `ffmpeg -version`
- See installation instructions in the Prerequisites section

### Transcription is slow
- Use a smaller Whisper model (base or small)
- Larger models (medium, large) require more processing time and memory
- First run downloads the model - subsequent runs are faster

### "File size exceeds limit"
- The file must be under 25MB. Try compressing your audio file or splitting it into smaller segments

### "Rate limit exceeded" (Gemini)
- Free tier: 15 requests/minute for gemini-1.5-flash, 2/minute for gemini-1.5-pro
- Wait a moment and try again

### Out of memory errors
- Use a smaller Whisper model (base or small instead of medium/large)
- Close other applications to free up RAM
- On Streamlit Cloud, stick to "base" or "small" models

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Transcription by [OpenAI Whisper](https://github.com/openai/whisper) (open-source)
- Report generation by [Google Gemini AI](https://ai.google.dev/)

---

Made with ❤️ for easy, free audio transcription and analysis
