# Telegram Bot Setup Guide

## Step 1: Create Your Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Send** `/newbot` to BotFather
3. **Follow the prompts**:
   - Choose a name for your bot (e.g., "Civic Assistant")
   - Choose a username (must end in 'bot', e.g., "civic_assistant_bot")
4. **Copy the bot token** - it will look like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

## Step 2: Add Token to .env File

Create or update `.env` file in your project root:

```bash
# Existing keys
GROQ_API_KEY=your_groq_key_here
GOOGLE_API_KEY=your_google_key_here

# Add this line
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

## Step 3: Install Dependencies

If python-telegram-bot isn't installed yet:

```powershell
pip install python-telegram-bot
```

Or install all requirements:

```powershell
pip install -r requirements.txt
```

## Step 4: Run the Bot

```powershell
python src/telegram_bot.py
```

You should see:
```
INFO - Starting Telegram bot...
INFO - Bot is running. Press Ctrl+C to stop.
```

## Step 5: Test Your Bot

1. **Search for your bot** in Telegram using the username you created
2. **Send** `/start`
3. **You should see**:
   ```
   🏛️ Welcome to Civic Assistance!
   I can help you with government schemes and benefits.
   Choose an option below:
   
   [💰 Check Benefits]
   [✅ Verify Eligibility]
   [📜 Explain Policy]
   [📝 Help Fill Application]
   ```

## Bot Commands

- `/start` - Start the bot and see all options
- `/help` - Get help and usage instructions
- `/cancel` - Cancel current operation

## How to Use Each Option

### 💰 Check Benefits
1. Click "Check Benefits"
2. Answer questions about:
   - Age
   - Annual income
   - Location (state)
   - Employment status
   - Family size
   - Education level (optional)
   - Social category (optional)
3. Get a list of all benefits you qualify for

### ✅ Verify Eligibility
1. Click "Verify Eligibility"
2. Enter the scheme name (e.g., "PM-KISAN")
3. Provide your profile information
4. Get eligibility confirmation

### 📜 Explain Policy
1. Click "Explain Policy"
2. Enter the policy/scheme name
3. Choose what aspect to understand
4. Get a detailed explanation

### 📝 Help Fill Application
1. Click "Help Fill Application"
2. Enter the scheme you're applying for
3. Indicate which documents you have
4. Specify your application stage
5. Get step-by-step guidance

## Troubleshooting

### Bot doesn't respond
- Check that `telegram_bot.py` is running
- Verify bot token in `.env` file
- Check internet connection

### "TELEGRAM_BOT_TOKEN not found" error
- Make sure `.env` file exists in project root
- Verify the token is correctly formatted
- No quotes around the token value

### Questions not appearing
- Wait a few seconds after clicking an option
- Try `/cancel` and `/start` again
- Check bot logs for errors

### Validation errors
- Follow the format examples provided
- For numbers: enter digits only
- For income: enter full amount (e.g., 200000, not 2 lakh)

## Features

### ✨ Smart Question Flow
- Questions appear one at a time
- Progress indicators (Question 2/7)
- Skip optional questions
- Input validation with helpful errors

### 🎯 Multiple Selection Types
- **Buttons**: For state, employment status
- **Free text**: For age, income, names
- **Multi-select**: For documents (comma-separated)

### 📱 Mobile-Friendly
- Designed for mobile Telegram apps
- Reply keyboards for easy selection
- Clear, concise messages

### 🔄 Session Management
- Each user has their own session
- Can handle multiple users simultaneously
- Sessions don't interfere with each other

## Example Conversation

```
You: /start

Bot: 🏛️ Welcome to Civic Assistance, John!
     Choose an option below:
     [Buttons appear]

You: [Click "Check Benefits"]

Bot: 💰 Check Your Benefits
     Answer a few questions to discover all government benefits you qualify for
     
     Question 1/7
     What is your age?
     Example: 35

You: 35

Bot: ✅ Got it!
     
     Question 2/7
     What is your annual household income (in ₹)?
     Example: 200000

You: 180000

Bot: ✅ Got it!
     
     Question 3/7
     Which state do you live in?
     [State buttons appear]

You: [Select "Maharashtra"]

... [continues through all questions]

Bot: 🔄 Processing your request...
     This may take a moment.

Bot: [Detailed response with all qualifying benefits]
     
     What would you like to do next?
     [🏠 Back to Home] [🔄 Try Another Option]
```

## Advanced Features

### Handling Long Responses
- Automatically splits messages over 4096 characters
- Preserves markdown formatting
- Sends as multiple consecutive messages

### Error Handling
- Network timeouts retry automatically
- Clear error messages for users
- Logs errors for debugging

### Markdown Support
- **Bold** text for emphasis
- _Italic_ for notes
- `Code` for scheme names
- Bullet points for lists

## Running in Production

For deploying the bot in production, consider:

1. **Use a process manager** (e.g., systemd, PM2)
2. **Set up logging** to files
3. **Monitor bot uptime**
4. **Consider webhook mode** (instead of polling) for better performance

### Webhook Mode (Optional)

For higher traffic, switch to webhook mode. Requires:
- Public HTTPS URL
- SSL certificate
- Modify `main()` function in telegram_bot.py

Contact me if you need help setting up webhooks!

## Getting Help

If you encounter issues:
1. Check the bot logs in the terminal
2. Verify `.env` configuration
3. Test with `/start` command
4. Try `/cancel` to reset state

## Next Steps

Once your bot is running:
- [ ] Share bot with test users
- [ ] Collect feedback on question flow
- [ ] Monitor agent response quality
- [ ] Add more question variations
- [ ] Consider adding voice message support
