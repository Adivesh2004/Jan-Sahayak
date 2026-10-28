import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath("."))
load_dotenv()

# --- MOCKING BLOCKING DEPENDENCIES ---
# The src.config.get_zynd_agent function attempts to start a Flask server
# which blocks this script. We mock it here before importing graph.
import src.config
src.config.get_zynd_agent = lambda agent_name="default": None
print("Mocked get_zynd_agent to prevent server startup.")
# -------------------------------------

from src.graph import app
from langchain_core.messages import HumanMessage
from src.state import AgentState

def verify_lang(language: str, greeting_expected_snippet: str):
    print(f"\n--- Verifying {language} ---")
    state = {
        "messages": [HumanMessage(content="Ask for help")],
        "language": language,
        "input_text": "Ask for help"
    }
    
    # Run the graph
    print("Invoking graph...")
    try:
        # Checkpointer requires thread_id
        config = {"configurable": {"thread_id": f"test_{language}_mocked"}}
        result = app.invoke(state, config=config)
        
        # Check if result contains expected greeting
        messages = result.get("messages", [])
        if messages:
            last_msg = messages[-1].content
            # Handle potential encoding issues in print
            safe_msg = last_msg.encode('ascii', 'ignore').decode('ascii')
            full_msg_repr = repr(last_msg)
            
            print(f"Response (safe): {safe_msg[:100]}...")
            
            # Check snippet in original unicode string
            if greeting_expected_snippet in last_msg:
                print(f"[SUCCESS] Found expected greeting snippet")
            else:
                print(f"[FAILURE] Expected snippet not found.")
                print(f"Full response repr: {full_msg_repr[:200]}")
        else:
            print("[FAILURE] No messages returned.")
            
    except Exception as e:
        print(f"[EXCEPTION] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test English
    verify_lang("en", "Namaste")
    
    # Test Hindi
    verify_lang("hi", "नमस्ते")
    
    # Test Kannada
    verify_lang("kn", "ನಮಸ್ಕಾರ")
