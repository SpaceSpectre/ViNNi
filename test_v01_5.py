from vinni.core import ChatBot
from vinni.monitor import IntentTagger
from vinni import __version__
import os

def test_v01_5():
    print(f"Testing ViNNi v{__version__} Polish...")
    
    # 1. Version Check
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.1.2.md")
    print(f"Prompt Version Injected: {bot.prompt_version}")
    
    if bot.prompt_version == f"v{__version__}":
        print("[PASS] Version Match.")
    else:
        print(f"[FAIL] Version Mismatch: {bot.prompt_version} != v{__version__}")
        
    # 2. Intent Refinement
    tagger = IntentTagger()
    cases = [
        ("Tell me about functions", "ANALYSIS"),
        ("Write a function", "CODE"),
        ("What is a variable?", "ANALYSIS"),
        ("def foo():", "CODE")
    ]
    
    print("\n--- Intent Tuning ---")
    for text, expected in cases:
        res = tagger.tag(text)
        pred = res["predicted"]
        conf = res["confidence"]
        print(f"'{text}' -> {pred} ({conf})")
        if pred == expected:
            print("  [PASS]")
        else:
            print(f"  [FAIL] Expected {expected}")
            
    # 3. Confidence Check (manual simulation)
    low_conf_text = "functions" # Ambiguous
    res = tagger.tag(low_conf_text)
    print(f"\nAmbiguous '{low_conf_text}' -> {res['predicted']} ({res['confidence']})")
    if res['confidence'] < 0.6:
        print("[PASS] Low confidence detected.")
    else:
        print("[WARN] Confidence might be too high for ambiguity.")

if __name__ == "__main__":
    test_v01_5()
