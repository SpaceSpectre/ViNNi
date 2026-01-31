import sys
import os
import unittest
from decimal import Decimal

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

class TestFinanceSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- ViNNi Finance Test Suite (v0.3.0 Gatekeeper) ---")
        cls.bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")

    def test_P01_blackjack(self):
        """Probability of Blackjack (2 cards). Expect ~4.83%."""
        q = "What is the probability of being dealt a blackjack in a single-deck game?"
        print(f"\n[P-01] {q}")
        resp = "".join(self.bot.chat(q))
        print(f"Result: {resp}")
        
        # Must detect ~4.8
        self.assertTrue("4.8" in resp or "0.048" in resp, "Failed P-01: Blackjack probability incorrect.")
        self.assertTrue("2 cards" in resp.lower() or "two cards" in resp.lower(), "Failed P-01: Hand size incorrect.")

    def test_L01_loan_daily(self):
        """Loan $1500, 18.99% APR, Daily Compounding. Weekly Payments."""
        # This was the failure case.
        # 18.99% / 365 = 0.052% daily.
        q = "I have a loan of $1500, 18.99% annual interest calculated daily. Weekly payments over 1 year. How much total interest do I pay?"
        print(f"\n[L-01] {q}")
        resp = "".join(self.bot.chat(q))
        print(f"Result: {resp}")
        
        # Approximate Total Interest should be ~ $150-$160 range if calculated correctly (reducing balance).
        # $1500 at 19% amortized is approx $150 interest.
        # If it says $75 (flat) -> Fail.
        # If it says >$1000 -> Fail.
        
        self.assertFalse("5.19%" in resp, "Failed L-01: Hallucinated daily rate 5.19%.")
        self.assertFalse("75.20" in resp or "75$" in resp, "Failed L-01: Used simple interest (Flat).")

    def test_A01_annuity_ordinary(self):
        """Annuity Ordinary: $500/mo, 30 years, 5%."""
        q = "Calculate total value of an ordinary annuity: $500 monthly for 30 years at 5% annual return."
        print(f"\n[A-01] {q}")
        resp = "".join(self.bot.chat(q))
        print(f"Result: {resp}")
        
        # FV = P * ((1+r)^n - 1)/r
        # r = 0.05/12, n=360
        # Expected ≈ $416,000
        
        self.assertTrue("416," in resp or "415," in resp or "417," in resp, "Failed A-01: Annuity value mismatch.")

    def test_B01_bond_par(self):
        """Bond Valuation: Coupon = YTM -> Price = Par."""
        q = "Value a bond: Face $1000, Coupon 5%, YTM 5%, 10 years."
        print(f"\n[B-01] {q}")
        resp = "".join(self.bot.chat(q))
        print(f"Result: {resp}")
        
        self.assertTrue("1000" in resp or "$1,000" in resp, "Failed B-01: Bond Par value incorrect.")

if __name__ == "__main__":
    unittest.main()
