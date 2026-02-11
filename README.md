# JARVIS - VoiceAi Agent 🤖

A premium, JARVIS-inspired AI voice agent that listens, learns, and acts. Built with Python 3.13.5 and a modern glowing web interface.

## ✨ Core Features

### 🎙️ Advanced Voice Intelligence

- **Voice-to-Voice Loop**: Real-time speech recognition (STT) and professional neural voice synthesis (TTS) using Edge-TTS.
- **Continuous Learning**: Stores every interaction in a local SQLite memory system, allowing JARVIS to recall past context and "learn" about you.
- **Intent Recognition**: Powered by Google Gemini 1.5 Flash for witty, intelligent, and context-aware responses.

### 🛡️ Secure User System

- **Authorized Access**: Secure login system requiring email and a minimum 7-character password.
- **Smart Onboarding**: Automatically detects if you need an account and guides you through initialization.
- **Privacy First**: All data and memory are stored locally on your machine in `voice_ai.db`.

### ⚡ System Actions (The "Acts")

JARVIS doesn't just talk; he takes action. You can command him to:

- "Open Chrome"
- "Launch Notepad"
- "Start the Calculator"
- "Open Microsoft Edge"
- ...and more. He uses system-level hooks to execute your requests smoothly.

### 💎 Professional UI/UX

- **Futuristic Aesthetic**: Glassmorphism, glowing visualizer, and rotating HUD elements.
- **Live Status**: Real-time synchronization between what JARVIS is doing (Listening, Analyzing, Acting) and the UI.
- **Integrated Chat**: Visual log of your conversation alongside the voice interaction.

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.13.5** installed.
- **Microphone**: Ensure your default system mic is active.
- **Gemini API Key**: Obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Installation

Navigate to the project directory and install the requirements:

```bash
# It is recommended to use the virtual environment already set up
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration

Rename `.env.example` to `.env` and paste your Gemini API key:

```env
GEMINI_API_KEY=your_key_here
```

### 4. Launch

Run the main application:

```bash
python main.py
```

---

## 🛠️ Commands for Testing

- **Greeting**: "Hello Jarvis, how are you today?"
- **Action**: "Jarvis, please open Chrome for me."
- **Memory**: "My name is John. Remember that." (Then later ask: "What is my name?")
- **System**: "Launch the calculator."

---

## 🛡️ Robustness & Stability

- **Multi-threaded**: Audio processing runs in background threads to keep the UI perfectly smooth.
- **Error Handling**: Graceful fallback if the microphone is busy or the API is offline.
- **Clean Cleanup**: Automatic temporary audio file management to prevent disk clutter.
