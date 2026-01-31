import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def debug_math():
    print("--- Debugging Math Response ---")
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    query = "What is the probability of being dealt a blackjack naturally?"
    print(f"Query: '{query}'")
    
    response = ""
    for chunk in bot.chat(query):
        response += chunk
        
    print(f"FULL RESPONSE:\n{response}")

if __name__ == "__main__":
    debug_math()
