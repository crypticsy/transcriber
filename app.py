import streamlit as st
import whisper
import google.generativeai as genai
from pathlib import Path
import tempfile
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from io import BytesIO

# Function to convert markdown to reportlab-compatible HTML
def markdown_to_reportlab_html(text):
    """Convert markdown formatting to reportlab-compatible HTML tags"""
    # Escape XML special characters first (but not < and > yet, we'll add HTML tags)
    text = text.replace('&', '&amp;')

    # Convert bold (**text** or __text__)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

    # Convert italic (*text* or _text_) - be careful not to match ** or __
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<i>\1</i>', text)

    # Convert inline code (`text`)
    text = re.sub(r'`(.+?)`', r'<font face="Courier">\1</font>', text)

    # Now escape remaining < and > that aren't part of our HTML tags
    # This is a bit tricky, so we'll just leave them for now as reportlab handles them

    return text

# Function to generate PDF
def generate_pdf(title, content, filename):
    """Generate a PDF from text content with markdown support"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1f77b4',
        spaceAfter=30,
        alignment=TA_LEFT
    )

    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#2c3e50',
        spaceAfter=12,
        spaceBefore=12,
        alignment=TA_LEFT
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#34495e',
        spaceAfter=10,
        spaceBefore=10,
        alignment=TA_LEFT
    )

    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor='#34495e',
        spaceAfter=8,
        spaceBefore=8,
        alignment=TA_LEFT
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['BodyText'],
        fontSize=11,
        leading=14,
        leftIndent=20,
        alignment=TA_LEFT
    )

    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        leading=12,
        fontName='Courier',
        leftIndent=20,
        rightIndent=20,
        spaceBefore=6,
        spaceAfter=6
    )

    # Add title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))

    # Process content line by line
    lines = content.split('\n')
    i = 0
    in_code_block = False
    code_block_content = []
    current_list = []
    list_type = None  # 'bullet' or 'number'

    while i < len(lines):
        line = lines[i]

        # Check for code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                if code_block_content:
                    code_text = '\n'.join(code_block_content)
                    code_text = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    elements.append(Paragraph(code_text, code_style))
                    elements.append(Spacer(1, 6))
                code_block_content = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_block_content.append(line)
            i += 1
            continue

        # Flush current list if we're not on a list item
        if current_list and not (line.strip().startswith('-') or line.strip().startswith('*') or re.match(r'^\d+\.', line.strip())):
            # Create list flowable
            list_items = [ListItem(Paragraph(markdown_to_reportlab_html(item), bullet_style), leftIndent=0) for item in current_list]
            if list_type == 'bullet':
                elements.append(ListFlowable(list_items, bulletType='bullet', start='•'))
            else:
                elements.append(ListFlowable(list_items, bulletType='1'))
            elements.append(Spacer(1, 6))
            current_list = []
            list_type = None

        # Process the line
        if not line.strip():
            # Empty line - add small spacer
            if not current_list:
                elements.append(Spacer(1, 6))
        elif line.startswith('### '):
            # Heading 3
            heading_text = markdown_to_reportlab_html(line[4:])
            elements.append(Paragraph(heading_text, heading3_style))
        elif line.startswith('## '):
            # Heading 2
            heading_text = markdown_to_reportlab_html(line[3:])
            elements.append(Paragraph(heading_text, heading2_style))
        elif line.startswith('# '):
            # Heading 1
            heading_text = markdown_to_reportlab_html(line[2:])
            elements.append(Paragraph(heading_text, heading1_style))
        elif line.strip().startswith('-') or line.strip().startswith('*'):
            # Bullet point
            bullet_text = line.strip()[1:].strip()
            current_list.append(bullet_text)
            list_type = 'bullet'
        elif re.match(r'^\d+\.', line.strip()):
            # Numbered list
            numbered_text = re.sub(r'^\d+\.\s*', '', line.strip())
            current_list.append(numbered_text)
            list_type = 'number'
        else:
            # Regular paragraph
            para_text = markdown_to_reportlab_html(line)
            elements.append(Paragraph(para_text, body_style))
            elements.append(Spacer(1, 6))

        i += 1

    # Flush any remaining list
    if current_list:
        list_items = [ListItem(Paragraph(markdown_to_reportlab_html(item), bullet_style), leftIndent=0) for item in current_list]
        if list_type == 'bullet':
            elements.append(ListFlowable(list_items, bulletType='bullet', start='•'))
        else:
            elements.append(ListFlowable(list_items, bulletType='1'))
        elements.append(Spacer(1, 6))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

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
        ["tiny", "base", "small"],
        index=0, 
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
if 'current_transcript' not in st.session_state:
    st.session_state['current_transcript'] = None
if 'current_report' not in st.session_state:
    st.session_state['current_report'] = None
if 'current_filename' not in st.session_state:
    st.session_state['current_filename'] = None

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

            # Store in session state
            st.session_state['current_transcript'] = transcript
            st.session_state['current_filename'] = uploaded_file.name

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

                # Store report in session state
                st.session_state['current_report'] = report

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.exception(e)

# Display results outside the process button block (persists across reruns)
if st.session_state['current_transcript'] is not None:
    st.divider()

    # Display transcription
    st.header("📄 Transcription")
    with st.expander("View Full Transcription", expanded=True):
        st.text_area("Transcribed Text", value=st.session_state['current_transcript'], height=200, disabled=True)

        # Generate PDF for download
        pdf_buffer = generate_pdf(
            title=f"Transcription - {st.session_state['current_filename']}",
            content=st.session_state['current_transcript'],
            filename=f"{Path(st.session_state['current_filename']).stem}_transcription.pdf"
        )

        st.download_button(
            "⬇️ Download Transcription (PDF)",
            data=pdf_buffer,
            file_name=f"{Path(st.session_state['current_filename']).stem}_transcription.pdf",
            mime="application/pdf",
            key="download_transcript"
        )

    # Display report if available
    if st.session_state['current_report'] is not None:
        st.header("📊 Generated Report")
        with st.expander("View Full Report", expanded=True):
            st.markdown(st.session_state['current_report'])

            # Generate PDF for download
            report_pdf_buffer = generate_pdf(
                title=f"AI-Generated Report - {st.session_state['current_filename']}",
                content=st.session_state['current_report'],
                filename=f"{Path(st.session_state['current_filename']).stem}_report.pdf"
            )

            st.download_button(
                "⬇️ Download Report (PDF)",
                data=report_pdf_buffer,
                file_name=f"{Path(st.session_state['current_filename']).stem}_report.pdf",
                mime="application/pdf",
                key="download_report"
            )

# Add a clear button at the bottom if there are results
if st.session_state['current_transcript'] is not None:
    st.divider()
    if st.button("🔄 Clear Results and Start New", type="secondary"):
        st.session_state['current_transcript'] = None
        st.session_state['current_report'] = None
        st.session_state['current_filename'] = None
        st.rerun()
