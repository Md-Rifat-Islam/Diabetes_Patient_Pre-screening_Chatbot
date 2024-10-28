import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

import speech_recognition as sr
import pyttsx3

import tkinter as tk
from PIL import Image, ImageTk
import threading

window = tk.Tk()
window.title("Chatbot Interface")

# Load the images
image_speaking = Image.open("Images/speaking.png")
image_listening = Image.open("Images/listening.png")
image_speaking = ImageTk.PhotoImage(image_speaking)
image_listening = ImageTk.PhotoImage(image_listening)

# Create a label to display the images
image_label = tk.Label(window, image=image_listening)
image_label.pack()

chat_speaking = False

# Function to switch images
def toggle_image(speaking=False):
    if speaking:
        image_label["image"] = image_speaking
    else:
        image_label["image"] = image_listening

# Initial image (listening)
toggle_image(False)

# Create a thread for the image switching task
image_thread = threading.Thread(target=toggle_image)
image_thread.daemon = True  # Allow the thread to exit when the main program exits
image_thread.start()

# Voice chatbot code (replace with your chatbot logic)
def chatbot_voice():
    lemmatizer = WordNetLemmatizer()
    intents = json.loads(open('dataset.json').read())
    words = pickle.load(open('words.pkl', 'rb'))
    classes = pickle.load(open('classes.pkl', 'rb'))
    model = load_model('chatbot_model.model')

    def clean_up_sentence(sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
        return sentence_words

    def bag_of_words(sentence):
        sentence_words = clean_up_sentence(sentence)
        bag = [0] * len(words)
        print("Vocabulary Size:", len(words))
        for w in sentence_words:
            if w in words:
                bag[words.index(w)] = 1
        return np.array(bag)


    def predict_class(sentence):
        bow = bag_of_words(sentence)
        res = model.predict(np.array([bow]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
        return return_list

    def get_response(intents_list, intents_json):
        tag = intents_list[0]['intent']
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                break
        return result

    import speech_recognition as sr

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

    def speak_text(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    speak_text("I am on")  # Say "I am on" when the chatbot starts

    # Create an array to store the conversation history
    conversation_history = []

    print("Bot is running")

    while True:
        input_text = recognize_speech()
        print("User:", input_text)

        # Add user's input to the conversation history
        conversation_history.append("User: " + input_text)

        chat_speaking = True
        toggle_image(chat_speaking)

        ints = predict_class(input_text)
        res = get_response(ints, intents)

        if "okay. Thank you for your cooperation. You will be contacted by a doctor soon." in res:
            speak_text(res)
            # Terminate the program gracefully
            window.quit()  # This closes the Tkinter window
            break  # This exits the chatbot loop

        speak_text(res)

        # Add chatbot's response to the conversation history
        conversation_history.append("Chatbot: " + res)

        chat_speaking = False
        toggle_image(chat_speaking)

    # Process the conversation history to extract patient information
    patient_name = None
    patient_age = None
    problem = None
    medication_history = "No medication"

    for utterance in conversation_history:
        if "User: my name is" in utterance:
            patient_name = utterance.split("User: my name is")[1].strip()
        elif "User: my age is" in utterance:
            patient_age = utterance.split("User: my age is")[1].strip()
        elif "User: I have" in utterance:
            problem = utterance.split("User: I have")[1].strip()
        elif "User: I take" in utterance:
            medication_history = utterance.split("User: I take")[1].strip()

    # Print the patient report
    print("\nPatient Report:")
    print("Patient Name:", patient_name)
    print("Patient Age:", patient_age)
    print("Problem:", problem)
    print("Medication History:", medication_history)

# Create a thread for the voice chatbot
chatbot_thread = threading.Thread(target=chatbot_voice)
chatbot_thread.daemon = True
chatbot_thread.start()

# Run the Tkinter main loop
window.mainloop()
