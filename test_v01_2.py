from vinni.core import ChatBot
import os
import time

def test_v01_2():
    print("Testing ViNNi v0.1.2 Features...")
    
    prompt_path = "prompts/system_v0.1.2.md"
    if not os.path.exists(prompt_path):
        print(f"FAILURE: Prompt file not found at {prompt_path}")
        return

    bot = ChatBot(model_name="llama3.1", system_prompt_path=prompt_path)
    
    # Test 1: Static Capabilities Check via code intercept
    print("\n--- Testing Static Capabilities ---")
    response_cap = ""
    for chunk in bot.chat("What can you do?"):
        response_cap += chunk
    
    print(f"Response: {response_cap.strip()}")
    
    if "- CHAT" in response_cap and "General conversation" in response_cap:
        print("[PASS] Static capabilities response triggered.")
    else:
        print("[FAIL] Capabilities response looked dynamic or wrong.")

    # Test 2: Locked Identity via Prompt
    print("\n--- Testing Locked Identity ---")
    response_id = ""
    for chunk in bot.chat("Who created you?"):
        response_id += chunk
    
    print(f"Response: {response_id.strip()}")
    # Using stricter check based on prompt v0.1.2
    if "locally run AI system" in response_id and "Abhishek Arora" in response_id:
         print("[PASS] Identity matches template.")
    else:
         print("[FAIL] Identity template not followed.")

if __name__ == "__main__":
    test_v01_2()
