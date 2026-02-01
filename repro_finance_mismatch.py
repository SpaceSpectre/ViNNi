import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

class TestFinanceMismatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- ViNNi Finance Mismatch Repro (v0.4.2) ---")
        cls.bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")

    def test_loan_annual_biweekly(self):
        """
        User Query: $35000, 7 years, 6.99% compounded annually, biweekly payments.
        Expected: ~$273.60
        Current (Bug): ~$263.04
        """
        q = "Lets say I take a loan of $35000 which I would pay over a period of 7 years on a biweekly basis, the rate of interest is 6.99%, calculated annually. What is my biweekly payment?"
        print(f"\n[Query] {q}")
        resp = "".join(self.bot.chat(q))
        print(f"Result: {resp}")
        
        # Check for correct value
        # Allow small range 273.00 - 274.00
        has_correct = "273" in resp
        has_wrong = "263" in resp
        
        if has_wrong:
            print("[FAIL] Returned inaccurate value (~263).")
        
        with open("last_run.log", "w", encoding="utf-8") as f:
            f.write(resp)

        self.assertTrue(has_correct, "Failed: Did not return ~273.60")
        self.assertFalse(has_wrong, "Failed: Returned bugged value 263.")

if __name__ == "__main__":
    unittest.main()
