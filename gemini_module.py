# gemini_module.py (FINAL VERSION)
import google.generativeai as genai
from config_loader import GEMINI_API_KEY # Assuming this is loaded correctly

# _gemini_model aur _is_gemini_configured_once lazy loading ke liye hain
_gemini_model = None
_is_gemini_configured_once = False 

def _configure_gemini_if_needed():
    global _gemini_model, _is_gemini_configured_once
    if _is_gemini_configured_once:
        return

    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            _gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest') # Changed to FLASH model
            print("✅ Gemini module configured successfully.")
        except Exception as e:
            print(f"❌ CRITICAL: Gemini configuration failed: {e}")
    else:
        print("❌ WARNING: Gemini API Key not found.")
    _is_gemini_configured_once = True 

def chat_with_gemini(prompt: str) -> str:
    _configure_gemini_if_needed()
    
    if not _gemini_model:
        return "Gemini Error: Module configure nahi ho paaya. Apni .env file aur API Key check karein."
    
    try:
        response = _gemini_model.generate_content(prompt)
        # Yahan koi re.sub ya cleaning nahi hai. Gemini ka raw Markdown text return hoga.
        return response.text.strip() 
    except Exception as e:
        error_message = f"Gemini Error: API call fail ho gayi. Kaaran: {e}"
        print(f"❌ {error_message}")
        return error_message