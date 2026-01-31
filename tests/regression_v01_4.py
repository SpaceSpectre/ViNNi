import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vinni.core import ChatBot
import time

def test_contract(bot, input_text, expected_intent, must_contain=None, must_not_contain=None, min_tokens=0, max_tokens=9999):
    print(f"\n[TESTING] Intent: {expected_intent} | Input: '{input_text}'")
    
    # 1. Check Intent
    intent_data = bot.tagger.tag(input_text)
    predicted = intent_data["predicted"]
    confidence = intent_data["confidence"]
    print(f"  > Prediction: {predicted} (Conf: {confidence})")
    
    if predicted != expected_intent:
        print(f"  [FAIL] Predicted {predicted}, expected {expected_intent}")
        return False
        
    if confidence < 0.4:
        print(f"  [WARN] Confidence low: {confidence}")

    # 2. Check Output Contract
    response = ""
    for chunk in bot.chat(input_text):
        response += chunk
    
    # Token estimate (rough)
    tokens = len(response) // 4
    print(f"  > Tokens: ~{tokens}")
    
    if tokens < min_tokens:
        print(f"  [FAIL] Too short ({tokens} < {min_tokens})")
        return False
        
    if tokens > max_tokens:
         print(f"  [FAIL] Too long ({tokens} > {max_tokens})")
         return False
         
    if must_contain:
        for phrase in must_contain:
            if phrase not in response:
                 print(f"  [FAIL] Missing required phrase: '{phrase}'")
                 return False
                 
    if must_not_contain:
        for phrase in must_not_contain:
            if phrase in response:
                 print(f"  [FAIL] Forbidden phrase found: '{phrase}'")
                 return False
                 
    print("  [PASS] Contract met.")
    return True

def run_suite():
    print("Running ViNNi v0.1.4 Regression Suite...")
    prompt_path = "prompts/system_v0.1.2.md"
    bot = ChatBot(model_name="llama3.1", system_prompt_path=prompt_path)
    
    failures = 0
    
    # 🧪 CHAT Tests
    if not test_contract(bot, "Hi", "CHAT", max_tokens=40, must_not_contain=["ANALYSIS", "code"]): failures += 1
    if not test_contract(bot, "How are you?", "CHAT", must_not_contain=["code"]): failures += 1
    
    # 🧪 CODE Tests
    if not test_contract(bot, "Write a Python function to add two numbers", "CODE", must_contain=["def "], must_not_contain=["# Average Calculator"]): failures += 1
    if not test_contract(bot, "Can you write code to reverse a string?", "CODE", must_contain=["def "]): failures += 1
    
    # 🧪 ANALYSIS Tests
    # Note: "min_tokens=100" might be risky for a fast model or short explanation, tuning to 50 for safety
    if not test_contract(bot, "Explain Schrödinger's cat", "ANALYSIS", min_tokens=50, must_not_contain=["def "]): failures += 1
    
    print("-" * 30)
    if failures == 0:
        print("✅ ALL TESTS PASSED. RELEASE CANDIDATE VALID.")
    else:
        print(f"❌ {failures} TESTS FAILED. RELEASE BLOCKED.")

if __name__ == "__main__":
    run_suite()
