import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def test_persona():
    print("--- Testing Persona Consistency (v0.2.11) ---")
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    # 1. CHAT
    print("\n1. CHAT ('Hi there')")
    for chunk in bot.chat("Hi there"):
        print(chunk, end="")
    print("\n")
    
    # 2. MATH ('What is 25 * 4?')
    print("\n2. MATH ('What is 25 * 4?')")
    for chunk in bot.chat("What is 25 * 4?"):
        print(chunk, end="")
    print("\n")
        
    # 3. ANALYSIS ('How do I treat a minor burn?')
    print("\n3. ANALYSIS ('How do I treat a minor burn?')")
    for chunk in bot.chat("How do I treat a minor burn?"):
        print(chunk, end="")
    print("\n")

if __name__ == "__main__":
    test_persona()
