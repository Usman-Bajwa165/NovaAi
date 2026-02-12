# NOVA Quick Start Guide 🚀

## 5-Minute Setup

### Step 1: Install Ollama
1. Download from: https://ollama.com/download
2. Install and run Ollama
3. Open terminal and run:
   ```bash
   ollama pull llama3.2:1b
   ```

### Step 2: Start NOVA
1. Open terminal in VoiceAi folder
2. Activate virtual environment:
   ```bash
   venv\Scripts\activate
   ```
3. Run:
   ```bash
   python main.py
   ```

### Step 3: First Login
1. Click "ACCESS INTERFACE"
2. Click "Register" (first time only)
3. Enter email and password (min 7 characters)
4. Login automatically saves - no need to login again!

### Step 4: Start Talking
1. Click the microphone button (or press Enter)
2. Wait for "🎤 LISTENING..."
3. Speak your command clearly
4. Wait for NOVA to respond

## Common Commands

### Open Apps
```
"Open Chrome"
"Launch Calculator"
"Start Notepad"
"Open WhatsApp"
```

### Search Web
```
"Search for Python tutorials"
"Find best laptops 2024"
"Search weather in London"
```

### Get Information
```
"What time is it"
"What's today's date"
"Tell me weather in Paris"
```

### Websites
```
"Open YouTube"
"Go to Google"
"Open SoundCloud"
```

## Tips for Best Results

### Speaking Tips
✅ **DO:**
- Speak clearly and at normal pace
- Wait for "🎤 LISTENING..." before speaking
- Pause 1 second after finishing
- Use natural language

❌ **DON'T:**
- Speak too fast or mumble
- Start speaking before "🎤 LISTENING..."
- Speak in a noisy environment
- Use very long sentences (keep under 15 words)

### Command Tips
✅ **Good Commands:**
- "Open Chrome" (clear, direct)
- "Search for Python" (specific)
- "What time is it" (simple)

❌ **Bad Commands:**
- "Um, can you maybe like open Chrome if possible" (too wordy)
- "Chrome" (too vague)
- "Open that browser thing" (unclear)

## Troubleshooting

### Problem: Microphone not working
**Solution:**
1. Run: `python test_mic.py`
2. Check Windows microphone permissions
3. Delete `config.json` and restart

### Problem: NOVA not responding
**Solution:**
1. Check if Ollama is running: `ollama --version`
2. Verify model is installed: `ollama list`
3. Test model: `ollama run llama3.2:1b "Hello"`

### Problem: Slow responses
**Solution:**
1. Close other heavy applications
2. Upgrade to better model: `ollama pull llama3.2:3b`
3. Check CPU usage in Task Manager

### Problem: Session not saving
**Solution:**
1. Check if `session.json` exists in folder
2. Ensure you have write permissions
3. Click "PURGE SESSION" and login again

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Start/stop listening |
| Esc | Close modal |

## Status Indicators

| Icon | Meaning |
|------|---------|
| 🎤 LISTENING | Capturing your voice |
| 🧠 THINKING | Processing with AI |
| 💬 RESPONDING | Speaking answer |
| ⚙️ CALIBRATING | Setting up microphone |
| ✅ STANDBY | Ready for next command |

## Performance Expectations

### Normal Response Time
- Listening: < 1 second
- Processing: 2-4 seconds
- Speaking: 1-3 seconds
- **Total: 4-8 seconds**

### If Slower Than Expected
1. Check CPU usage (should be < 80%)
2. Close background apps
3. Restart NOVA
4. Consider upgrading model

## Privacy & Security

### What's Stored Locally
- ✅ User credentials (encrypted)
- ✅ Conversation history
- ✅ Session data
- ✅ Microphone settings

### What's Sent Online
- ⚠️ Voice audio (to Google STT only)
- ❌ Nothing else!

### How to Clear Data
1. **Clear Session**: Click "PURGE SESSION"
2. **Clear Memory**: Delete `voice_ai.db`
3. **Clear All**: Delete `session.json`, `config.json`, `voice_ai.db`

## Advanced Usage

### Change AI Model
Edit `src/ai_engine.py`:
```python
model="llama3.2:3b"  # Better quality, slower
```

### Change Voice
Edit `src/voice_engine.py`:
```python
"--voice", "en-US-AriaNeural",  # Female voice
```

### Add Custom Apps
Edit `src/actions.py`:
```python
app_mapping = {
    "myapp": "myapp.exe",
}
```

## Getting Help

### Check Logs
Logs are in `logs/` folder:
```bash
cat logs/jarvis_20260210.log
```

### Common Error Messages

| Error | Solution |
|-------|----------|
| "Mic error" | Run `python test_mic.py` |
| "Ollama error" | Check if Ollama is running |
| "Authentication error" | Login again |
| "System error" | Check logs folder |

## Best Practices

### For Best Experience
1. **Quiet Environment**: Use in quiet room
2. **Good Microphone**: Use quality mic
3. **Clear Speech**: Speak clearly
4. **Short Commands**: Keep under 15 words
5. **Wait for Status**: Watch status indicators

### For Best Performance
1. **Close Heavy Apps**: Free up CPU
2. **Regular Restarts**: Restart NOVA daily
3. **Update Models**: Keep Ollama updated
4. **Clean Logs**: Delete old logs monthly

## Next Steps

### Learn More
- Read [README.md](README.md) for full documentation
- Read [AGENT_TRAINING.md](AGENT_TRAINING.md) for agent behavior
- Check `src/` folder for code examples

### Customize
- Change agent name in `src/ai_engine.py`
- Add new commands in `src/actions.py`
- Modify UI in `ui/` folder

### Contribute
- Report bugs on GitHub
- Suggest new features
- Share your customizations

---

**Need Help?** Check the logs in `logs/` folder or run diagnostic tests.

**Enjoying NOVA?** Star the project and share with friends!

**Version**: 1.0.0  
**Last Updated**: February 2026
