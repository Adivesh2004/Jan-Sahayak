"""
Telegram Bot for Zynd Civic Assistant
Provides conversational interface for the 4 main options
"""
import os
import sys
import logging
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph import app as agent_graph
from src.question_config import get_option_config, get_all_options
from src.validators import (
    validate_age, validate_income, validate_location,
    validate_family_size, validate_scheme_name, validate_policy_name,
    INDIAN_STATES, EMPLOYMENT_STATUSES, EDUCATION_LEVELS, SOCIAL_CATEGORIES
)
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
SELECTING_OPTION = 0
COLLECTING_ANSWERS = 1
PROCESSING = 2

# Callback data for options
OPTION_ASK_FOR_HELP = "opt_ask_for_help"  # NEW: Featured option
OPTION_CHECK_BENEFITS = "opt_check_benefits"
OPTION_VERIFY_ELIGIBILITY = "opt_verify_eligibility"
OPTION_EXPLAIN_POLICY = "opt_explain_policy"
OPTION_HELP_APPLICATION = "opt_help_application"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send welcome message with featured Ask for Help and 4 option buttons."""
    user = update.effective_user
    
    welcome_text = (
        f"🏛️ *Welcome to Civic Assistance, {user.first_name}!*\n\n"
        "🤝 *Not sure what you need?*\n"
        "Let's have a conversation. I'll help you discover benefits you may be eligible for.\n\n"
        "Or choose a specific option below:"
    )
    
    # Create inline keyboard with featured Ask for Help + 4 main options
    keyboard = [
        [InlineKeyboardButton("🗣️ Ask for Help (Recommended)", callback_data=OPTION_ASK_FOR_HELP)],
        [InlineKeyboardButton("💰 Check Benefits", callback_data=OPTION_CHECK_BENEFITS)],
        [InlineKeyboardButton("✅ Verify Eligibility", callback_data=OPTION_VERIFY_ELIGIBILITY)],
        [InlineKeyboardButton("📜 Explain Policy", callback_data=OPTION_EXPLAIN_POLICY)],
        [InlineKeyboardButton("📝 Help Fill Application", callback_data=OPTION_HELP_APPLICATION)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Initialize user context
    context.user_data.clear()
    
    return SELECTING_OPTION


async def option_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle option selection and start question flow."""
    query = update.callback_query
    await query.answer()
    
    selected_option = query.data
    
    # Map callback data to option keys
    option_map = {
        OPTION_ASK_FOR_HELP: "ask_for_help",  # NEW: Featured option
        OPTION_CHECK_BENEFITS: "check_benefits",
        OPTION_VERIFY_ELIGIBILITY: "eligibility_verification",
        OPTION_EXPLAIN_POLICY: "explain_policy",
        OPTION_HELP_APPLICATION: "help_application"
    }
    
    option_key = option_map.get(selected_option)
    if not option_key:
        await query.edit_message_text("Invalid option selected.")
        return ConversationHandler.END
    
    # Get option configuration
    config = get_option_config(option_key)
    
    # Store in context
    context.user_data['option_key'] = option_key
    context.user_data['config'] = config
    context.user_data['questions'] = config['questions']
    context.user_data['current_question_index'] = 0
    context.user_data['answers'] = {}
    
    # Send first question
    await query.edit_message_text(
        f"*{config['title']}*\n\n{config['description']}",
        parse_mode='Markdown'
    )
    
    return await ask_next_question(update, context)


