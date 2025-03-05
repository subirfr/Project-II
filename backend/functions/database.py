import json
import os

DB_FILE = "conversation.json"

# Retrieve recent messages from the database (conversation history)
def get_recent_messages():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

# Store messages in the database
def store_messages(user_input, english_response, hindi_translation):
    """
    Stores the conversation history, including:
    - The original user input (English)
    - The LLaMA-generated English response
    - The Hindi translation of the response
    """
    messages = get_recent_messages()
    
    messages.append({"role": "user", "content": user_input})
    messages.append({"role": "assistant_english", "content": english_response})
    messages.append({"role": "assistant_hindi", "content": hindi_translation})

    with open(DB_FILE, "w") as file:
        json.dump(messages, file, indent=4)

# Reset conversation history
def reset_messages():
    with open(DB_FILE, "w") as file:
        json.dump([], file)
