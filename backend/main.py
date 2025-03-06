from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import io

# Custom function imports
from functions.text_to_speech import convert_text_to_speech
from functions.requests import convert_audio_to_text, translate_text_to_hindi, generate_llama_response
from functions.database import store_messages, reset_messages

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initiate FastAPI App
app = FastAPI()

# CORS - Allowed Origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
]

# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store audio output temporarily
AUDIO_STORAGE = {}

# Post Audio & Get Translated Response
@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")
        file.file.seek(0)  # Reset file pointer

        # Save file temporarily
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            buffer.write(file.file.read())

        logger.info(f"Saved file: {temp_filename}")

        # Process audio
        with open(temp_filename, "rb") as audio_input:
            message_decoded = convert_audio_to_text(audio_input)

        os.remove(temp_filename)  # Clean up

        if not message_decoded:
            raise HTTPException(status_code=400, detail="Failed to decode audio")

        logger.info(f"Decoded Message: {message_decoded}")

        # Generate English response
        english_response = generate_llama_response(message_decoded)

        if not english_response:
            raise HTTPException(status_code=400, detail="Failed to generate English response")

        logger.info(f"English Response: {english_response}")

        # Translate text to Hindi
        hindi_translation = translate_text_to_hindi(message_decoded)

        if not hindi_translation:
            raise HTTPException(status_code=400, detail="Failed to generate Hindi translation")

        logger.info(f"Hindi Translation: {hindi_translation}")

        # Store messages in database
        store_messages(message_decoded, english_response, hindi_translation)

        # Convert text to speech
        audio_output = convert_text_to_speech(hindi_translation)
        if not audio_output:
            raise HTTPException(status_code=400, detail="Failed to generate audio output")

        # Store audio in dictionary (simulating a database)
        audio_id = f"audio_{len(AUDIO_STORAGE) + 1}"
        AUDIO_STORAGE[audio_id] = audio_output

        # Return JSON response with an audio ID
        return JSONResponse(content={
            "message_decoded": message_decoded,
            "english_response": english_response,
            "hindi_translation": hindi_translation,
            "audio_id": audio_id  # Client will use this to request audio separately
        })

    except Exception as e:
        logger.error(f"Error in /post-audio/: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# New Route: Fetch Hindi Speech Audio Separately
@app.get("/get-audio/{audio_id}")
async def get_audio(audio_id: str):
    audio_output = AUDIO_STORAGE.get(audio_id)
    if not audio_output:
        raise HTTPException(status_code=404, detail="Audio not found")

    return StreamingResponse(io.BytesIO(audio_output), media_type="audio/mpeg")
