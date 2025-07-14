# gemini_module.py – The Professional, Failsafe Version

import google.generativeai as genai
import re # Regular expressions ke liye import karein
from config_loader import GEMINI_API_KEY

# --- Module Level Configuration ---
# Yeh ek "light switch" jaisa hai. Default mein switch 'OFF' hai.
is_gemini_configured = False

# Sirf ek baar, jab program shuru ho, tabhi configuration try karein.
if GEMINI_API_KEY and "YAHAN_APNI" not in GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        is_gemini_configured = True # Agar sab theek raha, to switch ko 'ON' kar do.
        print("✅ Gemini module configured successfully.")
    except Exception as e:
        # Agar koi error aaya, to switch 'OFF' hi rahega.
        print(f"❌ CRITICAL: Gemini API Key configuration failed. Error: {e}")
else:
    # Agar key hai hi nahi, to bhi switch 'OFF' hi rahega.
    print("❌ WARNING: Gemini API Key not found or is a placeholder in config.ini.")


def chat_with_gemini(prompt: str) -> str:
    """
    Gemini se chat karta hai aur saaf-suthra response return karta hai.
    Error aane par, ek error message string return karta hai.
    """
    # Ab humein bas light switch check karna hai.
    if not is_gemini_configured:
        return "Gemini Error: Module is not configured. Please check your API Key in config.ini."

    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(prompt)
        
        # Behtar Text Cleaning: Regular expressions se markdown (jaise **, *, ###) hatayein
        # 'r' ka matlab hai raw string, jo backslash ke saath aache se kaam karta hai.
        # '[*#]+' ka matlab hai * ya # character ek ya ek se zyada baar aaye.
        clean_text = re.sub(r'[\*#]+', '', response.text)
        
        # Shuru aur ant ke faltu spaces ko hata dein
        return clean_text.strip()

    except Exception as e:
        error_message = f"Gemini Error: API call fail ho gayi. Kaaran: {e}"
        print(f"❌ {error_message}")
        return error_message