import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def repro_coin():
    print("--- Repro Coin Flip Collision ---")
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    q = "What is the probability of getting heads when flipping a fair coin?"
    print(f"Query: '{q}'")
    
    resp = ""
    for chunk in bot.chat(q):
        resp += chunk
        
    print(f"Response: '{resp}'")
    
    if "4.8" in resp or "1326" in resp:
         print("   [FAIL] Coin Flip triggered Blackjack Math!")
    else:
         print("   [PASS] Coin Flip unaffected.")

if __name__ == "__main__":
    repro_coin()
