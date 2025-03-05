import requests
from decouple import config
from requests.exceptions import RequestException, Timeout

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

    try:
        # Make the request with a timeout to prevent long waits
        response = requests.post(endpoint, json=body, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an error for bad HTTP status codes
    except Timeout:
        print("Error: The request timed out. Please check the network connection.")
        return None
    except RequestException as e:
        # Log the error and return a message
        print(f"Error during request: {e}")
        return None

    # Check if the response was successful
    if response.status_code == 200:
        # Return the audio content
        return response.content
    else:
        # Log the response error
        print(f"Error: {response.status_code} - {response.text}")
        return None
