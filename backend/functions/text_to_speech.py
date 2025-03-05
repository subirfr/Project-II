import requests
from decouple import config
from requests.exceptions import RequestException, Timeout
import time

ELEVEN_LABS_API_KEY = config("ELEVEN_LABS_API_KEY")

# Eleven Labs
# Convert text to speech
def convert_text_to_speech(message):
    body = {
        "text": message,
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0
        }
    }

    voice_shaun = "mTSvIrm2hmcnOvb21nW2"
    voice_rachel = "21m00Tcm4TlvDq8ikWAM"
    voice_antoni = "ErXwobaYiN019PkySvjV"

    # Construct request headers and url
    headers = { 
        "xi-api-key": ELEVEN_LABS_API_KEY, 
        "Content-Type": "application/json", 
        "accept": "audio/mpeg" 
    }
    endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_rachel}"

    # Retry logic for making the request
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.post(endpoint, json=body, headers=headers, timeout=10)
            response.raise_for_status()  # Check for HTTP errors
            if response.status_code == 200:
                # Log success and return the audio content
                print(f"Successfully received audio response on attempt {attempt + 1}.")
                return response.content
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        except Timeout:
            print(f"Timeout occurred on attempt {attempt + 1}, retrying...")
        except RequestException as e:
            print(f"Error during request on attempt {attempt + 1}: {e}, retrying...")

        time.sleep(3)  # Wait for 3 seconds before retrying

    # If all retries fail, return None
    print("Failed to generate audio after 3 attempts.")
    return None
