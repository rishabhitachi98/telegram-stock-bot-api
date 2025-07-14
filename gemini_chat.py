import time
import google.generativeai as genai

# 🔐 Direct API key pass karo (no .env confusion)
genai.configure(api_key="AIzaSyCacfMKc6q5r71Qi2sF04nztZNCJ37nxRA")

# ✅ Latest model
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# 🧠 Gemini se baat karne ka function (delay ke saath)
def chat_with_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        time.sleep(3)  # ✅ Delay to avoid quota breach
        return response.text
    except Exception as e:
        return f"❌ Gemini Error: {e}"
