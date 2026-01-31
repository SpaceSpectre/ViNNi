import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vinni.core import ChatBot
from vinni.monitor import IntentTagger
from vinni import __version__

def test_intent(tagger, text, expected, min_conf=0.5):
    res = tagger.tag(text)
    pred = res["predicted"]
    conf = res["confidence"]
    print(f"'{text}' -> {pred} ({conf})")
    
    if pred != expected:
        print(f"  ❌ FAIL: Expected {expected}")
        return False
    if conf < min_conf:
        print(f"  ⚠️ WARN: Low confidence ({conf})")
        return True # Soft pass
    return True

def test_contract(bot, input_text, expected_tokens_min=10):
    print(f"\nGenerative Check: '{input_text}'")
    response = ""
    for chunk in bot.chat(input_text):
        response += chunk
    
    tokens = len(response) // 4
    print(f"  Length: {tokens} tokens")
    if tokens < expected_tokens_min:
        print(f"  ❌ FAIL: Response too short")
        return False
    return True

def run_suite():
    print(f"Running ViNNi v{__version__} Regression Suite (v0.2.0)...")
    
    failures = 0
    tagger = IntentTagger()
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.1.2.md") # Using locked prompt
    
    print("\n--- 1. Intent Classification ---")
    # CHAT
    if not test_intent(tagger, "Hi", "CHAT"): failures += 1
    if not test_intent(tagger, "Who created you?", "CHAT"): failures += 1
    
    # CODE
    if not test_intent(tagger, "Write a python script", "CODE"): failures += 1
    if not test_intent(tagger, "def add(a,b):", "CODE"): failures += 1
    
    # ANALYSIS
    if not test_intent(tagger, "Explain black holes", "ANALYSIS"): failures += 1
    if not test_intent(tagger, "Tell me about functions", "ANALYSIS"): failures += 1
    
    # DOCUMENT (New in v0.2.0)
    if not test_intent(tagger, "Draft an email to my boss", "DOCUMENT"): failures += 1
    if not test_intent(tagger, "Summarize this story", "DOCUMENT"): failures += 1
    
    print("\n--- 2. Command Check (Static) ---")
    if __version__ == "0.2.0":
        print("  ✅ Version is 0.2.0")
    else:
        print(f"  ❌ Version Match Failed: {__version__}")
        failures += 1

    print("\n--- 3. Contract Checks (Sample) ---")
    if not test_contract(bot, "Draft a short email", expected_tokens_min=15): failures += 1
    
    print("-" * 30)
    if failures == 0:
        print("✅ ALL TESTS PASSED. v0.2.0 READY.")
    else:
        print(f"❌ {failures} TESTS FAILED.")

if __name__ == "__main__":
    run_suite()
