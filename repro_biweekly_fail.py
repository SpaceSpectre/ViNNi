import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot
from vinni.verifier import MathVerifier

class TestBiweekly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- ViNNi BiWeekly Repro (v0.5.1) ---")
        cls.bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
        cls.verifier = MathVerifier()

    def test_biweekly_scenario(self):
        """
        User Query: d) If instead I make bi-weekly payments... how does total interest change?
        Hallucination: "Increases total interest".
        Target: Verifier should FLAG this as FAIL.
        """
        # Simulated Hallucinated Response (from User Log)
        bad_response = """
        d) Bi-weekly payments (26 per year):
        M = $302.91
        Total Amount Paid ≈ M * n ≈ $39,175.80
        Total Interest ≈ $16,675.80
        Comparing the results, making bi-weekly payments increases the total interest paid.
        """
        
        q = "If instead I make bi-weekly payments (26 per year) while keeping the same interest rate, how does the total interest paid change?"
        
        print(f"\n[Response Checked]\n{bad_response}")
        
        # Verify
        result = self.verifier.verify(q, bad_response)
        print(f"\n[Verifier Result] {result}")
        
        # We EXPECT "FAIL" status because logic is flawed.
        # Currently (before fix), it might PASS (if it implies logic is fine).
        # We want it to FAIL.
        
        if result["status"] == "PASS":
            print("[FAIL] Verifier passed a hallucinated response!")
            self.fail("Verifier failed to catch Interest Increase fallacy")
        else:
            print("[PASS] Verifier correctly flagged the error.")

if __name__ == "__main__":
    unittest.main()
