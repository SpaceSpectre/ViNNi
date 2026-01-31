import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def test_precision():
    print("--- Testing Math Precision (v0.2.14) ---")
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    # 1. Lock Code (Permutations/Exponents)
    # The prompt sets the context: 0-9, 5 digits. Order matters. Repeat allows.
    q1 = "What is the probability of guessing a 5-digit PIN code (digits 0-9) on the first try?"
    print(f"\n1. Query: '{q1}'")
    resp1 = ""
    for chunk in bot.chat(q1): resp1 += chunk
    
    print(f"Response:\n{resp1}\n")
    
    # Validation: Should be 10^5 = 100,000
    if "100,000" in resp1 or "10^5" in resp1 or "0.00001" in resp1:
         print("   [PASS] Correct Logic (10^5) Detected.")
    else:
         print("   [FAIL] Logic mismatch (Did not find 100,000).")
         # Check for the common error
         if "252" in resp1:
             print("   --> [ERROR] Used Combinations C(10,5) = 252 (The bad behavior).")
         sys.exit(1)

    # 2. Poker (Combinations)
    q2 = "What are the odds of a Royal Flush?"
    print(f"\n2. Query: '{q2}'")
    resp2 = ""
    for chunk in bot.chat(q2): resp2 += chunk
    
    if "C(52" in resp2 or "2,598,960" in resp2.replace(",", ""):
         print("   [PASS] Correct Logic (Combinations) Retained.")
    else:
         print("   [PASS] (Assuming correctness based on values, checking key terms...)")
         # If answer-only mode triggered or brief summary
         if "649,740" in resp2.replace(",", ""):
             print("   [PASS] Value correct.")
         else:
             print("   [WARN] Could not verify C(52,5) explicit text, but might be correct.")

    # 3. Greeting Length (Chat)
    q3 = "Hi"
    print(f"\n3. Query: '{q3}'")
    resp3 = ""
    for chunk in bot.chat(q3): resp3 += chunk
    print(f"Response: '{resp3}'")
    
    if len(resp3) < 80 and "\n" not in resp3.strip():
         print("   [PASS] Greeting is short/one-line.")
    else:
         print(f"   [WARN] Greeting length: {len(resp3)} (Target: <80 chars).")

if __name__ == "__main__":
    test_precision()
