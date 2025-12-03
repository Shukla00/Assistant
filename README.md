

# **Kalua – AI Voice Assistant (Local + Gemini Powered + Notepad Code Writer)**

Kalua is a lightweight but powerful desktop voice assistant written in Python.
It supports:

* 🎤 **Voice control** (open apps, search web, get time, play YouTube music, etc.)
* ✍️ **“Open Notepad and write…” command** → generates code using Gemini (optional) and opens it in Notepad
* 🌐 **Built-in Flask API** (optional) to allow browser or external apps to send text commands
* 🗣️ Indian-accent optimized speech recognition
* 🔧 Works **offline** for local tasks
* ☁️ Works **online** with Gemini / LLM integration (if configured)

*No database is used—simple and clean.*

---

## 🚀 Features

### **1. Voice Commands (Offline)**

* “**Open YouTube**”
* “**Search for Python decorators**”
* “**Play music Shape of You**”
* “**What is the time?**”
* “**Open Notepad**”

### **2. Smart Notepad Code Writer (Online/Offline)**

You can say:

> **“Open notepad and write a Python function to reverse a string”**
> **“Open notepad and write HTML for a contact form”**

If Gemini API is configured:

* Kalua sends the prompt to Gemini
* Gemini returns code
* Kalua saves it in a temp file → opens it in Notepad automatically

If Gemini is **not configured**:

* Browser search opens
* Kalua informs you to configure Gemini for auto-generation

### **3. Optional API Mode**

Enable Flask API to allow:

* Browser UI
* Mobile/desktop apps
* Web extensions

to control your assistant.

### **4. Safety**

* Only safe apps are allowed to launch
* Shutdown/restart are disabled
* No shell execution beyond the allowlist

---

# 📦 Installation

### **1. Clone or download the project**

```
git clone https://github.com/Shukla00/Assistant.git
cd Assistant
```

### **2. Install Python packages**

```
pip install pyttsx3 SpeechRecognition wikipedia pywhatkit Flask requests python-dotenv
```

### **3. (Windows) Install PyAudio**

```
pip install pipwin
pipwin install pyaudio
```

Linux:

```
sudo apt install python3-pyaudio
```

---

# ⚙️ Environment Setup

Create a file named **`.env`** in the same folder as `kalua.py`.

```
RUN_FLASK=1
FLASK_PORT=5000

# Gemini / LLM Integration (optional)
GEMINI_API_KEY=
GEMINI_URL=

# Voice settings
VOICE_ID_INDEX=1
ENERGY_THRESHOLD=300
LISTEN_TIMEOUT=6
```

If you don’t set GEMINI_API_KEY, Kalua will still work, but code-writing will fallback to browser search.

---

# ▶️ Running the Assistant

## **Voice Only Mode**

```
python kalua.py
```

## **Voice + Flask API Mode**

Windows PowerShell:

```
$env:RUN_FLASK=1; python kalua.py or jarvis.py
```

Linux/macOS:

```
RUN_FLASK=1 python kalua.py
```

The API will be available at:

```
http://localhost:5000/api/command
```

---

# 🧪 Example Voice Commands

### 🎤 General

* “**Jai Shree Ram**”
* “**Open Google**”
* “**Search Python OOP**”
* “**Play music Believer**”
* “**What's the time?**”

### 🤖 Gemini / AI tasks

* “**Ask Gemini explain what recursion is**”
* “**Research best laptops 2025**”

### 📝 Notepad Code Writing

* “**Open notepad and write a Python function for Fibonacci**”
* “**Open notepad and create HTML login page**”
* “**Open notepad and generate C++ code for bubble sort**”

---

# 🧩 Project Structure

```
kalua-assistant/
│
├── kalua.py      # Main assistant logic
├── README.md         # Documentation
└── .env              # Environment variables (you create this)
```

---

# 🔐 Security Notes

* Flask API is **local only**—do NOT expose publicly without authentication.
* Shell commands are **restricted** by allowlist.
* No system-destructive commands (shutdown/reboot).
* Gemini requests only happen if API key is provided.

---

# ⭐ Future Enhancements (Optional)

If you want, I can help you add:

* MongoDB logging (disabled by request)
* Visual Studio Code integration instead of Notepad
* Tray icon + global hotkey (Ctrl+Shift+K to activate Kalua)
* Full React dashboard
* Wake-word detection (“Hey Kalua”)
* Offline LLM integration (GPT4All / llama.cpp)

Just ask anytime. 🙏

---

# 🙌 Credits

Built with ❤️ using Python, SpeechRecognition, pyttsx3, Flask, and Gemini integration.

