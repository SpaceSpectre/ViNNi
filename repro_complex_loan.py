import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

class TestComplexLoan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- ViNNi Complex Loan Repro (v0.5.0) ---")
        cls.bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")

    def test_semi_annual_biweekly(self):
        """
        User Query: $48k, 10 years, 5.4% compounded semi-annually, monthly payments.
        Correct Monthly: ~$493.49?
        User provided check:
        r_monthly = (1 + 0.054/2)^(2/12) - 1 = (1.027)^(1/6) - 1 ≈ 0.00445
        N = 120.
        PMT = 48000 * 0.00445...
        Wait, user said User Result for Monthly was $493.49 (from ViNNi).
        User said "Monthly case... PMT = P * r / ..."
        
        Using correct math:
        r = 0.00445037
        PMT = 48000 * r / (1 - (1+r)^-120)
        PMT ≈ 518.something?
        ViNNi said 493.49? That was based on 0.0135 rate (Wrong).
        
        Bi-weekly check:
        Input: "I instead make bi-weekly payments..."
        ViNNi said: Divide by 1.5 -> $329. Wrong.
        Correct: Payments/year = 26.
        """
        q1 = "I take out a loan of $48,000 to be repaid over 10 years with monthly payments. The interest rate is 5.4% per annum, compounded semi-annually. What will my monthly payment be?"
        print(f"\n[Query 1] {q1}")
        resp1 = "".join(self.bot.chat(q1))
        print(f"Result 1: {resp1}")
        
        # Check for simple interest hallmark
        if "Total Interest = P * i * n" in resp1 or "Total Interest = P * r * n" in resp1:
            print("[FAIL] Detected Simple Interest Formula usage!")
            self.fail("Used Simple Interest for Amortization")
            
        print("-" * 30)
        
        q2 = "If I instead make bi-weekly payments, how does this change the total interest paid?"
        print(f"\n[Query 2] {q2}")
        resp2 = "".join(self.bot.chat(q2))
        print(f"Result 2: {resp2}")
        
        # Check for bi-weekly hallmarks
        if "24 payments" in resp2:
            print("[FAIL] Detected 24 payments assumption for bi-weekly!")
            self.fail("Used 24 payments/year for bi-weekly")
            
        if "divide by 1.5" in resp2:
            print("[FAIL] Detected heuristic division!")
            self.fail("Used heuristic division")

if __name__ == "__main__":
    unittest.main()
