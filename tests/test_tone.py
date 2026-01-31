import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def test_tone():
    print("--- Testing Tone (v0.2.7) ---")
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    queries = [
        "How are you?",
        "What's up?",
        "Who created you?"
    ]
    
    for q in queries:
        print(f"\nUser: {q}")
        print("ViNNi: ", end="")
        for chunk in bot.chat(q):
            print(chunk, end="")
        print()

if __name__ == "__main__":
    test_tone()
