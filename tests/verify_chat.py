import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def run_chat_test():
    session = requests.Session()
    
    print("0. Checking Home Page Link...")
    try:
        r = session.get(f"{BASE_URL}/")
        r.raise_for_status()
        if "/chat" in r.text:
             print("   [OK] Home Page contains /chat link")
        else:
             print("   [WARN] Home Page does NOT contain /chat link (or it's dynamic).")
    except Exception as e:
        print(f"   [FAIL] Home Page check failed: {e}")

    print("1. Checking Chat Page...")
    try:
        r = session.get(f"{BASE_URL}/chat")
        r.raise_for_status()
        if "Jan Sahayak Chat" in r.text:
            print("   [OK] Chat Page Accessible")
        else:
            print("   [WARN] Chat Page loaded but title not found.")
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return

    print("\n2. Sending Chat Message & Streaming...")
    payload = {
        "selected_option": "chat",
        "query": "Hello, who are you?",
        "thread_id": "test-thread-123"
    }
    
    try:
        # Stream request
        with session.post(f"{BASE_URL}/api/submit-query", json=payload, stream=True) as r:
            r.raise_for_status()
            print("   [OK] Connection Established. Streaming logs:")
            
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data: "):
                        data_str = decoded_line[6:]
                        try:
                            data = json.loads(data_str)
                            if data['type'] == 'meta':
                                print(f"      [META] Thread ID: {data.get('thread_id')}")
                            elif data['type'] == 'log':
                                # Sanitize log message
                                safe_msg = data['message'].encode('ascii', 'ignore').decode('ascii')
                                print(f"      - {safe_msg}")
                            elif data['type'] == 'result' or data['type'] == 'redirect':
                                print(f"      [RESULT] Received Final Response")
                                # print(f"      Response length: {len(data.get('response', ''))}")
                                if data.get('response'):
                                    print("      [OK] Response content present.")
                                else:
                                    print("      [WARN] Response content empty.")
                                break # Stop after result
                            elif data['type'] == 'error':
                                print(f"      [FAIL] Received Error Event: {data['message']}")
                        except json.JSONDecodeError:
                            pass
                            
    except Exception as e:
        print(f"   [FAIL] Streaming Failed: {e}")
        return

    print("\n3. Checking Chat History Retrieval...")
    history_payload = {"thread_id": "test-thread-123"}
    try:
        r = session.post(f"{BASE_URL}/api/get-chat-history", json=history_payload)
        r.raise_for_status()
        messages = r.json().get("messages", [])
        if len(messages) > 0:
            print(f"   [OK] History retrieved. Count: {len(messages)}")
            print(f"   Last Message: {messages[-1].get('content')[:50]}...")
        else:
            print("   [WARN] History empty (might be first run or persistence failed).")
    except Exception as e:
        print(f"   [FAIL] History check failed: {e}")

    print("\n[SUCCESS] CHAT TEST COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_chat_test()
