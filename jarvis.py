# pip install pyaudio

import pyttsx3 #pip install pyttsx3
import speech_recognition as sr #pip install speechRecognition
import datetime
import wikipedia #pip install wikipedia
import webbrowser
import os
import smtplib
import pywhatkit as kit
import sys

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
# print(voices[1].id)
engine.setProperty('voice', voices[1].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    speak("Jai Shree Ram!")
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Su Prabhat!")

    elif hour>=12 and hour<18:
        speak("Radhe Radhe!")   

    else:
        speak("Jai Shree Krishna!")  

    speak("I am Kalua. Sir Please tell me how may I help you")       

def takeCommand():
    #It takes microphone input from the user and returns string output

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)    
        print("Say that again please...")  
        return "None"
    return query

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('youremail@gmail.com', 'your-password')
    server.sendmail('youremail@gmail.com', to, content)
    server.close()

if __name__ == "__main__":
    wishMe()
    while True:
    # if 1:
        query = takeCommand().lower()

        # Logic for executing tasks based on query
        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'open youtube' in query:
            webbrowser.open("youtube.com")

        elif 'open google' in query:
            webbrowser.open("google.com")

        elif 'search' in query:
            speak(query)
            content = query.replace("search", "")
            webbrowser.open(f"https://google.com/search?q={content}")

        elif 'open stackoverflow' in query:
            webbrowser.open("stackoverflow.com")   

        elif 'search on youtube' in query:
            speak('Searching on Youtube.....')
            song_name = query.replace("search on youtube","").strip()
            webbrowser.open(f"https://youtube.com/search?q={song_name} song")
        elif 'play music' in query:
            speak('Searching Song.....')
            song_name = query.replace("play music","").strip()
            #webbrowser.open(f"https://youtube.com/search?q={song_name} song")
            kit.playonyt(song_name)

        elif 'exit' in query:
            speak(query)
            sys.exit()

        # elif query:
        #     speak(query)
        #     webbrowser.open(f"https://google.com/search?q={query}")

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")    
            speak(f"Sir, the time is {strTime}")

        elif 'open code' in query:
            codePath = "C:/Users/91860/AppData/Local/Programs/Python/Python313/python.exe"
            os.startfile(codePath)

        elif 'email to vinayak' in query:
            try:
                speak("What should I say?")
                content = takeCommand()
                to = "vinayaksh2408@gmail.com"    
                sendEmail(to, content)
                speak("Email has been sent!")
            except Exception as e:
                print(e)
                speak("Sorry my friend Vinayak. I am not able to send this email")    
        else:
            print("No query matched")
            sys.exit()