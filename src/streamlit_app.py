import streamlit as st
import sys
import os
import time

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph import app
from src.logger import setup_logger
from src.langsmith_config import setup_langsmith, get_langsmith_url
from langchain_core.messages import HumanMessage, AIMessage
from src.languages import TRANSLATIONS
import src.user_interface as ui

logger = setup_logger("StreamlitApp")

# Enable LangSmith tracing
langsmith_enabled = setup_langsmith()

st.set_page_config(
    page_title="Zynd Civic Agent",
    page_icon="🤖",
    layout="wide"
)

# Initialize Session State for Language
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
    st.session_state.language = lang_map[lang_choice]

# Get current language translations
lang = st.session_state.language
t = TRANSLATIONS[lang]

st.title(t["app_title"])
st.markdown(t["hero_subtitle"])

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)

# User Input
if prompt := st.chat_input(t["ask_placeholder"]):
    # Add User Message to History
    user_msg = HumanMessage(content=prompt)
    st.session_state.messages.append(user_msg)
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process with Agent
    with st.chat_message("assistant"):
        logger.info(f"Processing query: {prompt}")
        
        # Container for thought process
        status_container = st.status(t["thinking"], expanded=True)
        final_response = ""
        
        try:
            # Thread Config for Memory
            thread_config = {"configurable": {"thread_id": "streamlit_user"}}
            
            inputs = {
                "input_text": prompt,
                "messages": [user_msg],
                "language": lang  # Pass language to graph
            }
            
            # Stream events
            for event in app.stream(inputs, config=thread_config):
                for key, value in event.items():
                    # Update status for each node execution
                    if key == "orchestrator":
                        status_container.write("🧠 **Orchestrator** is routing your request...")
                    elif key == "policy_agent":
                        status_container.write("📜 **Policy Agent** is analyzing regulations...")
                    elif key == "eligibility_agent":
                        status_container.write("✅ **Eligibility Agent** is checking criteria...")
                    elif key == "benefit_agent":
                        status_container.write("💰 **Benefit Agent** is searching for schemes...")
                    elif key == "advocacy_agent":
                        status_container.write("📢 **Advocacy Agent** is preparing a plan...")
                    
                    # Log internal decisions if available
                    if "current_intent" in value:
                        intent = value["current_intent"]
                        status_container.info(f"Routed to: `{intent}`")
                    
                    # Capture Response
                    if "messages" in value:
                        msg = value["messages"][-1]
                        content = msg.content if hasattr(msg, "content") else str(msg)
                        final_response = content
                        
            status_container.update(label=t["processing_success"], state="complete", expanded=False)
            
            if final_response:
                st.markdown(final_response)
                st.session_state.messages.append(AIMessage(content=final_response))
            else:
                st.warning(t["no_response"])
                
        except Exception as e:
            status_container.update(label=t["error_title"], state="error")
            st.error(f"An error occurred: {e}")
            logger.error(f"Streamlit Error: {e}")

# Call UI functions with language
if __name__ == "__main__":
    # We need to make sure user_interface also knows about the session state language
    # But since user_interface functions will be called from here (or we rely on main there?),
    # Wait, streamlit_app imports user_interface but doesn't use it in the original code logic I saw above?
    # Ah, I see `from src.graph import app` in `streamlit_app.py`.
    # AND `src/user_interface.py` has a `main()` function. 
    # Usually one runs `streamlit run src/streamlit_app.py` OR `src/user_interface.py`.
    # The original `streamlit_app.py` was a simple chat interface. `user_interface.py` was the complex one.
    # The user asked me to "implement it". I should probably assume they are using `user_interface.py` as the main entry point 
    # OR that both exist. 
    # In my previous listing `user_interface.py` had `if __name__ == "__main__": main()`.
    # And `streamlit_app.py` was also a standalone app.
    # I should update `user_interface.py` as that seems to be the "Civic Assistance Platform" with buttons.
    # I will also update `streamlit_app.py` just in case, which I just did. 
    pass
