import os
import sys

# Ensure project root is in path to allow 'src' imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph import app
from src.logger import setup_logger
from src.langsmith_config import setup_langsmith
from langchain_core.messages import HumanMessage

import json
import time
from datetime import datetime
from pathlib import Path

logger = setup_logger("Main")

# Enable LangSmith tracing
setup_langsmith()

def save_session_history(thread_id, messages):
    """
    Saves the session history to a JSON file.
    """
    if not messages:
        return
        
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    filename = f"session_{thread_id}_{int(time.time())}.json"
    filepath = os.path.join(log_dir, filename)
    
    history_data = []
    for msg in messages:
        content = msg.content if hasattr(msg, "content") else str(msg)
        msg_type = type(msg).__name__
        history_data.append({"type": msg_type, "content": content})
    
    try:
        with open(filepath, "w") as f:
            json.dump(history_data, f, indent=2)
        logger.info(f"Session history saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save session history: {e}")

def main():
    print("\n=============================================")
    print("Civic Assistance Agent System (Zynd Enhanced)")
    print("---------------------------------------------")
    print("Type 'exit' or 'quit' to stop.")
    print("=============================================\n")
    
    logger.info("System initializing...")
    
    # Initialize thread configuration for conversation memory
    thread_id = "1" # In a real app, this would be dynamic per user
    thread_config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        try:
            query = input("\nUser (Question): ").strip()
            
            if not query:
                continue
                
            if query.lower() in ["exit", "quit"]:
                logger.info("User requested exit.")
                # Retrieve full state history to save
                current_state = app.get_state(thread_config)
                if current_state and current_state.values:
                    save_session_history(thread_id, current_state.values.get("messages", []))
                break
            
            logger.info(f"Processing query: {query}")
            
            # With checkpointer, we only need to pass the new input. 
            # The graph will append it to history.
            inputs = {
                "input_text": query,
                "messages": [HumanMessage(content=query)]
            }
            
            print("\n--- Agent Response ---")
            
            # Stream output
            for event in app.stream(inputs, config=thread_config):
                for key, value in event.items():
                    # logger.debug(f"Node '{key}' completed.")
                    if "messages" in value:
                        msg = value["messages"][-1]
                        content = msg.content if hasattr(msg, "content") else str(msg)
                        # Print only the AI response clearly to the user
                        print(f"\n[{key.upper()}]: {content}") 
                    if "current_intent" in value:
                         logger.info(f"Orchestrator routed to: {value['current_intent']}")
            
            print("\n----------------------")

        except KeyboardInterrupt:
            print("\n\nExiting...")
            # Attempt save on interrupt too
            try:
                current_state = app.get_state(thread_config)
                if current_state and current_state.values:
                    save_session_history(thread_id, current_state.values.get("messages", []))
            except:
                pass
            break
        except Exception as e:
            logger.error(f"Runtime Error: {e}")
            import traceback
            traceback.print_exc()
    
    logger.info("Execution finished.")

if __name__ == "__main__":
    main()
