import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

class TestFinanceTrigger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- ViNNi Trigger Repro (v0.4.1) ---")
        cls.bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")

    def test_investment_bypass(self):
        """Query with no explicit 'interest' or 'calculate' keyword."""
        q = "$1,000 invested at 5% per annum, compounded annually, for 10 years."
        print(f"\n[Query] {q}")
        resp = "".join(self.bot.chat(q))
        print(f"Result: {resp}")
        
        # Check for Engine Injection
        has_engine = "Deterministic Math Engine" in resp
        print(f"Engine Triggered: {has_engine}")
        
        # Check for correct maths (1628)
        has_correct_value = "1628" in resp or "1,628" in resp
        
        if not has_engine:
            print("[FAIL] Engine NOT triggered. Trigger list needs update.")
        else:
            print("[PASS] Engine triggered.")
            
        if has_correct_value:
             print("[PASS] Value Correct.")
        else:
             print("[FAIL] Value Incorrect (Hallucination).")

        # For the test to pass after fix:
        self.assertTrue(has_engine, "Engine did not trigger.")
        self.assertTrue(has_correct_value, "Math value incorrect.")

if __name__ == "__main__":
    unittest.main()
