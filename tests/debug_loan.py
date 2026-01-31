import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def debug_loan():
    print("--- Debugging Loan Calculation ---")
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    q = "I have a loan of $1500, 18.99% annual interest calculated daily. Weekly payments over 1 year. How much total interest do I pay?"
    print(f"Query: '{q}'")
    
    # Process
    try:
        resp = ""
        for chunk in bot.chat(q): resp += chunk
        print(f"\nResponse:\n{resp}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_loan()
