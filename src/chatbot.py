import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

# --- 1. Load Environment Variables (.env) ---
# Yeh logic .env file ko dhundta hai chahe wo kisi bhi folder me ho

env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GROQ_API_KEY")

# env_path = Path(__file__).parent.parent / '.env'
# load_dotenv(dotenv_path=env_path)

# # --- 2. Initialize Groq Client ---
# api_key = os.getenv("GROQ_API_KEY")

# Debugging: Terminal me check karega ki key mili ya nahi
if not api_key:
    print("❌ ERROR: 'GROQ_API_KEY' nahi mili! .env file check karein.")
    client = None
else:
    print(f"✅ API Key Loaded successfully: {api_key[:5]}********")
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        print(f"❌ Client Initialization Error: {e}")
        client = None

def get_chat_response(user_input):
    """
    User ke input ka jawab Llama 3 model se le kar aata hai.
    """
    # Agar client load nahi hua to seedha error return karein
    if not client:
        return "System Error: API Key is missing or invalid. Check terminal logs."

    # System prompt: AI ko batana ki wo kaise behave kare
    system_prompt = (
        "You are 'MindLog', a supportive, empathetic, and gentle AI diary companion. "
        "Your goal is to listen to the user's feelings without judging. "
        "Keep your responses short (2-3 sentences), warm, and human-like. "
        "Do not give medical advice. If the user sounds very depressed, gently suggest seeking help "
        "but mostly focus on being a good listener."
    )
    
    try:
        # API Call to Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            model="llama-3.3-70b-versatile", # Fast and Free model
            temperature=0.7,       # Thoda creative aur natural jawab ke liye
            max_tokens=200,        # Jawab zyada lamba na ho
        )
        
        # Jawab nikalna
        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"❌ API Error: {e}")
        return "I am having trouble thinking right now. Please try again in a moment."

# Test run (sirf jab is file ko directly run karein)
if __name__ == "__main__":
    print(get_chat_response("I am feeling very sad today."))