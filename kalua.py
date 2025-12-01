import os
import sys
import subprocess
import json
import threading
import datetime
import time
import webbrowser
import tempfile
from typing import Tuple

import pyttsx3
import speech_recognition as sr
import wikipedia
import pywhatkit as kit
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------
# Configuration (env overrides)
# ---------------------------
VOICE_ID_INDEX = int(os.getenv("VOICE_ID_INDEX"))
LISTEN_TIMEOUT = int(os.getenv("LISTEN_TIMEOUT"))
ENERGY_THRESHOLD = int(os.getenv("ENERGY_THRESHOLD"))
FLASK_PORT = int(os.getenv("FLASK_PORT"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = os.getenv("GEMINI_URL", "")  # optional: used to open browser if you want

# ---------------------------
# TTS init
# ---------------------------
engine = pyttsx3.init()
voices = engine.getProperty("voices")
if len(voices) > VOICE_ID_INDEX:
    engine.setProperty("voice", voices[VOICE_ID_INDEX].id)

def speak(text: str):
    print(f"[Kalua] {text}")
    engine.say(text)
    engine.runAndWait()

# ---------------------------
# LLM (Gemini) helper
# ---------------------------
def ask_gemini(prompt: str, prefer_open_browser: bool = False) -> str:
    """
    If GEMINI_API_KEY is set, call the configured endpoint.
    Otherwise, return empty string (caller will open web search).
    prefer_open_browser: if True and GEMINI_URL is set, open browser to that URL (for transparency).
    """
    speak("Contacting online assistant...")
    if prefer_open_browser and GEMINI_URL:
        # Open the Gemini/LLM URL with a search query param if sensible
        try:
            # attempt to craft a visible query URL (this is a best-effort UX; provider-specific)
            q = prompt.replace(" ", "+")
            webbrowser.open(f"{GEMINI_URL}?q={q}")
        except Exception:
            pass

    if not GEMINI_API_KEY:
        return ""  # indicate not configured

    try:
        # Example generic call: adapt to your provider. This is a generic JSON POST.
        headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "prompt": prompt,
            "max_tokens": 800,
        }
        r = requests.post(GEMINI_URL, json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            # adapt this extraction to the provider response schema:
            # check common keys:
            for key in ("text", "response", "output", "result", "reply"):
                if key in data:
                    return data[key]
            # fallback: return stringified json
            return json.dumps(data)
        else:
            return f"(LLM error {r.status_code}) {r.text}"
    except Exception as e:
        return f"(LLM call failed) {e}"

# ---------------------------
# Helpers for Notepad/code flow
# ---------------------------
EXT_MAP = {
    "python": ".py",
    "py": ".py",
    "javascript": ".js",
    "js": ".js",
    "html": ".html",
    "css": ".css",
    "c++": ".cpp",
    "cpp": ".cpp",
    "c": ".c",
    "java": ".java",
    "bash": ".sh",
    "shell": ".sh",
    "json": ".json",
    "txt": ".txt",
}

def infer_extension_from_text(text: str) -> str:
    # basic language keywords -> extension
    t = text.lower()
    for k in EXT_MAP:
        if k in t:
            return EXT_MAP[k]
    # fallback to .txt
    return ".txt"

def save_code_to_tempfile(code_text: str, ext: str = ".txt") -> str:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fd, path = tempfile.mkstemp(prefix=f"kalua_{ts}_", suffix=ext)
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(code_text)
    return path

def open_in_notepad(file_path: str):
    """
    Open the given file in Notepad (Windows). Uses notepad.exe for reliable behavior.
    On other OSes, fallback to default opener.
    """
    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(["notepad.exe", file_path])
        else:
            # try default OS opener (Linux/macOS)
            if sys.platform.startswith("darwin"):
                subprocess.Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])
    except Exception as e:
        speak(f"Could not open editor: {e}")
        # fallback: try os.startfile on Windows
        try:
            os.startfile(file_path)
        except Exception:
            pass

