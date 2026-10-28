import os
import sys
import uuid
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Ensure project root is in path to allow 'src' imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.graph import app as graph_app
from src.question_config import get_option_config, get_all_options
from langchain_core.messages import HumanMessage

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configurations
THREAD_ID_KEY = "thread_id"

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/service/<option_key>')
def service_form(option_key):
    """Render dynamic form based on service type."""
    config = get_option_config(option_key)
    if not config:
        return redirect(url_for('index'))
    
    return render_template('form.html', config=config, option_key=option_key)

@app.route('/eligibility')
def eligibility_form():
    """Legacy route redirect."""
    return redirect(url_for('service_form', option_key='eligibility_verification'))

@app.route('/processing')
def processing():
    """Render the intermediate processing page."""
    # Retrieve what option was selected from query param or default
    selected_option = request.args.get('option', 'unknown')
    return render_template('processing.html', selected_option=selected_option)

@app.route('/results')
def results():
    """Render the results page with data from the session."""
    response_content = session.get('agent_response', "No response generated.")
    reference_id = session.get('reference_id', "N/A")
    return render_template('results.html', response=response_content, reference_id=reference_id)

def build_query_from_answers(option_key, answers):
    """Build a natural language query from collected answers (Logic from user_interface.py)."""
    
    if option_key == "check_benefits":
        query_parts = [
            "I am looking for government benefits and schemes I may qualify for.",
            f"I am {answers.get('age')} years old",
            f"with an annual household income of ₹{answers.get('annual_income', 0)}.",
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
            f"with an annual income of ₹{answers.get('annual_income', 0)}.",
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

# Simple in-memory storage for results (since streaming response prevents setting session cookie)
RESULTS_CACHE = {}

@app.route('/api/store_result', methods=['POST'])
def store_result():
    """Store the result in session after streaming is complete."""
    data = request.json
    session['agent_response'] = data.get('response')
    session['reference_id'] = data.get('reference_id')
    return jsonify({"status": "success"})

@app.route('/api/get-chat-history', methods=['POST'])
def get_chat_history():
    """Retrieve chat history for a given thread_id."""
    data = request.json
    thread_id = data.get('thread_id')
    if not thread_id:
        return jsonify({"messages": []})
    
    thread_config = {"configurable": {"thread_id": thread_id}}
    try:
        # Get current state
        state = graph_app.get_state(thread_config)
        if not state.values:
            return jsonify({"messages": []})
            
        messages = state.values.get("messages", [])
        # Serialize messages
        formatted_messages = []
        for msg in messages:
            role = "user" if msg.type == "human" else "bot"
            formatted_messages.append({
                "role": role,
                "content": msg.content
            })
            
        return jsonify({"messages": formatted_messages})
    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear-chat', methods=['POST'])
def clear_chat():
    """
    Clears the chat history for a given thread_id.
    """
    try:
        data = request.json
        thread_id = data.get('thread_id')
        if not thread_id:
            return jsonify({"error": "No thread_id provided"}), 400

        # Create the configuration for the specific thread
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get the current state
        state = graph_app.get_state(config)
        
        # If there is history, we can clear the messages
        if state and hasattr(state, 'values') and "messages" in state.values:
            from langchain_core.messages import RemoveMessage
            
            # Find all message IDs to remove
            messages = state.values["messages"]
            if messages:
                # Create a list of RemoveMessage objects for every message in history
                removals = [RemoveMessage(id=msg.id) for msg in messages if hasattr(msg, 'id')]
                
                if removals:
                    # Update the graph state by sending these removals
                    graph_app.update_state(config, {"messages": removals})
                    print(f"Cleared {len(removals)} messages for thread {thread_id}")

        return jsonify({"status": "success", "message": "Chat history cleared"})
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat')
def chat_interface():
    """Render the conversational chat interface."""
    return render_template('chat.html')

@app.route('/api/submit-query', methods=['POST'])
def submit_query():
    """
    API Endpoint to process the user query through the LangGraph agent.
    Streams events (logs) back to the client.
    """
    data = request.json
    selected_option = data.get('selected_option', 'custom')
    collected_answers = data.get('collected_answers', {})
    print(f"\n[API] submit-query received: option={selected_option}")
    print(f"[API] Payload: {json.dumps(data, indent=2)}")
    
    # 1. Build Query
    query = build_query_from_answers(selected_option, collected_answers)
    if not query:
        query = data.get('query', '')

    if not query:
        return jsonify({"error": "No query provided"}), 400

    # 2. Build User Profile
    user_profile = {
        "age": collected_answers.get("age"),
        "annual_income": collected_answers.get("annual_income"),
        "location": collected_answers.get("location"),
        "employment_status": collected_answers.get("employment_status"),
        "family_size": collected_answers.get("family_size"),
        "education_level": collected_answers.get("education_level"),
        "social_category": collected_answers.get("social_category")
    }

    # 3. Get Agent Mapping
    config = get_option_config(selected_option)
    
    # First, try to get intent from the incoming data
    current_intent = data.get('intent')
    
    # Force intent for chat option to avoid Orchestrator routing to other agents
    if selected_option == "chat":
        current_intent = "CONVERSATION_DISCOVERY"
    # If intent was not explicitly provided in data and it's not a chat option,
    # then use the agent_mapping from the config.
    elif current_intent is None:
        current_intent = config.get('agent_mapping') if config else None

    # Thread ID (Use provided or generate new)
    thread_id = data.get('thread_id') or str(uuid.uuid4())
    thread_config = {"configurable": {"thread_id": thread_id}}
    
    # 4. Prepare Inputs
    # For chat, we might not want to force markdown prompting every time if it feels unnatural, 
    # but strictly structured output is good for the agent.
    final_query_text = query
    if selected_option != "chat":
         final_query_text += "\n\nIMPORTANT: Please format your response using clear Markdown. Use level 2/3 headers for sections, bullet points for lists, and bold text for key information."

    inputs = {
        "input_text": final_query_text,
        "messages": [HumanMessage(content=final_query_text)],
        "user_profile": user_profile,
        "selected_option": selected_option,
        "collected_answers": collected_answers,
        "current_intent": current_intent, 
        "language": "en" 
    }

    def generate():
        final_response = ""
        try:
            # Send initial metadata event with thread_id
            yield f"data: {json.dumps({'type': 'meta', 'thread_id': thread_id})}\n\n"
            yield f"data: {json.dumps({'type': 'log', 'message': '🧠 Orchestrator: Processing request...'})}\n\n"
            
            # Stream events from the graph
            for event in graph_app.stream(inputs, config=thread_config):
                for key, value in event.items():
                    # Map agent keys to user-friendly messages
                    log_message = ""
                    if key == "orchestrator":
                        log_message = "🧠 Orchestrator: Analyzing intent..."
                    elif key == "conversation_agent":
                        log_message = "🗣️ Conversation Agent: Refining query..."
                    elif key == "policy_agent":
                        log_message = "📜 Policy Agent: Searching regulations..."
                    elif key == "eligibility_agent":
                        log_message = "✅ Eligibility Agent: Verifying criteria..."
                    elif key == "benefit_agent":
                        log_message = "💰 Benefit Agent: Finding schemes..."
                    elif key == "advocacy_agent":
                        log_message = "📢 Advocacy Agent: Preparing guidance..."
                    else:
                        log_message = f"⚙️ System: Processing with {key}..."
                    
                    yield f"data: {json.dumps({'type': 'log', 'message': log_message})}\n\n"

                    if "messages" in value and value["messages"]:
                        msg = value["messages"][-1]
                        content = msg.content if hasattr(msg, "content") else str(msg)
                        final_response = content
            
            # Final Event with result
            reference_id = f"ZY-{uuid.uuid4().hex[:8].upper()}"
            yield f"data: {json.dumps({'type': 'result', 'url': url_for('results'), 'response': final_response, 'reference_id': reference_id})}\n\n"

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Streaming Error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    from flask import Response, stream_with_context
    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response

if __name__ == '__main__':
    # Ensure threaded=True to handle multiple concurrent requests (SSE occupies one thread)
    # Disable reloader to prevent "Detected change in torch..." restarts
    app.run(debug=True, port=5000, threaded=True, use_reloader=False)
