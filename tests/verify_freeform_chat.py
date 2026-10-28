import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def run_test():
    session = requests.Session()
    thread_id = f"test-freeform-{int(time.time())}"
    print(f"=== Testing Free-form Chat (Thread: {thread_id}) ===\n")

    conversations = [
        {
            "input": "Hello",
            "expect_context": False,
            "desc": "Initial Greeting"
        },
        {
            "input": "Tell me about PM Kisan Samman Nidhi",
            "expect_context": "PM Kisan",
            "desc": "Specific Query"
        },
        {
            "input": "Who is eligible for it?",
            "expect_context": "landholder", # Keyword likely in PM Kisan eligibility
            "desc": "Contextual Follow-up"
        }
    ]

    for turn in conversations:
        print(f"Sending: '{turn['input']}' ({turn['desc']})...")
        payload = {
            "selected_option": "chat",
            "query": turn['input'],
            "thread_id": thread_id
        }
        
        full_response = ""
        try:
            with session.post(f"{BASE_URL}/api/submit-query", json=payload, stream=True) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:]
                            try:
                                data = json.loads(data_str)
                                if data['type'] == 'result' or data['type'] == 'redirect':
                                    full_response = data.get('response', '')
                            except json.JSONDecodeError:
                                pass
            
            print(f"Response: {full_response[:100]}...")
            
            if turn['expect_context']:
                if isinstance(turn['expect_context'], str) and turn['expect_context'].lower() in full_response.lower():
                    print("   [OK] Context validated.")
                elif isinstance(turn['expect_context'], bool):
                    print("   [OK] Response received.")
                else:
                     print(f"   [WARN] Expected context '{turn['expect_context']}' not found clearly.")
            
        except Exception as e:
            print(f"   [FAIL] Error: {e}")
            break
        
        time.sleep(1) 

if __name__ == "__main__":
    try:
        run_test()
    except KeyboardInterrupt:
        print("\nTest stopped.")
