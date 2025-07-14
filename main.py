from voice_module import listen, speak
from gemini_module import chat_with_gemini

exit_keywords = ["bye", "exit", "quit", "close", "goodbye", "see you", "exit karte hain", "chalo"]

def is_exit_command(text):
    text = text.lower()
    for kw in exit_keywords:
        if kw in text:
            return True
    return False

def main():
    speak("Namaste! Kya jaanna chahte ho?")
    while True:
        query = listen()
        if not query:
            speak("Kuch samajh nahi aaya, dobara bolo.")
            continue

        if is_exit_command(query):
            speak("Theek hai, bye!")
            break

        response = chat_with_gemini(query)
        print("\n🧠 Gemini (Text):", response)

if __name__ == "__main__":
    main()
