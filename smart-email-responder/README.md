# Smart Email Responder 🤖📧

An intelligent AI-powered email assistant that automatically processes your unread Gmail emails, filters out spam and marketing content, and creates draft responses for important emails that need your attention.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg)](https://openai.com)
[![Gmail API](https://img.shields.io/badge/Gmail-API-red.svg)](https://developers.google.com/gmail/api)

## 🎯 What It Does

The Smart Email Responder uses advanced AI reasoning to:

- 📬 **Read unread emails** from your Gmail inbox
- 🧠 **Analyze with AI reasoning** to determine which emails need responses
- 🚫 **Filter out spam, marketing, and promotional emails** automatically
- ✍️ **Create draft responses** for important emails in your Gmail drafts
- 📅 **Handle meeting requests** with intelligent calendar integration
- ⏰ **Check availability** and suggest alternative meeting times
- 🎯 **Prioritize emails** by urgency and importance

## 🌟 Key Features

### Intelligent Email Analysis
- **5-Step Reasoning Framework**: Sender analysis, content analysis, urgency assessment, spam filtering, and business context evaluation
- **Smart Filtering**: Automatically ignores newsletters, marketing emails, and automated notifications
- **Priority Classification**: Categorizes emails as high, medium, or low priority

### Automated Response Generation
- **Context-Aware Responses**: Generates appropriate draft responses based on email content
- **Professional Tone**: Maintains professional communication style
- **Draft Creation**: Saves responses as Gmail drafts for your review before sending

### Meeting Intelligence
- **Calendar Integration**: Checks your Google Calendar for availability
- **Smart Scheduling**: Creates calendar invites for available time slots
- **Alternative Suggestions**: Proposes 2 alternative times if requested slot is busy
- **Working Hours Respect**: Only schedules within business hours (9 AM - 5 PM, weekdays)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Gmail account
- Google Cloud Console access
- OpenAI API account

### Installation

1. **Clone this directory:**
   ```bash
   git clone https://github.com/agentbuild-ai/agents.git
   cd agents/smart-email-responder
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

#### 1. OpenAI API Setup

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in and create a new API key
3. Copy the API key (starts with `sk-`)

#### 2. Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Gmail API
   - Google Calendar API
4. Create credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the JSON file and rename it to `credentials.json`
   - Place it in the project directory

#### 3. Environment Variables

1. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Add your OpenAI API key to `.env`:
   ```env
   # OpenAI API Key
   OPENAI_API_KEY=your_actual_openai_api_key_here
   
   # Optional: Customize settings
   TIMEZONE=UTC
   DEFAULT_MEETING_DURATION=30
   WORKING_HOURS_START=09:00
   WORKING_HOURS_END=17:00
   ```

### First Run

1. **Test your setup:**
   ```bash
   python test_setup.py
   ```

2. **Run the Smart Email Responder:**
   ```bash
   python smart_email_responder.py
   ```

3. **First-time authentication:**
   - The app will open your browser for Google OAuth
   - Sign in to your Google account
   - Grant permissions for Gmail and Calendar access

## 📖 How It Works

### AI Reasoning Framework

The system uses a proven 5-step reasoning framework to analyze each email:

1. **Sender Analysis** 👤 - Identifies real people vs automated systems vs marketing
2. **Content Analysis** 📝 - Detects questions, requests, and calls to action
3. **Urgency Analysis** ⚡ - Assesses time-sensitivity and importance
4. **Spam/Marketing Filter** 🚫 - Filters promotional content and newsletters
5. **Business Context** 💼 - Distinguishes work-related vs personal emails

### Email Classification

**Responds to:**
- ✅ Direct questions from colleagues or clients
- ✅ Meeting requests and scheduling inquiries
- ✅ Work assignments and project communications
- ✅ Personal messages from known contacts

**Ignores:**
- ❌ Marketing and promotional emails
- ❌ Newsletters and automated notifications
- ❌ Spam and junk mail
- ❌ Social media notifications

## 📊 Usage Example

```
Getting unread emails...

Analyzing: Project Update Meeting Request...
Type: business
Needs response: true
Priority: high
Reasoning: Contains meeting request from colleague, requires scheduling
✅ Draft response created
Meeting scheduled for January 15, 2024 at 2:00 PM. Calendar invite sent!

Analyzing: Newsletter: Weekly Tech Updates...
Type: newsletter
Needs response: false
Skipped: Automated newsletter, no response needed

Done! Created 1 draft responses and 1 meetings.
```

## 🛡️ Security & Privacy

- **Local Processing**: All email analysis happens locally on your machine
- **Secure Authentication**: Uses Google OAuth 2.0 for secure API access
- **Minimal Permissions**: Only requests necessary Gmail and Calendar permissions
- **No Data Storage**: Doesn't store or log your email content
- **Draft Only**: Creates drafts for your review, never sends automatically

## 🔍 Troubleshooting

### Common Issues

**"OpenAI API key not found"**
- Ensure your `.env` file contains `OPENAI_API_KEY=your_actual_key`

**"credentials.json not found"**
- Download OAuth credentials from Google Cloud Console
- Ensure file is named exactly `credentials.json`

**"Permission denied" errors**
- Re-run the OAuth flow by deleting token files:
  ```bash
  rm gmail_token.json calendar_token.json
  python smart_email_responder.py
  ```

## 🤝 Contributing

This agent is part of the [AgentBuild.ai Agents Collection](https://github.com/agentbuild-ai/agents). 

To contribute:
1. Fork the main repository
2. Create a feature branch
3. Make your changes in the `smart-email-responder/` directory
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Part of the [AgentBuild.ai Agents Collection](https://github.com/agentbuild-ai/agents) - Building the future of AI agents, one tool at a time.**