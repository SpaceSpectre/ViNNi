import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

class TestBiweeklyComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- ViNNi BiWeekly Comparison Repro (v0.7.0) ---")
        cls.bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")

    def test_comparison_logic(self):
        """
        User Query: Loan $30k, 6yr, 6% Monthly Comp.
        Part d) If bi-weekly... what happens to interest?
        Expected:
        1. Correct Bi-weekly frequency (156 payments, not 78).
        2. Correct Comparison (Interest Reduces).
        """
        q = "I take out a loan of $30,000 to be repaid over 6 years. The interest rate is 6.0% per annum, compounded monthly. If instead I make bi-weekly payments (26 per year) while keeping the same interest rate, what happens to the total interest paid?"
        print(f"\n[Query] {q}")
        resp = "".join(self.bot.chat(q))
        print(f"Result: {resp}")
        
        # Check for Hallucination "13 periods"
        if "13 bi-weekly" in resp or "78 months" in resp or "78 payments" in resp:
            self.fail("Hallucinated 13 periods/year (should be 26).")
            
        # Check for Correct Direction
        if "increase" in resp.lower() and "interest" in resp.lower():
            # Allow "increase" only if it says "Does NOT increase"
            if "not increase" not in resp.lower() and "reduce" not in resp.lower():
                 self.fail("Hallucinated Interest Increase.")
        
        # Check if Context was likely used (Look for accurate numbers)
        # 30k, 6%, 6yr.
        # Monthly PMT = 514.17 approx.
        # Bi-weekly PMT = ?
        # r_eff = 1.005^(12/26)-1.
        # PMT ~= 237? 
        # Check if numbers are consistent.

if __name__ == "__main__":
    unittest.main()
