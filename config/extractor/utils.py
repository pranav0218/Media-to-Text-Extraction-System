import os

# 🔴 Make FFmpeg and Poppler visible to Python & Whisper
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
os.environ["PATH"] += os.pathsep + r"C:\poppler\Library\bin"

import pytesseract
from PIL import Image
import pdfplumber
import subprocess
import whisper
from pdf2image import convert_from_path

# Absolute FFmpeg path (safe fallback)
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

# Load Whisper model ONCE (important for performance)
whisper_model = whisper.load_model("base")


def extract_text(file_path):
    file_path_lower = file_path.lower()

    # ---------- IMAGE ----------
    if file_path_lower.endswith(('.png', '.jpg', '.jpeg')):
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)

    # ---------- PDF (TEXT + OCR FALLBACK) ----------
    elif file_path_lower.endswith('.pdf'):
        text = ""

        # Try extracting digital text first
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # If digital text exists, return it
        if text.strip():
            return text

        # OCR fallback for scanned PDFs
        images = convert_from_path(file_path, dpi=300)

        ocr_text = ""
        for img in images:
            ocr_text += pytesseract.image_to_string(img) + "\n"

        return ocr_text

    # ---------- VIDEO ----------
    elif file_path_lower.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        return video_to_text(file_path)

    return "Unsupported file format"


# ---------- WHISPER TIMESTAMP HELPERS ----------

def format_timestamp(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def video_to_text(video_path):
    """
    Extract audio using FFmpeg and transcribe using Whisper WITH timestamps
    """
    audio_path = video_path + ".wav"

    # Extract audio from video
    subprocess.run([
        FFMPEG_PATH,
        "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ], check=True)

    # Transcribe audio using Whisper
    result = whisper_model.transcribe(audio_path)

    transcript = ""

    for segment in result["segments"]:
        start = format_timestamp(segment["start"])
        end = format_timestamp(segment["end"])
        text = segment["text"].strip()

        transcript += f"[{start} – {end}] {text}\n"

    # Cleanup temporary audio file
    if os.path.exists(audio_path):
        os.remove(audio_path)

    return transcript
