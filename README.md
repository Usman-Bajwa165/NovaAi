# NOVA - Professional AI Voice Assistant 🤖

A premium, locally-running AI voice assistant that listens, learns, and acts. Built with Python 3.13+ and powered by Ollama for complete offline functionality.

## ✨ Key Features

### 🎙️ Advanced Voice Intelligence
- **Voice-to-Voice Loop**: Real-time speech recognition (Google STT) and professional neural voice synthesis (Edge-TTS)
- **Continuous Learning**: Stores every interaction in local SQLite memory for contextual conversations
- **Intent Recognition**: Powered by Ollama (llama3.2:1b) for intelligent, context-aware responses
- **100% Offline AI**: All AI processing happens locally on your machine

### 🛡️ Secure User System
- **Authorized Access**: Secure login with email and password (bcrypt encrypted)
- **Smart Onboarding**: Automatic account creation and guided setup
- **Privacy First**: All data stored locally in `voice_ai.db` and `session.json`
- **Persistent Sessions**: Auto-login on restart until you click "PURGE SESSION"

### ⚡ System Actions
NOVA doesn't just talk; she takes action:
- **Open Apps**: "Open Chrome", "Launch Calculator", "Start WhatsApp"
- **Web Search**: "Search Python tutorials", "Find best laptops 2024"
- **Weather**: "Tell me temperature in Bahawalpur Pakistan"
- **Websites**: "Open YouTube", "Go to SoundCloud"
- **Time/Date**: "What time is it", "What's today's date"

### 💎 Professional UI/UX
- **Futuristic Design**: Glassmorphism, glowing visualizer, rotating HUD elements
- **Live Status**: Real-time feedback (🎤 Listening, 🧠 Processing, 💬 Responding)
- **Word Streaming**: Text appears as NOVA speaks (subtitle effect)
- **Responsive**: Works on desktop and adapts to different screen sizes

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+** installed
- **Microphone**: Ensure your default system mic is active
- **Ollama**: Download from [ollama.com](https://ollama.com/download)

### Installation

```bash
# Navigate to project
cd VoiceAi

# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Pull Ollama model
ollama pull llama3.2:1b

# Run NOVA
python main.py
```

---

## 🎯 Usage Examples

### Voice Commands
```
"Open Chrome"                    → Launches Google Chrome
"Search Python tutorials"        → Opens Google search
"Tell me weather in London"      → Opens weather info
"What time is it"                → Tells current time
"Open YouTube"                   → Opens youtube.com
"Who are you"                    → NOVA introduces herself
```

### Keyboard Shortcuts
- **Enter**: Start/stop listening (when in agent screen)
- **Click Mic Button**: Manual voice activation

---

## 🏗️ Architecture

### Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (Glassmorphism UI)
- **Backend**: Python 3.13+
- **AI Engine**: Ollama (llama3.2:1b) - 100% offline
- **Speech Recognition**: Google Speech Recognition API
- **Text-to-Speech**: Edge-TTS (Microsoft Neural Voices)
- **Database**: SQLite3 (local storage)
- **Authentication**: bcrypt password hashing
- **UI Framework**: pywebview (native window)

### Project Structure
```
VoiceAi/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── voice_ai.db            # SQLite database (auto-created)
├── session.json           # Persistent session (auto-created)
├── config.json            # Microphone config (auto-created)
│
├── src/                   # Backend source code
│   ├── ai_engine.py       # AI brain - generates responses
│   ├── voice_engine.py    # Voice input/output handling
│   ├── actions.py         # System commands (open apps, search)
│   ├── auth.py            # User login/signup
│   ├── database.py        # Database operations
│   └── logger.py          # Logging system
│
├── ui/                    # Frontend interface
│   ├── index.html         # Main UI structure
│   ├── style.css          # Visual styling
│   └── script.js          # User interaction logic
│
└── logs/                  # Application logs
    └── nova.log           # Error and info logs
```

---

## 🔐 Privacy & Security

### Data Storage
- ✅ **100% Local**: All AI processing happens on your machine
- ✅ **No Cloud**: Ollama runs completely offline
- ✅ **Encrypted Passwords**: bcrypt hashing for user credentials
- ✅ **Local Database**: SQLite stores all data locally
- ✅ **Session Control**: Clear session anytime with "PURGE SESSION"

### What Gets Sent Online?
- **Speech Recognition**: Audio sent to Google STT API (required for voice input)
- **Nothing Else**: All AI, memory, and actions are 100% local

---

## ⚙️ Configuration

### Microphone Settings
Auto-calibrated on first run. To recalibrate:
```bash
# Delete config and restart
del config.json  # Windows
rm config.json   # Mac/Linux
python main.py
```

### AI Model Settings
Edit `src/ai_engine.py`:
```python
model="llama3.2:1b"      # Fast, lightweight
temperature=0.4          # Response creativity
num_predict=60           # Response length
```

### Voice Settings
Edit `src/voice_engine.py`:
```python
pause_threshold=2.0      # Silence before stopping
timeout=8                # Max wait for speech start
```

---

## 🔧 Troubleshooting

### Microphone Not Working
1. Check Windows microphone permissions
2. Delete `config.json` to force recalibration
3. Restart application

### Ollama Not Responding
1. Ensure Ollama is installed: `ollama --version`
2. Pull the model: `ollama pull llama3.2:1b`
3. Test: `ollama run llama3.2:1b "Hello"`

### Session Not Persisting
1. Check if `session.json` exists
2. Ensure write permissions in project folder
3. Click "PURGE SESSION" and login again

### Slow Responses
1. Upgrade model: `ollama pull llama3.2:3b`
2. Check CPU usage during processing
3. Close other heavy applications

---

## 📊 Performance

### Response Times
- **Listening**: < 1 second to start
- **Processing**: 2-4 seconds (Ollama)
- **Speaking**: 1-3 seconds (TTS)
- **Total**: 4-8 seconds end-to-end

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB for models
- **OS**: Windows 10/11, macOS, Linux

---

## 🎨 Customization

### Change Agent Name
Edit `src/ai_engine.py`:
```python
NOVA_INFO = {
    "name": "YOUR_NAME",
    "developer": "Your Name",
    ...
}
```

### Add New Apps
Edit `src/actions.py`:
```python
app_mapping = {
    "myapp": "myapp.exe",  # Add your app
}
```

### Change Voice
Edit `src/voice_engine.py`:
```python
"--voice", "en-US-AriaNeural",  # Change to any Edge-TTS voice
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - feel free to use for personal or commercial projects.

---

## 👨‍💻 Developer

**Usman Bajwa**
- Professional AI Voice Agent Developer
- Specialized in offline AI systems
- Privacy-focused solutions

---

## 🙏 Acknowledgments

- **Ollama**: For amazing local AI models
- **Google**: Speech Recognition API
- **Microsoft**: Edge-TTS neural voices
- **Python Community**: For excellent libraries

---

## 📚 Documentation

- [Technical Documentation](TECHNICAL_DOCUMENTATION.md) - Complete technical guide
- [API Documentation](docs/API.md) - Backend API reference (coming soon)
- [UI Guide](docs/UI.md) - Frontend customization (coming soon)

---

**Version**: 2.0.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅
