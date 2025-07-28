# Smart Email Responder 🤖📧

An intelligent AI-powered email assistant that automatically processes your unread Gmail emails, filters out spam and marketing content, and creates draft responses for important emails that need your attention.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-green.svg)](https://openai.com)
[![Gmail API](https://img.shields.io/badge/Gmail-API-red.svg)](https://developers.google.com/gmail/api)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/smart-email-responder.git
   cd smart-email-responder
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv gmail-ai-env
   source gmail-ai-env/bin/activate  # On Windows: gmail-ai-env\Scripts\activate
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
   - Place it in the project root directory

#### 3. Environment Variables

1. Create a `.env` file in the project root:
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
   This will verify your API keys and credentials are working.

2. **Run the Smart Email Responder:**
   ```bash
   python smart_email_responder.py
   ```

3. **First-time authentication:**
   - The app will open your browser for Google OAuth
   - Sign in to your Google account
   - Grant permissions for Gmail and Calendar access
   - Authentication tokens will be saved for future use

## 📖 How It Works

### AI Reasoning Framework

The system uses a proven 5-step reasoning framework to analyze each email:

1. **Sender Analysis** 👤
   - Identifies real people vs automated systems vs marketing
   - Recognizes known contacts and business relationships

2. **Content Analysis** 📝
   - Detects questions, requests, and calls to action
   - Identifies meeting requests and scheduling needs
   - Analyzes email structure and intent

3. **Urgency Analysis** ⚡
   - Assesses time-sensitivity and importance
   - Identifies deadline-driven communications
   - Prioritizes based on business impact

4. **Spam/Marketing Filter** 🚫
   - Filters promotional content and newsletters
   - Identifies automated notifications
   - Blocks known spam patterns

5. **Business Context** 💼
   - Distinguishes work-related vs personal emails
   - Considers sender relationship and history
   - Applies appropriate response protocols

### Email Classification

**Responds to:**
- ✅ Direct questions from colleagues or clients
- ✅ Meeting requests and scheduling inquiries
- ✅ Work assignments and project communications
- ✅ Personal messages from known contacts
- ✅ Time-sensitive business matters

**Ignores:**
- ❌ Marketing and promotional emails
- ❌ Newsletters and automated notifications
- ❌ Spam and junk mail
- ❌ Social media notifications
- ❌ System-generated alerts

### Meeting Request Handling

When a meeting request is detected:

1. **Parse Details**: Extracts meeting purpose, preferred time, duration, and attendees
2. **Check Availability**: Queries your Google Calendar for conflicts
3. **Create Event**: If available, creates calendar invite automatically
4. **Suggest Alternatives**: If busy, proposes 2 alternative time slots
5. **Draft Response**: Creates appropriate email response with meeting details

## 🔧 Configuration Options

### Working Hours
Customize your availability in the `.env` file:
```env
WORKING_HOURS_START=09:00
WORKING_HOURS_END=17:00
```

### Meeting Defaults
Set default meeting duration:
```env
DEFAULT_MEETING_DURATION=30
```

### Timezone
Configure your timezone:
```env
TIMEZONE=America/New_York
```

## 📊 Usage Examples

### Typical Output
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

Analyzing: Client Question About Proposal...
Type: business
Needs response: true
Priority: high
Reasoning: Direct question from client requiring immediate attention
✅ Draft response created

Done! Created 2 draft responses and 1 meetings.
```

### Draft Response Example
The AI generates professional responses like:
```
Hi [Name],

Thank you for your email regarding the project update meeting.

I've scheduled our meeting for January 15, 2024 at 2:00 PM as requested. 
You should receive a calendar invitation shortly.

Looking forward to discussing the project progress with you.

Best regards,
[Your Name]
```

## 🛡️ Security & Privacy

- **Local Processing**: All email analysis happens locally on your machine
- **Secure Authentication**: Uses Google OAuth 2.0 for secure API access
- **Minimal Permissions**: Only requests necessary Gmail and Calendar permissions
- **API Key Protection**: Environment variables keep your keys secure
- **No Data Storage**: Doesn't store or log your email content
- **Draft Only**: Creates drafts for your review, never sends automatically

## 🔍 Troubleshooting

### Common Issues

**"OpenAI API key not found"**
- Ensure your `.env` file contains `OPENAI_API_KEY=your_actual_key`
- Check for typos or extra spaces in the key

**"credentials.json not found"**
- Download OAuth credentials from Google Cloud Console
- Ensure file is named exactly `credentials.json`
- Place in the project root directory

**"Permission denied" errors**
- Re-run the OAuth flow by deleting token files:
  ```bash
  rm gmail_token.json calendar_token.json
  python smart_email_responder.py
  ```

**"Invalid attendee email" in calendar**
- The AI sometimes extracts malformed email addresses
- Check the draft response and edit before sending

### Getting Help

1. Run the setup test: `python test_setup.py`
2. Check the console output for specific error messages
3. Verify all prerequisites are installed
4. Ensure APIs are enabled in Google Cloud Console

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with a clear description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4o-mini model
- Google for Gmail and Calendar APIs
- The Python community for excellent libraries

## 📞 Support

If you find this project helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs via GitHub issues
- 💡 Suggesting new features
- 🔄 Sharing with others who might benefit

---

**Made with ❤️ for busy professionals who want to stay on top of important emails while filtering out the noise.**