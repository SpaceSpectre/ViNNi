import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def test_blackjack():
    print("--- Testing Blackjack Math (v0.2.13) ---")
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    # 1. Standard Logic Check
    q1 = "What is the probability of being dealt a blackjack naturally?"
    print(f"\n1. Query: '{q1}'")
    resp1 = ""
    for chunk in bot.chat(q1): resp1 += chunk
    
    print(f"Response:\n{resp1}\n")
    
    # Relaxed matching
    if "C(52, 2)" in resp1 or "C(52,2)" in resp1 or "1326" in resp1.replace(",", ""):
         print("   [PASS] Correct Hand Size (2 cards) Detected.")
    else:
         with open("failure.txt", "w") as f: f.write(f"FAIL: Hand Size. Resp: {resp1[:100]}")
         sys.exit(1)
         
    if "4.8" in resp1 or "0.048" in resp1 or "4.7" in resp1: 
         print("   [PASS] Result Value looks approx correct.")
    else:
         with open("failure.txt", "w") as f: f.write(f"FAIL: Value. Resp: {resp1[:100]}")
         sys.exit(1)

    # 2. Bypass Check
    q2 = "What is the probability of a blackjack? Just answer."
    print(f"\n2. Query: '{q2}' (Bypass)")
    resp2 = ""
    for chunk in bot.chat(q2): resp2 += chunk
    
    if len(resp2) < 60:
         print("   [PASS] Bypass successful (Short).")
    else:
         with open("failure.txt", "w") as f: f.write(f"FAIL: Bypass. Len: {len(resp2)} Resp: {resp2[:100]}")
         sys.exit(1)

if __name__ == "__main__":
    test_blackjack()