# ---------------------------
# Command handling
# ---------------------------
def handle_notepad_write(full_text: str) -> str:
    """
    Detect intent like:
      - 'open notepad and write a python function to reverse a string'
      - 'open notepad and write html for a contact form'
    Steps:
      1) extract the 'write' prompt (text after 'write' or 'type')
      2) ask Gemini (if configured) to generate code for that prompt
      3) save to temp file with sensible extension
      4) open Notepad with that file and speak status
    """
    q = full_text.lower()
    # find 'write' or 'type' or 'create' keyword
    trigger_words = ["write", "type", "create", "generate"]
    trigger_index = -1
    trigger_word_used = None
    for tw in trigger_words:
        if f" {tw} " in q:
            trigger_index = q.index(f" {tw} ")
            trigger_word_used = tw
            break
    if trigger_index == -1:
        # if user said "open notepad and [something]" try after 'and'
        if " and " in q:
            # heuristic
            parts = q.split(" and ", 1)
            if len(parts) > 1:
                prompt = parts[1].strip()
            else:
                prompt = ""
        else:
            prompt = ""
    else:
        prompt = full_text[trigger_index + len(trigger_word_used) + 1 :].strip()

    if not prompt:
        return "I didn't catch what to write in notepad. Please say, for example: open notepad and write a python function to reverse a string."

    speak(f"Preparing to write to Notepad: {prompt}")

    # If GEMINI_API_KEY configured call it; otherwise open browser search to show Gemini/search results
    generated = ""
    if GEMINI_API_KEY and GEMINI_URL:
        # call LLM
        generated = ask_gemini(prompt, prefer_open_browser=True)
    else:
        # open browser to search for the prompt (user asked to open browser + gemini)
        try:
            # search query emphasizes 'code' and 'gemini' to surface relevant pages
            qparam = f"{prompt} code"
            webbrowser.open(f"https://www.google.com/search?q={qparam.replace(' ', '+')}")
            speak("Gemini API not configured. I opened a browser search for you. If you want me to auto-generate code here, set the GEMINI_API_KEY and GEMINI_URL environment variables.")
        except Exception:
            pass
        # we do not have a generated code — ask user to speak or type the content for Notepad
        # For a smoother UX, we can ask the user to repeat or say 'paste this' after copying from browser.
        # Return now to avoid writing empty file.
        return "Opened browser to search for code (Gemini not configured). If you want me to generate code directly, set GEMINI_API_KEY and GEMINI_URL."

    # At this point, 'generated' may be empty or contain the LLM reply
    if not generated:
        return "I couldn't get a response from the online assistant."

    # Decide extension
    ext = infer_extension_from_text(prompt)
    file_path = save_code_to_tempfile(generated, ext=ext)
    open_in_notepad(file_path)
    speak(f"I saved the generated code to {os.path.basename(file_path)} and opened it in Notepad.")
    return f"Generated code saved to {file_path}"

# keep a small allowlist for other safe shell commands if you want
safe_shell_commands = {
    "notepad": ["notepad.exe"],
    "calc": ["calc.exe"],
    "explorer": ["explorer.exe"],
}

def run_shell_command(cmd_name: str) -> Tuple[bool, str]:
    key = cmd_name.lower().strip()
    if key in safe_shell_commands:
        args = [os.path.expandvars(a) for a in safe_shell_commands[key]]
        try:
            subprocess.Popen(args)
            return True, f"Started {key}."
        except Exception as e:
            return False, f"Failed to start {key}: {e}"
    else:
        return False, "Command not in safe list."

