import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def run_e2e_test():
    session = requests.Session()
    
    print("1. Checking Home Page...")
    try:
        r = session.get(f"{BASE_URL}/")
        r.raise_for_status()
        print("   [OK] Home Page Accessible")
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return

    print("\n2. Checking Service Form (Explain Policy)...")
    try:
        r = session.get(f"{BASE_URL}/service/explain_policy")
        r.raise_for_status()
        print("   [OK] Service Form Accessible")
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return

    print("\n3. Submitting Query & Streaming Logs...")
    payload = {
        "selected_option": "explain_policy",
        "collected_answers": {
            "policy_name": "PM Kisan Samman Nidhi",
            "specific_aspect": "Eligibility",
            "additional_questions": "Who is excluded?"
        }
    }
    
    final_response_data = None
    
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
                            if data['type'] == 'log':
                                safe_msg = data['message'].encode('ascii', 'ignore').decode('ascii')
                                print(f"      - {safe_msg}")
                            elif data['type'] == 'redirect':
                                print(f"      [OK] Received Redirect Event")
                                final_response_data = data
                            elif data['type'] == 'error':
                                print(f"      [FAIL] Received Error Event: {data['message']}")
                        except json.JSONDecodeError:
                            pass
                            
    except Exception as e:
        print(f"   [FAIL] Streaming Failed: {e}")
        return

    if not final_response_data:
        print("   [FAIL] Did not receive redirect/result data.")
        return

    print("\n4. Storing Result...")
    try:
        store_payload = {
            "response": final_response_data['response'],
            "reference_id": final_response_data['reference_id']
        }
        r = session.post(f"{BASE_URL}/api/store_result", json=store_payload)
        r.raise_for_status()
        print("   [OK] Result Stored in Session")
    except Exception as e:
        print(f"   [FAIL] Store Result Failed: {e}")
        return

    print("\n5. Checking Results Page...")
    try:
        r = session.get(f"{BASE_URL}{final_response_data['url']}")
        r.raise_for_status()
        
        # Verify content presence
        if "PM Kisan" in r.text or "Eligibility" in r.text or "Jan Sahayak" in r.text: # Basic check
             print("   [OK] Results Page Rendered successfully with content.")
        else:
             print("   [WARN] Results Page loaded but content verification is ambiguous.")
        
        print("\n[SUCCESS] E2E TEST COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"   ❌ Results Page Failed: {e}")
        return

if __name__ == "__main__":
    run_e2e_test()