async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the next question in the sequence."""
    questions = context.user_data['questions']
    current_index = context.user_data['current_question_index']
    
    if current_index >= len(questions):
        # All questions answered, process with agent
        return await process_with_agent(update, context)
    
    question = questions[current_index]
    total_questions = len([q for q in questions if q.get('required', False)])
    
    # Build question text
    question_text = f"*Question {current_index + 1}/{len(questions)}*\n\n"
    question_text += f"{question['label']}\n\n"
    
    if question.get('help_text'):
        question_text += f"ℹ️ _{question['help_text']}_\n\n"
    
    if question.get('placeholder'):
        question_text += f"Example: {question['placeholder']}\n\n"
    
    if not question.get('required', False):
        question_text += "_(Optional - send 'skip' to skip)_"
    
    # Handle different question types
    q_type = question['type']
    
    if q_type == 'selectbox':
        # Create reply keyboard for options
        options = question.get('options', [])
        if not question.get('required', False):
            options = options + ['Skip']
        
        # Create keyboard with 2 buttons per row
        keyboard = [[opt] for opt in options]
        reply_markup = ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=question_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif q_type == 'multiselect':
        question_text += "\n\n_Send options separated by commas_"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=question_text,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='Markdown'
        )
    
    else:
        # Regular text input
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=question_text,
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='Markdown'
        )
    
    return COLLECTING_ANSWERS


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's answer to current question."""
    user_answer = update.message.text.strip()
    
    questions = context.user_data['questions']
    current_index = context.user_data['current_question_index']
    question = questions[current_index]
    
    # Handle skip for optional questions
    if user_answer.lower() == 'skip' and not question.get('required', False):
        context.user_data['current_question_index'] += 1
        return await ask_next_question(update, context)
    
    # Validate answer
    validation_result = await validate_answer(question, user_answer, update, context)
    
    if not validation_result['valid']:
        await update.message.reply_text(
            f"❌ {validation_result['error']}\n\nPlease try again:",
            parse_mode='Markdown'
        )
        return COLLECTING_ANSWERS
    
    # Store answer
    context.user_data['answers'][question['id']] = validation_result['value']
    
    # Move to next question
    context.user_data['current_question_index'] += 1
    
    # Confirm answer
    await update.message.reply_text("✅ Got it!", reply_markup=ReplyKeyboardRemove())
    
    return await ask_next_question(update, context)


