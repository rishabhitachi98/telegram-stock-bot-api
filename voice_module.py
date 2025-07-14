# voice_module.py – Stable TTS playback without file‑lock issues

"""
Dependencies:
  pip install gTTS pygame SpeechRecognition pyaudio keyboard

Key features:
- Uses gTTS to generate a temp MP3 each time (no fixed filename)
- Plays audio via pygame mixer and blocks until playback finishes (no Enter needed)
- Cleans up temp file once done, avoiding WinError 32 / MCI 277
"""

import speech_recognition as sr
from gtts import gTTS
import pygame
import time
import tempfile
import os
import msvcrt  # for detecting key press on Windows

# 🟢 Initialise mixer once globally
if not pygame.mixer.get_init():
    pygame.mixer.init()

def listen():
    recognizer = sr.Recognizer()

    # Ask for preferred mode
    print("\n🟢 Type your question or just press Enter to use voice input:")
    typed = input("✍️  Input (leave blank for mic): ").strip()

    if typed:
        print(f"🗣️ You typed: {typed}")
        return typed  # Use typed input directly

    # Otherwise, fall back to voice
    try:
        with sr.Microphone() as source:
            print("🎙️ Speak now... (Hinglish chalega)")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        query = recognizer.recognize_google(audio, language="en-IN")
        print(f"🗣️ You said: {query}")
        return query

    except sr.UnknownValueError:
        return "Sorry, samajh nahi aaya."
    except sr.RequestError as e:
        return f"Speech service error: {e}"

def speak(text: str):
    """
    Sirf diye gaye text ko bolta hai. Koi extra processing nahi karta.
    """
    if not text or not text.strip():
        print("🔊 Nothing to speak.")
        return

    try:
        # ✅ Save to temp file
        tts = gTTS(text=text, lang='en', tld='co.in', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            filename = tmpfile.name
        tts.save(filename)

        # ✅ Play via pygame
        # Re-initialize mixer for each call to avoid state issues
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        print(f"🔊 Speaking: \"{text}\"")

        # Wait until playback is finished
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    except Exception as e:
        print(f"❌ Error in speak(): {e}")
    
    finally:
        # ✅ Cleanup
        # Ensure mixer is quit and file is removed, even if there's an error
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        if 'filename' in locals() and os.path.exists(filename):
            try:
                os.remove(filename)
            except PermissionError:
                # If file is still in use, wait a bit and try again
                time.sleep(0.5)
                if os.path.exists(filename):
                    os.remove(filename)