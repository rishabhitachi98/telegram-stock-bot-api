# gemini_module.py (The Final, Simplified Version)
import google.generativeai as genai
from config_loader import GEMINI_API_KEY

IS_CONFIGURED = False
model = None

try:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        print("✅ Gemini module configured successfully.")
        IS_CONFIGURED = True
    else:
        print("❌ WARNING: Gemini API Key not loaded.")
except Exception as e:
    print(f"❌ CRITICAL: Gemini configuration failed. Error: {e}")

def chat_with_gemini(prompt: str) -> str:
    if not IS_CONFIGURED or not model:
        return "Gemini Error: Module configure nahi ho paaya. Apni .env file aur API Key check karein."

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        error_message = f"Gemini Error: API call fail ho gayi. Kaaran: {e}"
        print(f"❌ {error_message}")
        return error_message