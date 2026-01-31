import sys
import os
import ollama
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def repro():
    print("--- Repro Empty Response ---")
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    q = "What is the probability of getting heads when flipping a fair coin?"
    print(f"Query: '{q}'")
    
    print("Sending to chat...")
    resp = ""
    for chunk in bot.chat(q):
        resp += chunk
        print(f"Chunk: '{chunk}'")
        
    print(f"Final Response Length: {len(resp)}")
    print(f"Final Response: '{resp}'")
    
    # Inspect History
    print("\n--- History State ---")
    for msg in bot.history:
        print(f"Role: {msg['role']}, Content Len: {len(msg['content'])}")
        if msg['role'] == 'system':
             print(f"System Content Snippet: {msg['content'][:50]}...")

if __name__ == "__main__":
    repro()