def handle_command_text(text: str) -> str:
    if not text:
        return "I didn't catch that."

    q = text.lower().strip()
    print(f"[handle] {q}")

    # Notepad + write flow
    if "notepad" in q and any(w in q for w in ["write", "type", "create", "generate"]):
        return handle_notepad_write(text)

    # simple open notepad
    if q.startswith("open notepad") or q == "open notepad":
        ok, msg = run_shell_command("notepad")
        if ok:
            return "Opening Notepad."
        else:
            return msg

    # Wikipedia
    if "wikipedia" in q:
        topic = q.replace("wikipedia", "").strip()
        if not topic:
            return "What should I search on Wikipedia?"
        try:
            summary = wikipedia.summary(topic, sentences=2)
            return f"Wikipedia: {summary}"
        except Exception as e:
            return f"Wikipedia lookup failed: {e}"

    # Open websites
    if q.startswith("open "):
        target = q.replace("open ", "").strip()
        mapping = {
            "youtube": "https://youtube.com",
            "google": "https://google.com",
            "stackoverflow": "https://stackoverflow.com",
            "github": "https://github.com",
        }
        if target in mapping:
            webbrowser.open(mapping[target])
            return f"Opening {target}."
        if "." in target or target.startswith("http"):
            url = target if target.startswith("http") else f"https://{target}"
            webbrowser.open(url)
            return f"Opening {url}"
        ok, msg = run_shell_command(target)
        return msg

    # Search (web)
    if q.startswith("search ") or q.startswith("google "):
        term = q.split(" ", 1)[1]
        url = f"https://www.google.com/search?q={term.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching Google for {term}."

    # Play music / youtube
    if q.startswith("play ") or "play music" in q:
        song = q.replace("play", "").replace("music", "").strip()
        if not song:
            return "Which song should I play?"
        try:
            kit.playonyt(song)
            return f"Playing {song} on YouTube."
        except Exception as e:
            return f"Failed to play song: {e}"

    # Time
    if "time" in q:
        t = datetime.datetime.now().strftime("%H:%M:%S")
        return f"The time is {t}"

    # Ask Gemini / online assistant (general)
    if q.startswith("ask ") or q.startswith("gemini ") or q.startswith("research "):
        prompt = q.split(" ", 1)[1] if " " in q else q
        resp = ask_gemini(prompt, prefer_open_browser=True)
        return resp or "No response from online assistant."

    if "shutdown" in q or "restart" in q:
        return "For safety I won't perform shutdown/restart. Please run that manually."

    if q in ("exit", "quit", "stop", "bye"):
        speak("Goodbye!")
        sys.exit(0)

    # fallback
    return f"I don't have a direct action for that. I can search the web for: {text}"

# ---------------------------
# Speech recognition (local)
# ---------------------------
def takeCommand() -> str:
    r = sr.Recognizer()
    r.energy_threshold = ENERGY_THRESHOLD
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.6)
        audio = None
        try:
            audio = r.listen(source, timeout=LISTEN_TIMEOUT, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("No speech detected (timeout).")
            return ""
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(f"User said: {query}")
        return query
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return ""
    except sr.RequestError as e:
        print(f"Recognition request failed: {e}")
        return ""

# ---------------------------
# Flask API (optional)
# ---------------------------
app = Flask(__name__)

@app.route("/api/command", methods=["POST"])
def api_command():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text") or ""
    if not text:
        return jsonify({"error": "No text provided."}), 400
    result = handle_command_text(text)
    return jsonify({"result": result})

@app.route("/api/ask_gemini", methods=["POST"])
def api_ask_gemini():
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get("prompt") or ""
    if not prompt:
        return jsonify({"error": "No prompt provided."}), 400
    resp = ask_gemini(prompt, prefer_open_browser=True)
    return jsonify({"result": resp})

def run_flask():
    app.run(host="0.0.0.0", port=FLASK_PORT, debug=False)

# ---------------------------
# Main flow
# ---------------------------
def wish_me():
    speak("Jai Shree Ram!")
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Su Prabhat!")
    elif 12 <= hour < 18:
        speak("Radhe Radhe!")
    else:
        speak("Jai Shree Krishna!")
    speak("I am Kalua. Please tell me how may I help you.")

def voice_loop():
    wish_me()
    while True:
        query = takeCommand()
        if not query:
            print("No input — listening again...")
            continue
        result = handle_command_text(query)
        speak(result)
        time.sleep(0.6)

if __name__ == "__main__":
    if os.environ.get("RUN_FLASK", "") == "1":
        t = threading.Thread(target=run_flask, daemon=True)
        t.start()
        print(f"Flask API running on http://localhost:{FLASK_PORT}")
    try:
        voice_loop()
    except KeyboardInterrupt:
        print("Exiting by user request.")
        sys.exit(0)
