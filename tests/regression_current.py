import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni import __version__
from vinni.monitor import IntentTagger
from vinni.core import ChatBot

def test_intent(tagger, text, expected):
    result = tagger.tag(text)
    pred = result["predicted"]
    if pred == expected:
        print(f"  ✅ '{text}' -> {pred}")
        return True
    else:
        print(f"  ❌ '{text}' -> {pred} (Expected {expected})")
        return False

def test_contract(bot, prompt, expected_tokens_min=1):
    print(f"  Testing Contract: '{prompt}'")
    response = ""
    for chunk in bot.chat(prompt):
        response += chunk
    
    tokens = bot.last_turn_tokens
    if tokens >= expected_tokens_min:
        print(f"  ✅ ({tokens} tokens)")
        return True
    else:
        print(f"  ❌ Too short: {tokens} tokens (Expected > {expected_tokens_min})")
        return False

def run_suite():
    print(f"Running ViNNi Regression Suite (Current: v{__version__})...")
    
    failures = 0
    tagger = IntentTagger()
    # Use the production prompt (v0.2.7 for Tone)
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    
    print("\n--- 1. Intent Classification ---")
    # CHAT (Tone check implicitly covered by manual test, here we check routing)
    if not test_intent(tagger, "Hi", "CHAT"): failures += 1
    if not test_intent(tagger, "Who created you?", "CHAT"): failures += 1
    
    # CODE
    if not test_intent(tagger, "Write a python script", "CODE"): failures += 1
    
    # ANALYSIS
    if not test_intent(tagger, "Explain black holes", "ANALYSIS"): failures += 1
    
    # DOCUMENT
    if not test_intent(tagger, "Draft an email to my boss", "DOCUMENT"): failures += 1
    
    print("\n--- 2. Version Check ---")
    # Dynamic check
    print(f"  Detected Package Version: {__version__}")
    
    print("\n--- 3. Contract Checks ---")
    if not test_contract(bot, "Draft a short email", expected_tokens_min=15): failures += 1
    
    print("-" * 30)
    if failures == 0:
        print(f"✅ ALL TESTS PASSED. v{__version__} READY.")
    else:
        print(f"❌ {failures} TESTS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    run_suite()
