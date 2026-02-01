import sys
import os
import unittest
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot
from vinni.math_engine import FinanceEngine

class TestCanadianMortgage(unittest.TestCase):
    def test_engine_math_exact(self):
        """
        Verify math_engine.py logic for Canadian Mortgage.
        P = 420,000
        Rate = 5.4% (0.054)
        Compounding = Semi-Annually (2)
        Payment = Monthly (12)
        Years = 25
        
        Expected:
        r_eff = (1 + 0.054/2)^(2/12) - 1
              = (1.027)^(1/6) - 1
              = 1.00445037 - 1 = 0.00445037...
        n = 300
        PMT = 420000 * r / (1 - (1+r)^-300)
        
        Calculation:
        PMT approx $2,538.47
        """
        print("\n--- Testing Engine Math Directly ---")
        res = FinanceEngine.calculate_loan_interest(
            principal=420000,
            annual_rate=0.054,
            months=300,
            payment_freq="monthly",
            compounding_freq="semi-annually"
        )
        print(f"Engine Result: {res}")
        pmt = res['payment_amount']
        
        # Check against expected range
        self.assertTrue(2530 < pmt < 2550, f"Payment {pmt} out of expected range ($2538.47)")

    def test_chatbot_integration(self):
        """
        Verify ChatBot uses the engine result.
        """
        print("\n--- Testing ChatBot Integration ---")
        bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
        q = "I take out a mortgage of $420,000 amortized over 25 years at an interest rate of 5.4% per annum compounded semi-annually (Canadian convention). What is my monthly payment?"
        resp = "".join(bot.chat(q))
        print(f"Bot Response: {resp}")
        
        # Check if the response contains the correct value ~2538
        # (Allowing formatting like $2,538)
        if "2,538" in resp or "2538" in resp:
            print("[PASS] Bot used correct value.")
        else:
            print("[FAIL] Bot output did not match Engine. Likely Hallucination.")
            # We don't fail the test here to allow analysis of the output, 
            # but in strict mode we would.
            self.fail("Bot Hallucinated wrong payment.")

if __name__ == "__main__":
    unittest.main()
