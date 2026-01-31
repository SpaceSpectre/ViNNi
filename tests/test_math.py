import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def test_math_reasoning():
    print("--- Testing Math Reasoning (v0.2.9) ---")
    # Using the updated system prompt (v0.2.7) which now has math rules
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    query = "What is the probability of getting a Royal Flush in a 5-card poker hand? Show reasoning."
    print(f"\nQuery: {query}")
    
    response = ""
    for chunk in bot.chat(query):
        response += chunk
        
    print(f"\nResponse:\n{response}\n")
    
    # Validation
    valid_denominators = ["2,598,960", "2598960", "C(52, 5)", "52 choose 5", "649,740", "649740"]
    
    if any(x in response for x in valid_denominators):
        print("✅ PASSED: Correct Combinatorial Logic Detected.")
    else:
        print("❌ FAILED: Could not find standard combinatorial terms (C(52,5) or 2,598,960).")
        print("   Risk: Logic might be sequential/approximate.")

if __name__ == "__main__":
    test_math_reasoning()
