import json
import logging
import vosk
import ollama
import os
import subprocess
import uuid

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Vosk Speech-to-Text Model
VOSK_MODEL_PATH = r"C:\Users\MY PC\vosk-model-small-en-us-0.15"  # Update with your model path

# Convert non-WAV audio files to WAV
def convert_to_wav(input_file_path):
    try:
        output_file = f"{uuid.uuid4().hex}.wav"
        
        # Run ffmpeg conversion with explicit Opus handling
        subprocess.run([
            'ffmpeg', '-y', '-i', input_file_path, 
            '-acodec', 'pcm_s16le', '-ac', '1', '-ar', '16000', output_file
        ], check=True)

        return output_file
    except Exception as e:
        logger.error(f"Error in converting audio to WAV: {e}")
        return None

# Convert Audio to Text using Vosk
def convert_audio_to_text(audio_file):
    try:
        # Generate a unique filename
        temp_filename = f"temp_{uuid.uuid4().hex}.wav"
        
        with open(temp_filename, "wb") as buffer:
            buffer.write(audio_file.read())

        # Convert to WAV if necessary
        file_path = convert_to_wav(temp_filename)
        if not file_path:
            logger.error("Failed to convert audio file to WAV")
            return None
        
        # Load Vosk model inside function (ensures fresh instance)
        vosk_model = vosk.Model(VOSK_MODEL_PATH)
        recognizer = vosk.KaldiRecognizer(vosk_model, 16000)
        
        with open(file_path, "rb") as wav_file:
            data = wav_file.read()
            recognizer.AcceptWaveform(data)

        result = recognizer.Result()

        # Cleanup temp files
        os.remove(file_path)
        os.remove(temp_filename)

        return json.loads(result)["text"]
        
    except Exception as e:
        logger.error(f"Error in audio transcription: {e}")
        return None

# Function to Generate LLaMA Response in English
def generate_llama_response(english_text):
    try:
        response = ollama.chat(model="llama3", messages=[{"role": "user", "content": english_text}])
        english_response = response["message"]["content"].strip()

        return english_response

    except Exception as e:
        logger.error(f"Error in generating LLaMA response: {e}")
        return None

# Function to Translate English to Hindi using LLaMA
# Function to Translate English to Hindi using LLaMA
# Function to Translate English to Hindi using LLaMA
def translate_text_to_hindi(english_text):
    try:
        prompt = f"Translate the following English text into Hindi: '{english_text}' and return only the Hindi translation without any explanations or notes."
        response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
        hindi_translation = response["message"]["content"].strip()

        # Remove "Hindi Translation:" prefix if present
        if "Hindi Translation:" in hindi_translation:
            hindi_translation = hindi_translation.split("Hindi Translation:")[-1].strip()

        # Remove any extra notes (assumes notes start with '(' or 'Note:')
        hindi_translation = hindi_translation.split("\n")[0]  # Takes only the first line
        hindi_translation = hindi_translation.split("Note:")[0].strip()  # Removes additional notes if present

        return hindi_translation

    except Exception as e:
        logger.error(f"Error in text translation: {e}")
        return None
