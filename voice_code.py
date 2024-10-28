import speech_recognition as sr
import keyboard

def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Please speak something...")
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand what you said."
    except sr.RequestError:
        return "Sorry, I am unable to access the Google API."

print("Press Enter to start listening...")
keyboard.wait("enter")

# Call the function to recognize speech
text = recognize_speech()
print(f"You said: {text}")

import pyttsx3

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


text_to_speech(text)