async def validate_answer(question: Dict, answer: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
    """Validate user's answer based on question type."""
    q_id = question['id']
    q_type = question['type']
    
    # Type-specific validation
    if q_id == 'age':
        is_valid, value, error = validate_age(answer)
        return {'valid': is_valid, 'value': value, 'error': error}
    
    elif q_id == 'annual_income':
        is_valid, value, error = validate_income(answer)
        return {'valid': is_valid, 'value': value, 'error': error}
    
    elif q_id == 'family_size':
        is_valid, value, error = validate_family_size(answer)
        return {'valid': is_valid, 'value': value, 'error': error}
    
    elif q_id == 'scheme_name':
        is_valid, value, error = validate_scheme_name(answer)
        return {'valid': is_valid, 'value': value, 'error': error}
    
    elif q_id == 'policy_name':
        is_valid, value, error = validate_policy_name(answer)
        return {'valid': is_valid, 'value': value, 'error': error}
    
    elif q_type == 'selectbox':
        options = question.get('options', [])
        if answer in options:
            return {'valid': True, 'value': answer, 'error': None}
        else:
            return {'valid': False, 'value': None, 'error': f"Please select from the available options"}
    
    elif q_type == 'multiselect':
        values = [v.strip() for v in answer.split(',')]
        return {'valid': True, 'value': values, 'error': None}
    
    else:
        # Regular text
        if len(answer) < 2:
            return {'valid': False, 'value': None, 'error': "Answer is too short"}
        return {'valid': True, 'value': answer, 'error': None}


async def process_with_agent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process collected answers with the agent system."""
    option_key = context.user_data['option_key']
    answers = context.user_data['answers']
    
    # Build natural language query
    query = build_query_from_answers(option_key, answers)
    
    # Create user profile
    user_profile = {
        "age": answers.get("age"),
        "annual_income": answers.get("annual_income"),
        "location": answers.get("location"),
        "employment_status": answers.get("employment_status"),
        "family_size": answers.get("family_size"),
        "education_level": answers.get("education_level"),
        "social_category": answers.get("social_category")
    }
    
    # Send processing message
    processing_msg = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔄 Processing your request...\n\nThis may take a moment.",
        parse_mode='Markdown'
    )
    
    try:
        # Invoke agent
        thread_config = {"configurable": {"thread_id": f"telegram_{update.effective_chat.id}"}}
        
        # Get agent mapping
        config = context.user_data['config']
        
        inputs = {
            "input_text": query,
            "messages": [HumanMessage(content=query)],
            "user_profile": user_profile,
            "selected_option": option_key,
            "collected_answers": answers,
            "current_intent": config['agent_mapping']
        }
        
        final_response = ""
        
        # Stream agent events
        for event in agent_graph.stream(inputs, config=thread_config):
            for key, value in event.items():
                if "messages" in value and value["messages"]:
                    msg = value["messages"][-1]
                    content = msg.content if hasattr(msg, "content") else str(msg)
                    final_response = content
        
        # Delete processing message
        # Delete processing message
        try:
            await processing_msg.delete()
        except Exception:
            pass  # Message might already be deleted
        
        # Send response (split if too long)
        await send_long_message(update.effective_chat.id, context, final_response)
        
        # Show options
        keyboard = [
            [InlineKeyboardButton("🏠 Back to Home", callback_data="back_home")],
            [InlineKeyboardButton("🔄 Try Another Option", callback_data="try_another")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="What would you like to do next?",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error processing with agent: {e}")
        try:
            await processing_msg.edit_text(
                f"Sorry, an error occurred while processing your request.\n\nPlease try again or use /start to begin over."
            )
        except Exception:
            # If edit fails, send new message
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, an error occurred. Please use /start to try again."
            )
    
    return SELECTING_OPTION


def build_query_from_answers(option_key: str, answers: Dict[str, Any]) -> str:
    """Build natural language query from collected answers."""
    
    if option_key == "check_benefits":
        query_parts = [
            "I am looking for government benefits and schemes I may qualify for.",
            f"I am {answers.get('age')} years old",
            f"with an annual household income of ₹{answers.get('annual_income', 0):,}.",
            f"I live in {answers.get('location')}",
            f"and my employment status is: {answers.get('employment_status')}.",
            f"My family has {answers.get('family_size')} members."
        ]
        
        if answers.get('education_level'):
            query_parts.append(f"My education level is: {answers['education_level']}.")
        if answers.get('social_category'):
            query_parts.append(f"I belong to {answers['social_category']} category.")
            
        return " ".join(query_parts)
    
    elif option_key == "eligibility_verification":
        query_parts = [
            f"I want to check if I am eligible for the {answers.get('scheme_name')} scheme.",
            f"I am {answers.get('age')} years old",
            f"with an annual income of ₹{answers.get('annual_income', 0):,}.",
            f"I live in {answers.get('location')}",
            f"and my employment status is: {answers.get('employment_status')}."
        ]
        
        if answers.get('social_category'):
            query_parts.append(f"I belong to {answers['social_category']} category.")
        if answers.get('additional_info'):
            query_parts.append(f"Additional information: {answers['additional_info']}")
            
        return " ".join(query_parts)
    
    elif option_key == "explain_policy":
        query = f"Please explain the {answers.get('policy_name')} policy/scheme."
        
        aspect = answers.get('specific_aspect', '')
        if aspect and aspect != "Everything about this policy":
            query += f" Specifically, I want to know: {aspect}"
        else:
            query += " I want a comprehensive explanation."
            
        if answers.get('additional_questions'):
            query += f" I also have these questions: {answers['additional_questions']}"
            
        return query
    
    elif option_key == "help_application":
        query_parts = [
            f"I need help applying for the {answers.get('scheme_name')} scheme.",
            f"I am currently at this stage: {answers.get('application_stage')}."
        ]
        
        docs = answers.get('documents_available', [])
        if docs and docs != ["None of the above"]:
            query_parts.append(f"I have the following documents: {', '.join(docs)}.")
        else:
            query_parts.append("I don't have any documents yet.")
            
        if answers.get('specific_help'):
            query_parts.append(f"Specific help needed: {answers['specific_help']}")
            
        return " ".join(query_parts)
    
    # NEW: Ask for Help (Conversational Discovery)
    elif option_key == "ask_for_help":
        query_parts = [
            "Help me discover government benefits I may be eligible for."
        ]
        
        if answers.get('support_type'):
            query_parts.append(f"I'm looking for support with: {answers['support_type']}.")
        
        if answers.get('age_range'):
            query_parts.append(f"I am {answers['age_range']} old.")
        
        if answers.get('employment'):
            query_parts.append(f"My employment status: {answers['employment']}.")
        
        if answers.get('income_bracket') and answers.get('income_bracket') != "Prefer not to say":
            query_parts.append(f"My family income is {answers['income_bracket']}.")
        
        if answers.get('location'):
            query_parts.append(f"I live in {answers['location']}.")
        
        if answers.get('family_size'):
            query_parts.append(f"My family has {answers['family_size']} members.")
        
        special = answers.get('special_conditions', [])
        if special and isinstance(special, list) and "None of these" not in special:
            query_parts.append(f"Special conditions: {', '.join(special)}.")
        elif special and isinstance(special, str):
            query_parts.append(f"Special conditions: {special}.")
            
        return " ".join(query_parts)
    
    return ""


async def send_long_message(chat_id: int, context: ContextTypes.DEFAULT_TYPE, text: str, max_length: int = 4096):
    """Split and send long messages."""
    # Remove problematic markdown characters for safety
    # Send as plain text to avoid parsing errors
    
    if len(text) <= max_length:
        try:
            await context.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            # Fallback: send without any formatting
            await context.bot.send_message(chat_id=chat_id, text=text)
    else:
        # Split by paragraphs
        parts = text.split('\n\n')
        current_message = ""
        
        for part in parts:
            if len(current_message) + len(part) + 2 <= max_length:
                current_message += part + "\n\n"
            else:
                if current_message:
                    try:
                        await context.bot.send_message(chat_id=chat_id, text=current_message)
                    except Exception as e:
                        logger.error(f"Error sending message part: {e}")
                        await context.bot.send_message(chat_id=chat_id, text=current_message)
                current_message = part + "\n\n"
        
        if current_message:
            try:
                await context.bot.send_message(chat_id=chat_id, text=current_message)
            except Exception as e:
                logger.error(f"Error sending final message part: {e}")
                await context.bot.send_message(chat_id=chat_id, text=current_message)


async def handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle navigation buttons."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_home":
        return await start_from_callback(query, context)
    elif query.data == "try_another":
        context.user_data.clear()
        return await start_from_callback(query, context)
    
    return SELECTING_OPTION


async def start_from_callback(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Restart from callback query."""
    welcome_text = (
        "🏛️ *Welcome Back!*\n\n"
        "Choose an option below:"
    )
    
    keyboard = [
        [InlineKeyboardButton("🗣️ Ask for Help", callback_data=OPTION_ASK_FOR_HELP)],
        [InlineKeyboardButton("💰 Check Benefits", callback_data=OPTION_CHECK_BENEFITS)],
        [InlineKeyboardButton("✅ Verify Eligibility", callback_data=OPTION_VERIFY_ELIGIBILITY)],
        [InlineKeyboardButton("📜 Explain Policy", callback_data=OPTION_EXPLAIN_POLICY)],
        [InlineKeyboardButton("📝 Help Fill Application", callback_data=OPTION_HELP_APPLICATION)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    context.user_data.clear()
    
    return SELECTING_OPTION


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message."""
    help_text = (
        "*Civic Assistance Bot Help*\n\n"
        "*Available Commands:*\n"
        "/start - Start the bot and see main options\n"
        "/help - Show this help message\n"
        "/cancel - Cancel current operation\n\n"
        "*How to Use:*\n"
        "1. Choose one of the 4 main options\n"
        "2. Answer the questions asked\n"
        "3. Get personalized assistance\n\n"
        "*Main Options:*\n"
        "💰 *Check Benefits* - Discover all benefits you qualify for\n"
        "✅ *Verify Eligibility* - Check if you qualify for a specific scheme\n"
        "📜 *Explain Policy* - Understand government policies\n"
        "📝 *Help Fill Application* - Get application guidance\n"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel current conversation."""
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ Operation cancelled.\n\nUse /start to begin again.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return ConversationHandler.END


def main():
    """Start the bot."""
    # Get token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        logger.error("Please add your bot token to the .env file")
        return
    
    # Create application with increased timeout for LLM responses
    from telegram.request import HTTPXRequest
    request = HTTPXRequest(
        read_timeout=60.0,
        write_timeout=60.0,
        connect_timeout=60.0
    )
    application = Application.builder().token(token).request(request).build()
    
    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_OPTION: [
                CallbackQueryHandler(option_selected, pattern=f"^{OPTION_ASK_FOR_HELP}|{OPTION_CHECK_BENEFITS}|{OPTION_VERIFY_ELIGIBILITY}|{OPTION_EXPLAIN_POLICY}|{OPTION_HELP_APPLICATION}$"),
                CallbackQueryHandler(handle_navigation, pattern="^back_home|try_another$")
            ],
            COLLECTING_ANSWERS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)
            ],
            PROCESSING: [
                CallbackQueryHandler(handle_navigation, pattern="^back_home|try_another$")
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help_command))
    
    # Start bot
    logger.info("Starting Telegram bot...")
    logger.info("Bot is running. Press Ctrl+C to stop.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
