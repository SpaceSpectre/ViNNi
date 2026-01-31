import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def debug_contract():
    print("--- Debugging Contract ---")
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    query = "Draft a short email"
    print(f"Query: '{query}'")
    
    response = ""
    for chunk in bot.chat(query):
        response += chunk
        
    tokens = bot.last_turn_tokens
    print(f"Response: {response}")
    print(f"Tokens: {tokens}")
    
    if tokens < 15:
        print("FAIL: < 15 tokens")
    else:
        print("PASS: >= 15 tokens")

if __name__ == "__main__":
    debug_contract()
