import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def test_finance():
    print("--- Testing Financial Reliability (v0.2.15) ---")
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    # 1. Simple Daily Rate Check
    q1 = "I have a loan with 365% annual interest compounded daily. What is my daily interest rate?"
    print(f"\n1. Query: '{q1}'")
    resp1 = ""
    for chunk in bot.chat(q1): resp1 += chunk
    
    print(f"Response:\n{resp1}\n")
    
    # Validation: 365% / 365 = 1%
    if "1%" in resp1 or "0.01" in resp1:
         print("   [PASS] Daily Rate is Correct (~1%).")
    else:
         print("   [FAIL] Daily Rate mismatch.")
         sys.exit(1)

    # 2. Assumption Header Check (Complex Query)
    q2 = "Calculate loan repayment for $1500 over a year at 18.99% interest computed daily."
    print(f"\n2. Query: '{q2}'")
    resp2 = ""
    for chunk in bot.chat(q2): resp2 += chunk
    
    print(f"Response Snippet: {resp2[:200]}...")
    
    if "ASSUMPTIONS" in resp2:
         print("   [PASS] Assumption Header Detected.")
    else:
         print("   [FAIL] Missing Assumption Disclosure.")
         sys.exit(1)
         
    # Check for the 5.19% hallucination
    if "5.19%" in resp2:
         print("   [FAIL] Old hallucination (5.19% daily) persisted.")
         sys.exit(1)
    
    # Check for correct daily rate approx (0.05%)
    if "0.05" in resp2 or "0.0005" in resp2:
         print("   [PASS] Daily Rate looks reasonable.")

if __name__ == "__main__":
    test_finance()
