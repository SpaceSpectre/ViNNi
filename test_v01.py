from vinni.core import ChatBot
from vinni.monitor import SecurityLogger
import os
import time

def test_v01():
    print("Testing ViNNi v0.1 Features...")
    
    # 1. Initialize with v0.1.1 prompt
    prompt_path = "prompts/system_v0.1.1.md"
    if not os.path.exists(prompt_path):
        print(f"FAILURE: Prompt file not found at {prompt_path}")
        return

    bot = ChatBot(model_name="llama3.1", system_prompt_path=prompt_path)
    
    # 2. Test Intent Tagging
    cases = [
        ("Write a python function to sum numbers", "CODE"),
        ("Analyze the impact of interest rates", "ANALYSIS"),
        ("How are you?", "CHAT"), # Regression test for issue: "how" -> ANALYSIS
        ("How do I install python?", "ANALYSIS") # Should still catch technical 'how'
    ]
    
    print("\n--- Testing Intent Tagger ---")
    for text, expected in cases:
        actual = bot.get_last_intent(text)
        if actual == expected:
            print(f"[PASS] '{text}' -> {actual}")
        else:
            print(f"[FAIL] '{text}' -> Got {actual}, Expected {expected}")

    # 3. Test Chat & Logging
    print("\n--- Testing Chat & Logging ---")
    log_file = "vinni.log"
    
    # Capture current log size/content
    start_size = 0
    if os.path.exists(log_file):
        start_size = os.path.getsize(log_file)
        
    print("Sending chat request...")
    response = ""
    for chunk in bot.chat("Write a short poem about code."):
        response += chunk
    
    if len(response) > 0:
        print("[PASS] Received response.")
    else:
        print("[FAIL] No response.")

    # Check log
    time.sleep(1) # Ensure flush
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            f.seek(start_size) # Read only new logs
            new_logs = f.read()
            
            if "poem" in new_logs and "DOCUMENT" in new_logs: 
                 print("[PASS] Log entry found with correct intent.")
            elif len(new_logs) > 0:
                 print(f"[WARN] Log found but intent check might have failed. New Logs:\n{new_logs}")
            else:
                 print(f"[FAIL] No new logs found.")
    else:
         print("[FAIL] vinni.log not created.")

if __name__ == "__main__":
    test_v01()
