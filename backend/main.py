# Run server with:
# uvicorn main:app --reload

# Main imports
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# Custom function imports
from functions.text_to_speech import convert_text_to_speech
from functions.requests import convert_audio_to_text, translate_text_to_hindi
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

# Health Check
@app.get("/health")
async def check_health():
    return {"response": "healthy"}

# Reset Conversation
@app.get("/reset")
async def reset_conversation():
    reset_messages()
    return {"response": "conversation reset"}


# Post Audio & Get Translated Response
@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")
        logger.info(f"File size: {len(file.file.read())} bytes")
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

        # Translate text
        chat_response = translate_text_to_hindi(message_decoded)
        store_messages(message_decoded, chat_response)

        if not chat_response:
            raise HTTPException(status_code=400, detail="Failed to generate chat response")

        logger.info(f"Chat Response: {chat_response}")

        # Convert text to speech
        audio_output = convert_text_to_speech(chat_response)
        if not audio_output:
            raise HTTPException(status_code=400, detail="Failed to generate audio output")

        return StreamingResponse(iter([audio_output]), media_type="application/octet-stream")

    except Exception as e:
        logger.error(f"Error in /post-audio/: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
