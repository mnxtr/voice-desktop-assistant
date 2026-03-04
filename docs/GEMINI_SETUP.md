# Gemini API Setup Guide

This guide will help you set up Google's Gemini API for enhanced voice command processing with multi-step workflow capabilities.

## Why Use Gemini API?

The Voice Desktop Assistant now supports **hybrid LLM processing**, combining the power of:

- **Gemini API** (cloud): Superior agentic workflows, multi-step task planning, better intent understanding
- **Ollama** (local): Offline fallback, privacy-conscious processing, zero cost

You can configure the system to:
- Use Gemini exclusively (cloud-only)
- Use Ollama exclusively (offline-only)
- Use hybrid mode (Gemini with Ollama fallback) **← Recommended**

## Getting Your Gemini API Key

### Step 1: Visit Google AI Studio

1. Go to [https://ai.google.dev/](https://ai.google.dev/)
2. Click **"Get API Key"** or **"Google AI Studio"**
3. Sign in with your Google account

### Step 2: Create API Key

1. In Google AI Studio, navigate to **"API Keys"** section
2. Click **"Create API Key"**
3. Select your Google Cloud project (or create a new one)
4. Copy the generated API key (keep it secure!)

**Important**: Treat your API key like a password. Never share it publicly or commit it to version control.

## Setting Up the API Key

### Option 1: Environment Variable (Recommended)

#### On Linux/Mac:

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Then reload your shell:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

#### On Windows:

**PowerShell**:
```powershell
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your-api-key-here', 'User')
```

**Command Prompt**:
```cmd
setx GEMINI_API_KEY "your-api-key-here"
```

**GUI Method**:
1. Right-click "This PC" → Properties
2. Advanced system settings → Environment Variables
3. Under "User variables", click "New"
4. Variable name: `GEMINI_API_KEY`
5. Variable value: your API key
6. Click OK

### Option 2: .env File (Development Only)

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
GEMINI_API_KEY=your-api-key-here
```

**Note**: This method requires installing `python-dotenv`:

```bash
pip install python-dotenv
```

And loading it in `main.py` (before importing config):

```python
from dotenv import load_dotenv
load_dotenv()
```

## Configuring LLM Mode

Edit `~/.desktop_llm_assistant/config.json` or use the configuration settings:

```json
{
  "llm_mode": "hybrid",
  "gemini_model": "gemini-1.5-flash",
  "gemini_temperature": 0.1,
  "gemini_max_tokens": 512,
  "gemini_timeout": 10,
  "gemini_fallback_enabled": true
}
```

### LLM Modes

#### `"hybrid"` (Recommended)
- **Primary**: Gemini API (fast, accurate, supports multi-step workflows)
- **Fallback**: Ollama (when Gemini unavailable or errors)
- **Best for**: Most users - combines cloud power with offline reliability

#### `"gemini"`
- **Primary**: Gemini API only
- **Fallback**: None (errors if Gemini unavailable)
- **Best for**: Users who always have internet and want best performance

#### `"ollama"`
- **Primary**: Ollama only (local Mistral model)
- **Fallback**: None
- **Best for**: Privacy-conscious users, offline-only usage, zero API costs

## Verifying Setup

### 1. Check API Key is Set

```bash
echo $GEMINI_API_KEY  # Linux/Mac
echo %GEMINI_API_KEY%  # Windows CMD
```

You should see your API key (or at least a partial view).

### 2. Test Connection

Run the assistant and check the logs:

```bash
python main.py
```

Look for these log messages:

```
✅ SUCCESS:
INFO: Gemini processor initialized: gemini-1.5-flash
INFO: Active processor: Gemini (hybrid mode, Gemini preferred)
INFO: LLM ready: Connected to Gemini (gemini-1.5-flash)

❌ FAILURE (Missing API Key):
WARNING: Gemini API key not found. Set GEMINI_API_KEY environment variable.
INFO: Active processor: Ollama (hybrid mode, Gemini unavailable)

❌ FAILURE (Invalid API Key):
ERROR: Failed to initialize Gemini API: [authentication error]
INFO: Active processor: Ollama (hybrid mode, Gemini unavailable)
```

### 3. Test Multi-Step Workflow

Say a complex command:

```
"Hey assistant, open chrome and search for weather"
```

Check the logs for:

```
INFO: Executing workflow with 3 steps
INFO: Step 1/3: {"action": "open_app", "target": "chrome"}
INFO: Step 2/3: {"action": "type_text", "text": "weather"}
INFO: Step 3/3: {"action": "press_key", "key": "enter"}
INFO: Workflow complete
```

## Troubleshooting

### Issue: "Gemini API key not found"

**Solution**: 
- Verify environment variable is set: `echo $GEMINI_API_KEY`
- Restart your terminal/IDE after setting the variable
- Check for typos in the variable name (`GEMINI_API_KEY` - all caps)

### Issue: "Authentication error" or "Invalid API key"

**Solution**:
- Verify the API key is correct (no extra spaces/characters)
- Check if the key is active in Google AI Studio
- Ensure you're using a key for Google AI (not Google Cloud Vertex AI)

### Issue: "Gemini processor initialized but not available"

**Solution**:
- Check internet connection
- Verify API key has proper permissions in Google Cloud
- Check if you've exceeded API quota (see Pricing section)

### Issue: "Cannot connect to Gemini"

**Solution**:
- Check firewall/proxy settings
- Verify `gemini_timeout` in config (increase if needed)
- Try switching to `"llm_mode": "ollama"` temporarily

### Issue: Falling back to Ollama too often

**Solution**:
- Check logs for specific Gemini errors
- Increase `gemini_timeout` in config (default: 10 seconds)
- Verify stable internet connection
- Check API quota usage

## Pricing and Usage

### Gemini 1.5 Flash Pricing (as of March 2026)

- **Input**: $0.075 per 1 million tokens
- **Output**: $0.30 per 1 million tokens

### Cost Estimation

**Typical voice command**: ~10 input tokens, ~50 output tokens

**Heavy user** (500 commands/day):
- Daily cost: $0.0086
- Monthly cost: ~$0.26
- Annual cost: ~$3.12

**Light user** (100 commands/day):
- Monthly cost: ~$0.05

### Free Tier

Google AI offers a generous free tier:
- 15 requests per minute (RPM)
- 1 million tokens per minute (TPM)
- 1,500 requests per day (RPD)

For most users, you'll **stay within the free tier**.

### Monitoring Usage

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Go to **"Usage"** or **"Quotas"**
3. Monitor daily/monthly usage

## Privacy Considerations

### What data is sent to Gemini?

When using Gemini API, the following is sent to Google servers:
- Your voice command text (after local speech-to-text conversion)
- Recent conversation history (last 6 exchanges for context)
- System prompt (action definitions)

**NOT sent**:
- Audio recordings (STT happens locally with Vosk)
- Screen contents
- Personal files
- Gaze tracking data

### How to minimize data sharing

1. **Use Ollama mode for sensitive commands**:
   ```python
   # Temporarily switch to Ollama for this session
   config.set("llm_mode", "ollama")
   ```

2. **Clear conversation history**:
   - Say "Hey assistant, clear history"
   - Or restart the application

3. **Use hybrid mode**: Only falls back to Gemini when needed

4. **Review Google's privacy policy**: [https://ai.google.dev/terms](https://ai.google.dev/terms)

## Advanced Configuration

### Switching Models

To use **Gemini 1.5 Pro** (more powerful, more expensive):

```json
{
  "gemini_model": "gemini-1.5-pro"
}
```

Pricing: ~4x more expensive than Flash, but better for complex reasoning.

### Adjusting Temperature

Control randomness/creativity (0.0 = deterministic, 1.0 = creative):

```json
{
  "gemini_temperature": 0.1
}
```

**Recommended**: 0.1 (low) for consistent command interpretation.

### Timeout Settings

Increase timeout for slow connections:

```json
{
  "gemini_timeout": 20
}
```

### Disabling Fallback

Force errors instead of falling back to Ollama:

```json
{
  "gemini_fallback_enabled": false
}
```

## Next Steps

- [Multi-Step Workflows Guide](WORKFLOWS.md) - Learn about agentic task execution
- [Fine-Tuning Guide](FINE_TUNING.md) - Customize Gemini for your command patterns
- [API Reference](API.md) - Full configuration options

## Support

If you encounter issues:

1. Check logs: `~/.desktop_llm_assistant/assistant.log`
2. Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
3. Report issues: [GitHub Issues](https://github.com/mnxtr/voice-desktop-assistant/issues)

---

**Last Updated**: March 2026  
**Gemini API Version**: 1.5 Flash/Pro
