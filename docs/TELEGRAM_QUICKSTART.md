# Telegram Bot - Quick Start

## 🚀 Get Started in 3 Steps

### Step 1: Create Bot (2 minutes)
1. Open Telegram → Search `@BotFather`
2. Send `/newbot`
3. Name your bot → Copy the token

### Step 2: Add Token
Edit `.env` file:
```
TELEGRAM_BOT_TOKEN=your_token_here
```

### Step 3: Run Bot
```powershell
python src/telegram_bot.py
```

Then search for your bot in Telegram and send `/start`!

---

## 📖 Full Documentation

See [TELEGRAM_BOT_SETUP.md](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/TELEGRAM_BOT_SETUP.md) for:
- Detailed setup instructions
- Troubleshooting guide
- Usage examples
- Advanced features

---

## 🎯 What the Bot Does

Same as the Streamlit interface, but in Telegram:

**💰 Check Benefits** - Find all schemes you qualify for
**✅ Verify Eligibility** - Check if you're eligible for a scheme
**📜 Explain Policy** - Understand government policies
**📝 Help Fill Application** - Get application guidance

---

## 💡 Features

- ✅ Conversational question flow (one at a time)
- ✅ Input validation with helpful errors
- ✅ Mobile-friendly interface
- ✅ Multiple users simultaneously
- ✅ Progress indicators
- ✅ Markdown formatting

---

## 🔧 Requirements

Already in `requirements.txt`:
- python-telegram-bot
- All existing dependencies

---

## 📱 Example

```
You: /start

Bot: 🏛️ Welcome!
     [4 option buttons]

You: [Click "Check Benefits"]

Bot: Question 1/7
     What is your age?

You: 35

Bot: ✅ Got it!
     Question 2/7...
```

---

Need help? See the full [setup guide](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/TELEGRAM_BOT_SETUP.md)!
