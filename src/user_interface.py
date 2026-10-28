"""
User-friendly Streamlit interface for Zynd Civic Assistant
Provides 4 main options with guided question collection
"""
import streamlit as st
import sys
import os
from typing import Dict, Any, List

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph import app
from src.logger import setup_logger
from src.langsmith_config import setup_langsmith
from src.question_config import get_option_config, get_all_options
from src.languages import TRANSLATIONS
from src.validators import (
    validate_age, validate_income, validate_location, 
    validate_family_size, validate_scheme_name, validate_policy_name,
    format_currency
)
from langchain_core.messages import HumanMessage, AIMessage

logger = setup_logger("UserInterface")
setup_langsmith()

# Page config
st.set_page_config(
    page_title="Civic Assistance - Zynd",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-option-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .main-option-card:hover {
        transform: translateY(-5px);
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        padding: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .question-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .success-banner {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e063 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    .info-box {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_view" not in st.session_state:
    st.session_state.current_view = "home"  # home, questions, results
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
if "collected_answers" not in st.session_state:
    st.session_state.collected_answers = {}
if "agent_response" not in st.session_state:
    st.session_state.agent_response = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "user_session"
if "language" not in st.session_state:
    st.session_state.language = "en"

# Sidebar for Language Selection
with st.sidebar:
    st.title(TRANSLATIONS[st.session_state.language]["sidebar_title"])
    lang_choice = st.selectbox(
        "Select Language",
        options=["English", "Hindi", "Kannada"],
        index=["en", "hi", "kn"].index(st.session_state.language),
        label_visibility="collapsed"
    )
    
    # Update language in session state
    lang_map = {"English": "en", "Hindi": "hi", "Kannada": "kn"}
    if lang_map[lang_choice] != st.session_state.language:
        st.session_state.language = lang_map[lang_choice]
        st.rerun()

def get_translations():
    return TRANSLATIONS[st.session_state.language]

def reset_to_home():
    """Reset to home view."""
    st.session_state.current_view = "home"
    st.session_state.selected_option = None
    st.session_state.collected_answers = {}
    st.session_state.agent_response = None

def show_home_page():
    """Display the home page with featured Ask for Help and 4 other options."""
    t = get_translations()
    lang = st.session_state.language
    
    st.title(t["welcome_title"])
    st.markdown(t["welcome_subtitle"])
    st.markdown("---")
    
    # Get all options with current language
    options = get_all_options(lang)
    
    # Find the primary/featured option (Ask for Help)
    featured_option = next((opt for opt in options if opt.get('primary')), options[0])
    other_options = [opt for opt in options if not opt.get('primary')]
    
    # Display featured option prominently
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
        <h2 style="color: white; margin-bottom: 0.5rem;">{t["ask_for_help_card"]["title"]}</h2>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem;">{t["ask_for_help_card"]["text"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(t["ask_for_help_card"]["button"], key="btn_ask_for_help", use_container_width=True, type="primary"):
        st.session_state.selected_option = featured_option['key']
        st.session_state.current_view = "questions"
        st.rerun()
    
    st.markdown("---")
    st.markdown(t["or_choose_task"])
    
    # Display other options in 2x2 grid
    col1, col2 = st.columns(2)
    
    with col1:
        # Option 1: Check Benefits
        st.markdown(f"### {other_options[0]['title']}")
        st.markdown(other_options[0]['description'])
        if st.button(t["start_button"], key="btn_check_benefits"):
            st.session_state.selected_option = other_options[0]['key']
            st.session_state.current_view = "questions"
            st.rerun()
        st.markdown("")
        
        # Option 3: Explain Policy
        if len(other_options) > 2:
            st.markdown(f"### {other_options[2]['title']}")
            st.markdown(other_options[2]['description'])
            if st.button(t["start_button"], key="btn_explain_policy"):
                st.session_state.selected_option = other_options[2]['key']
                st.session_state.current_view = "questions"
                st.rerun()
    
    with col2:
        # Option 2: Verify Eligibility
        if len(other_options) > 1:
            st.markdown(f"### {other_options[1]['title']}")
            st.markdown(other_options[1]['description'])
            if st.button(t["start_button"], key="btn_eligibility"):
                st.session_state.selected_option = other_options[1]['key']
                st.session_state.current_view = "questions"
                st.rerun()
            st.markdown("")
        
        # Option 4: Help Application
        if len(other_options) > 3:
            st.markdown(f"### {other_options[3]['title']}")
            st.markdown(other_options[3]['description'])
            if st.button(t["start_button"], key="btn_help_application"):
                st.session_state.selected_option = other_options[3]['key']
                st.session_state.current_view = "questions"
                st.rerun()
    
    st.markdown("---")
    st.markdown(t["ask_directly_header"])
    
    # Free-form query option
    custom_query = st.text_input(
        "Type your question here...",
        placeholder=t["ask_placeholder"],
        label_visibility="collapsed"
    )
    
    if st.button(t["ask_button"], key="btn_custom_query"):
        if custom_query.strip():
            # Process custom query through orchestrator
            process_custom_query(custom_query)
        else:
            st.warning("Please enter a question")


def show_questions_page():
    """Display question collection page based on selected option."""
    t = get_translations()
    lang = st.session_state.language
    option_key = st.session_state.selected_option
    
    config = get_option_config(option_key, lang)
    
    if not config:
        st.error("Invalid option selected")
        reset_to_home()
        return
    
    # Header
    st.title(config['title'])
    st.markdown(f"_{config['description']}_")
    
    # Show entry message for conversational flow
    if config.get('conversational'):
        st.markdown("---")
        if config.get('entry_message'):
            st.markdown(f"""
            <div class="info-box">
                {config['entry_message'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
        if config.get('privacy_assurance'):
            st.info(f"🔒 {config['privacy_assurance']}")
    
    st.markdown("---")
    
    # Back button
    if st.button(t["back_home"]):
        reset_to_home()
        st.rerun()
    
    st.markdown("")
    
    # Create form for questions
    with st.form(key="question_form"):
        answers = {}
        
        for question in config['questions']:
            q_id = question['id']
            q_label = question['label']
            q_type = question['type']
            q_required = question.get('required', False)
            q_help = question.get('help_text', '')
            
            # Display question based on type
            if q_type == "number":
                value = st.number_input(
                    q_label,
                    min_value=0,
                    value=None,
                    help=q_help,
                    placeholder=question.get('placeholder', ''),
                    key=f"q_{q_id}"
                )
                if value is not None:
                    answers[q_id] = value
                    
            elif q_type == "text":
                value = st.text_input(
                    q_label,
                    help=q_help,
                    placeholder=question.get('placeholder', ''),
                    key=f"q_{q_id}"
                )
                if value:
                    answers[q_id] = value
                    
            elif q_type == "textarea":
                value = st.text_area(
                    q_label,
                    help=q_help,
                    placeholder=question.get('placeholder', ''),
                    key=f"q_{q_id}"
                )
                if value:
                    answers[q_id] = value
                    
            elif q_type == "selectbox":
                options = question.get('options', [])
                value = st.selectbox(
                    q_label,
                    options=[""] + options if not q_required else options,
                    help=q_help,
                    key=f"q_{q_id}"
                )
                if value:
                    answers[q_id] = value
                    
            elif q_type == "multiselect":
                options = question.get('options', [])
                value = st.multiselect(
                    q_label,
                    options=options,
                    help=q_help,
                    key=f"q_{q_id}"
                )
                if value:
                    answers[q_id] = value
            
            # NEW: Quick select (radio buttons) for conversational flow
            elif q_type == "quick_select":
                options = question.get('options', [])
                # Show conversational prompt if available
                if question.get('conversational_prompt'):
                    st.markdown(f"**{question['conversational_prompt']}**")
                value = st.radio(
                    q_label,
                    options=options,
                    help=q_help,
                    key=f"q_{q_id}",
                    label_visibility="collapsed" if question.get('conversational_prompt') else "visible"
                )
                if value:
                    answers[q_id] = value
        
        # Submit button
        submitted = st.form_submit_button(t["submit_button"], use_container_width=True)
        
        if submitted:
            # Validate required fields
            validation_errors = validate_answers(config['questions'], answers)
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                # Store answers and process
                st.session_state.collected_answers = answers
                process_with_agent(option_key, config, answers)


def validate_answers(questions: List[Dict], answers: Dict[str, Any]) -> List[str]:
    """Validate collected answers."""
    t = get_translations()
    errors = []
    
    for question in questions:
        q_id = question['id']
        q_label = question['label']
        q_required = question.get('required', False)
        
        if q_required and q_id not in answers:
            errors.append(f"❌ {q_label} {t['validation']['required']}")
            continue
        
        if q_id not in answers:
            continue
            
        value = answers[q_id]
        
        # Type-specific validation
        if q_id == "age":
            is_valid, _, error = validate_age(str(value))
            if not is_valid:
                errors.append(f"❌ Age: {error}")
                
        elif q_id == "annual_income":
            is_valid, _, error = validate_income(str(value))
            if not is_valid:
                errors.append(f"❌ Income: {error}")
                
        elif q_id == "family_size":
            is_valid, _, error = validate_family_size(str(value))
            if not is_valid:
                errors.append(f"❌ Family Size: {error}")
                
        elif q_id == "scheme_name":
            is_valid, _, error = validate_scheme_name(value)
            if not is_valid:
                errors.append(f"❌ Scheme Name: {error}")
                
        elif q_id == "policy_name":
            is_valid, _, error = validate_policy_name(value)
            if not is_valid:
                errors.append(f"❌ Policy Name: {error}")
    
    return errors


def build_query_from_answers(option_key: str, answers: Dict[str, Any]) -> str:
    """Build a natural language query from collected answers."""
    # Constructed query can remain in English/Mixed as LLM handles it.
    # We use the user's provided answers which might be in local language.
    
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
        if special and "None of these" not in special:
            query_parts.append(f"Special conditions: {', '.join(special)}.")
            
        return " ".join(query_parts)
    
    return ""


def process_with_agent(option_key: str, config: Dict, answers: Dict[str, Any]):
    """Process the query with the appropriate agent."""
    t = get_translations()
    lang = st.session_state.language
    
    # Build natural language query
    query = build_query_from_answers(option_key, answers)
    
    logger.info(f"Processing with agent. Option: {option_key}, Query: {query}, Lang: {lang}")
    
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
    
    # Show processing status
    with st.spinner(t["processing_spinner"]):
        status_placeholder = st.empty()
        
        try:
            # Thread config for memory
            thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            # Prepare inputs
            inputs = {
                "input_text": query,
                "messages": [HumanMessage(content=query)],
                "user_profile": user_profile,
                "selected_option": option_key,
                "collected_answers": answers,
                "current_intent": config['agent_mapping'],  # Force specific agent
                "language": lang  # Pass language to graph
            }
            
            final_response = ""
            
            # Stream events
            for event in app.stream(inputs, config=thread_config):
                for key, value in event.items():
                    # Update status
                    if key == "orchestrator":
                        status_placeholder.info("🧠 Routing your request...")
                    elif key == "conversation_agent":
                        status_placeholder.info("🗣️ Analyzing your situation...")
                    elif key == "policy_agent":
                        status_placeholder.info("📜 Analyzing policy documents...")
                    elif key == "eligibility_agent":
                        status_placeholder.info("✅ Checking eligibility criteria...")
                    elif key == "benefit_agent":
                        status_placeholder.info("💰 Searching for matching benefits...")
                    elif key == "advocacy_agent":
                        status_placeholder.info("📢 Preparing application guidance...")
                    
                    # Capture response
                    if "messages" in value and value["messages"]:
                        msg = value["messages"][-1]
                        content = msg.content if hasattr(msg, "content") else str(msg)
                        final_response = content
            
            status_placeholder.success(t["processing_success"])
            
            # Store and display response
            st.session_state.agent_response = final_response
            st.session_state.current_view = "results"
            st.rerun()
            
        except Exception as e:
            status_placeholder.empty()
            st.error(f"{t['error_title']}: {str(e)}")
            logger.error(f"Agent processing error: {e}")


def process_custom_query(query: str):
    """Process a custom free-form query."""
    t = get_translations()
    lang = st.session_state.language
    
    logger.info(f"Processing custom query: {query}, Lang: {lang}")
    
    with st.spinner(t["processing_spinner"]):
        status_placeholder = st.empty()
        
        try:
            thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            inputs = {
                "input_text": query,
                "messages": [HumanMessage(content=query)],
                "language": lang  # Pass language to graph
            }
            
            final_response = ""
            
            for event in app.stream(inputs, config=thread_config):
                for key, value in event.items():
                    if key == "orchestrator":
                        status_placeholder.info("🧠 Understanding your question...")
                    elif key in ["policy_agent", "eligibility_agent", "benefit_agent", "advocacy_agent"]:
                        status_placeholder.info(f"Processing with {key.replace('_', ' ').title()}...")
                    
                    if "messages" in value and value["messages"]:
                        msg = value["messages"][-1]
                        content = msg.content if hasattr(msg, "content") else str(msg)
                        final_response = content
            
            status_placeholder.success(t["processing_success"])
            
            # Display response inline
            st.markdown("### 💡 Answer")
            st.markdown(final_response)
            
        except Exception as e:
            status_placeholder.empty()
            st.error(f"{t['error_title']}: {str(e)}")
            logger.error(f"Custom query error: {e}")


def show_results_page():
    """Display the agent response."""
    t = get_translations()
    st.title(t["results_title"])
    
    # Back button
    if st.button(t["start_new"]):
        reset_to_home()
        st.rerun()
    
    st.markdown("---")
    
    # Display the response
    if st.session_state.agent_response:
        st.markdown(st.session_state.agent_response)
    else:
        st.error(t["no_response"])
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["back_home_button"], use_container_width=True):
            reset_to_home()
            st.rerun()
    with col2:
        if st.button(t["try_another"], use_container_width=True):
            st.session_state.current_view = "home"
            st.session_state.agent_response = None
            st.rerun()


# Main app routing
def main():
    """Main application entry point."""
    
    view = st.session_state.current_view
    
    if view == "home":
        show_home_page()
    elif view == "questions":
        show_questions_page()
    elif view == "results":
        show_results_page()
    else:
        show_home_page()


if __name__ == "__main__":
    main()
