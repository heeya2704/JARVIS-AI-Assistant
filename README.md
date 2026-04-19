Jarvis AI Assistant

Jarvis is a voice-activated AI assistant built using Python, designed to perform real-time tasks through speech interaction. It integrates modern AI capabilities with a user-friendly interface to provide a seamless and intelligent assistant experience.

The assistant uses hotword detection (e.g., "Hey Jarvis") to activate and can process voice commands to perform actions like answering queries, fetching real-time information, and automating basic tasks.

🚀 Features
🎤 Voice Activation using hotword detection ("Hey Jarvis")
🧠 AI-Powered Responses via Groq API
🌐 Real-time Web Search Integration
🖥️ GUI Interface built with PyQt5
⚡ Fast Processing with optimized backend
🔊 Speech-to-Text & Text-to-Speech
🛠️ Tech Stack
Python
Groq API (LLM Integration)
PyQt5 (GUI)
SpeechRecognition / TTS Libraries
Web APIs for real-time data
📌 Use Cases
Personal productivity assistant
Voice-controlled system operations
Quick information retrieval
AI-powered conversation
📂 Project Goal

The goal of Jarvis is to create a scalable, real-time AI assistant that combines voice interaction, intelligent responses, and automation into a single system.


Installation & Setup Guide

Follow these steps to set up and run the Jarvis AI Assistant locally:

1️⃣ Clone the Repository
git clone https://github.com/your-username/jarvis-ai-assistant.git
cd jarvis-ai-assistant
2️⃣ Create Virtual Environment (Recommended)
python -m venv venv

Activate it:

Windows
venv\Scripts\activate
Mac/Linux
source venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt

If requirements.txt is not available, install manually:

pip install pyqt5 speechrecognition pyttsx3 requests pyaudio
4️⃣ Setup API Keys 🔑
Create a .env file in the root directory
Add your API keys:
GROQ_API_KEY=your_groq_api_key_here

(Optional: add other APIs if used for web search)

Install dotenv if needed:

pip install python-dotenv
5️⃣ Run the Assistant
python main.py
6️⃣ Usage
Launch the app
Say "Hey Jarvis" to activate
Speak your command 🎤
⚠️ Common Issues & Fixes

PyAudio Installation Error (Windows):

pip install pipwin
pipwin install pyaudio

Microphone Not Detected:

Check system microphone permissions
Ensure correct input device is selected

Slow Response:

Check internet connection
Verify API key is valid
