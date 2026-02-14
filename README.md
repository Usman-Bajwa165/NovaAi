# NOVA - AI Voice Assistant

NOVA is a privacy-focused voice assistant that runs entirely on your computer. Talk to it naturally, and it'll help you open apps, search the web, answer questions, and more—all while keeping your data local and secure.

## What Makes NOVA Different?

**Privacy First**: Your conversations never leave your machine. NOVA uses Ollama for AI processing, which runs completely offline. The only thing sent online is your voice audio for speech recognition (using Google's API)—everything else stays on your computer.

**Actually Useful**: NOVA doesn't just chat. It can open applications, search Google, check the weather, tell you the time, and execute real system commands. Just ask naturally: "Open Chrome and search for Python tutorials" or "What's the weather in London?"

**Smart Memory**: NOVA remembers your conversations in a local SQLite database, so it understands context and can have more natural back-and-forth discussions.

**Wake Word Activation**: Say "Nova" to activate it, press Enter, or click the microphone button. You'll hear a beep when it's listening.

## Getting Started

### What You'll Need

- Python 3.13 or newer
- A working microphone
- [Ollama](https://ollama.com/download) installed on your system
- Windows 10/11, macOS, or Linux

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd VoiceAi
   ```

2. **Set up a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\activate
   
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the AI model**
   ```bash
   ollama pull llama3.2:1b
   ```

5. **Run NOVA**
   ```bash
   python main.py
   ```

On first run, NOVA will calibrate your microphone automatically. Just stay quiet for a moment while it adjusts.

## How to Use NOVA

### Voice Commands

NOVA understands natural language. Here are some examples:

**Opening Applications**
- "Open Chrome"
- "Launch Calculator"
- "Start WhatsApp"

**Web Searches**
- "Search for Python tutorials"
- "Find the best laptops 2024"

**Weather & Time**
- "What's the weather in New York?"
- "What time is it?"
- "What's today's date?"

**General Questions**
- "Who are you?"
- "Tell me about yourself"

### Activation Methods

1. **Wake Word**: Say "Nova" and wait for the beep
2. **Keyboard**: Press Enter when the app is focused
3. **Mouse**: Click the microphone button

### User Accounts

NOVA requires you to create an account on first use. This is stored locally and encrypted with bcrypt. Your session persists between restarts—click "PURGE SESSION" to log out.

## Project Structure

```
VoiceAi/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── src/
│   ├── ai_engine.py     # AI response generation (Ollama)
│   ├── voice_engine.py  # Speech recognition and TTS
│   ├── actions.py       # System commands (apps, search, etc.)
│   ├── auth.py          # User authentication
│   ├── database.py      # SQLite operations
│   └── logger.py        # Logging system
├── ui/
│   ├── index.html       # Main interface
│   ├── style.css        # Styling
│   └── script.js        # Frontend logic
└── logs/                # Application logs (auto-created)
```

**Auto-generated files** (not in git):
- `voice_ai.db` - User accounts and conversation memory
- `session.json` - Login session persistence
- `config.json` - Microphone calibration settings

## Technical Details

### How It Works

1. **You speak**: Your voice is captured via your microphone
2. **Speech-to-Text**: Audio is sent to Google's Speech Recognition API
3. **Intent Processing**: NOVA analyzes your request locally using Ollama
4. **Action Execution**: If you asked to open an app or search, NOVA does it
5. **Response Generation**: NOVA formulates a reply using AI
6. **Text-to-Speech**: The response is spoken using Microsoft Edge TTS
7. **Memory Storage**: The conversation is saved locally for context

### Technologies Used

- **Python 3.13+**: Core language
- **Ollama (llama3.2:1b)**: Local AI model for response generation
- **SpeechRecognition**: Voice input processing
- **Edge-TTS**: Neural voice synthesis (Guy voice)
- **pywebview**: Native desktop window
- **SQLite**: Local database for users and memory
- **bcrypt**: Password encryption
- **pygame**: Audio playback

### Performance

- **Response time**: 4-8 seconds end-to-end
- **AI processing**: 2-4 seconds (depends on your CPU)
- **Memory usage**: ~500MB with model loaded
- **Disk space**: ~2GB for AI model

## Customization

### Change NOVA's Voice

Edit `src/voice_engine.py` and change the voice parameter:
```python
"--voice", "en-US-AriaNeural",  # Female voice
"--voice", "en-GB-RyanNeural",  # British male
```

See [Edge-TTS voices](https://github.com/rany2/edge-tts#voice-list) for all options.

### Add More Applications

Edit `src/actions.py` and add to the `app_mapping` dictionary:
```python
app_mapping = {
    "spotify": "spotify.exe",
    "your-app": "your-app.exe",
}
```

### Adjust AI Behavior

Edit `src/ai_engine.py` to modify the system prompt or model parameters:
```python
model="llama3.2:1b"      # Try llama3.2:3b for better quality
temperature=0.4          # Lower = more focused, higher = more creative
num_predict=60           # Max response length in tokens
```

## Troubleshooting

**Microphone not working?**
- Check Windows microphone permissions
- Delete `config.json` and restart to recalibrate
- Make sure no other app is using the microphone

**Ollama errors?**
In powershell/cmd:
- Verify installation: `ollama --version`
- Ensure model is downloaded: `ollama pull llama3.2:1b`
- Test it: `ollama run llama3.2:1b "Hello"`
- To run app do: `ollama server`

**Slow responses?**
- Close other heavy applications
- Try a smaller model or upgrade your CPU
- Check if Ollama is using GPU acceleration

**Session not saving?**
- Ensure the app has write permissions in its directory
- Check if `session.json` exists after login
- Try clicking "PURGE SESSION" and logging in again

## Privacy & Security

**What stays local:**
- All AI processing (Ollama runs on your machine)
- Your conversation history
- User accounts and passwords (bcrypt encrypted)
- All system actions and commands

**What goes online:**
- Voice audio for speech recognition (Google STT API)
- Web searches and website opens (when you request them)

NOVA never sends your conversation history, user data, or AI processing to any server.

## Contributing

Contributions are welcome! If you'd like to add features or fix bugs:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details. Free to use for personal or commercial projects.

## Credits

Developed by **Usman Bajwa**

Built with:
- [Ollama](https://ollama.com/) - Local AI models
- [Google Speech Recognition](https://cloud.google.com/speech-to-text) - Voice input
- [Edge-TTS](https://github.com/rany2/edge-tts) - Voice synthesis
- [pywebview](https://pywebview.flowrl.com/) - Desktop UI

---

**Version**: 2.0.0  
**Status**: Production Ready
