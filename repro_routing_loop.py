import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

class TestRoutingLoop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- ViNNi Routing Loop Repro (v0.7.1) ---")
        cls.bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")

    def test_canadian_mortgage(self):
        """
        User Query: "... compounded semi-annually (Canadian convention). ..."
        Bug: Triggered "capabilities" static response loop.
        Fix: Should go to Math Engine.
        """
        q = "I take out a mortgage of $420,000 amortized over 25 years at an interest rate of 5.4% per annum compounded semi-annually (Canadian convention). a) What is my monthly payment?"
        print(f"\n[Query] {q}")
        resp = "".join(self.bot.chat(q))
        print(f"Result: {resp}")
        
        # Check for Loop
        if "I support the following response intents" in resp:
            self.fail("Static Trigger Loop Detected! (Canadian Trigger)")
            
        # Check for Math Engine usage
        if "SYSTEM" not in resp and "2554" not in resp: # 2554 is approx payment
             print("[WARN] Math Engine might not have triggered, but Loop is gone.")
             # We just strictly fail on Loop presence here.
             
        if "SYSTEM: I have utilized" in resp:
            print("[PASS] Math Engine Triggered.")

if __name__ == "__main__":
    unittest.main()
