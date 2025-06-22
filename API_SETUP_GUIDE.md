# 🔑 TestPilot API Key Setup Guide

## Quick Setup (< 5 minutes)

### 1. Add Your API Keys

Edit the `.env` file in the project root:

```bash
# Open the .env file
nano .env

# Add your actual API keys:
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-claude-key-here
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### 2. Get API Keys

**Anthropic Claude (Recommended):**
- Go to: https://console.anthropic.com/
- Create account → Get API key
- Model: `claude-3-sonnet-20240229` (most capable)
- Cost: ~$3 per million tokens

**OpenAI (Alternative):**
- Go to: https://platform.openai.com/api-keys
- Create account → Generate API key
- Model: `gpt-4` or `gpt-4-turbo`
- Cost: ~$30 per million tokens

### 3. Test API Connection

```bash
# Test the AI client
python test_ai_connection.py
```

---

## 🎯 What You Get With API Keys

### AI-Powered Features
- **Natural Language Test Planning**: "Test a 2.4GHz amplifier for gain and harmonics"
- **Intelligent Driver Generation**: Upload manual → Get Python driver
- **Real-time Test Analysis**: AI monitors tests and suggests fixes
- **Automatic Report Generation**: Professional test reports with insights

### Example Conversation
```
You: "Test a WiFi power amplifier at 2.4GHz for gain, harmonics, and ACPR"

AI: "I'll create a comprehensive test plan:
1. Signal Generator: -5 dBm input at 2.4-2.5 GHz sweep
2. Spectrum Analyzer: Measure output power and harmonics
3. Pass criteria: Gain 20±2 dB, harmonics <-40 dBc
4. Expected duration: 45 minutes

[Generates mermaid diagram showing test flow]
[Creates SCPI command sequences]
[Sets up real-time monitoring]"
```

---

## 🔧 Real-Time Recorder & Plotter Features

Your TestPilot system now includes:

### Recording Capabilities
- **Real-time measurement capture** (1-50 Hz sample rates)
- **Live plotting** of amplitude, phase, power
- **Configurable test sessions** with metadata
- **JSON/CSV export** for AI analysis

### GUI Features  
- **Start/Pause/Stop controls**
- **Interactive charts** with zoom/pan
- **Data table** showing recent measurements
- **Export functionality** for post-analysis

### Data Format for LLM
```json
{
  "session": {
    "id": "test_123456789",
    "name": "RF Amplifier Test",
    "instruments": ["Signal Generator", "Spectrum Analyzer"],
    "testType": "RF Characterization"
  },
  "measurements": [
    {
      "timestamp": 1704067200000,
      "frequency": 2450000000,
      "amplitude": 20.5,
      "phase": -45.2,
      "power": 18.3
    }
  ]
}
```

---

## 🚀 How to Use

### Option 1: Dashboard (Default)
1. Open **http://localhost:3000**
2. See ChatInterface on right side
3. Click quick action buttons or type commands

### Option 2: Tests Page
1. Navigate to "Tests" in sidebar
2. Click **"AI Assistant"** for chat interface
3. Click **"Start Recording"** for real-time plots

### Option 3: Direct SCPI Testing
```bash
# Test your actual instrument
python test_real_instrument.py 1

# Edit the script first to set your instrument IP:
INSTRUMENT_IP = "192.168.1.100"  # Your instrument's IP
```

---

## 💡 Tips for Best Results

### For Test Planning
- Be specific: "Test 2.4GHz amplifier" vs "Test amplifier"
- Include requirements: "Gain should be 20±2 dB"
- Mention instruments: "Use Keysight signal generator"

### For Driver Generation
- Upload complete manual sections with SCPI commands
- Include parameter ranges and examples
- The AI will extract commands and generate Python classes

### For Real-time Recording
- Set appropriate sample rate (10 Hz good for most tests)
- Use export function to save data for AI analysis
- Switch between amplitude/phase/power plots during recording

---

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React GUI     │◄──►│   AI Backend    │◄──►│   Instruments   │
│   (Port 3000)   │    │   (Claude/GPT)  │    │   (SCPI/VISA)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
    Chat Interface        Natural Language        Real Hardware
    Mermaid Diagrams      Test Planning          Control & Measure
    Real-time Plots       Driver Generation      Data Collection
```

---

## 🎯 Ready to Test!

1. **Add your API key** to `.env`
2. **Open http://localhost:3000**
3. **Try: "Test a 2.4GHz WiFi amplifier"**
4. **Watch AI generate test plan with mermaid diagram**
5. **Click "Start Recording" for real-time plots**

Your AI-driven test automation platform is ready! 🚀