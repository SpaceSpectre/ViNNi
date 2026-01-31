from vinni.core import ChatBot
import os
import json
import time

def test_v01_3():
    print("Testing ViNNi v0.1.3 Observability...")
    
    prompt_path = "prompts/system_v0.1.2.md"
    bot = ChatBot(model_name="llama3.1", system_prompt_path=prompt_path)
    
    # Test 1: Static Identity Check
    print("\n--- Testing Static Identity ---")
    response_id = ""
    for chunk in bot.chat("Who created you?"):
        response_id += chunk
    
    print(f"Response: {response_id.strip()}")
    print(f"Tokens Recorded: {bot.last_turn_tokens}")
    
    if "Abhishek Arora" in response_id and bot.last_turn_tokens > 5:
         print("[PASS] Identity static & tokens tracked.")
    else:
         print("[FAIL] Identity or token count issue.")

    # Test 2: Log Schema Check
    print("\n--- Testing Log Schema ---")
    time.sleep(1)
    if os.path.exists("vinni.log"):
        with open("vinni.log", "r") as f:
            lines = f.readlines()
            last_line = lines[-1]
            data = json.loads(last_line)
            
            required = ["session_id", "system_prompt_version", "input_tokens", "output_tokens"]
            missing = [k for k in required if k not in data]
            
            if not missing:
                print(f"[PASS] Log schema valid. SessionID: {data['session_id']}")
            else:
                print(f"[FAIL] Missing log fields: {missing}")
    else:
        print("[FAIL] No log file found.")

if __name__ == "__main__":
    test_v01_3()
