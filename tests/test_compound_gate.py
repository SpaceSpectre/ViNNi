import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

class TestCompoundGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- ViNNi Compound & Gate Tests (v0.4.0) ---")
        cls.bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")

    def test_compound_interest(self):
        """Regression test for 5% 10 years hard fail."""
        q = "I invest $1000 at 5% for 10 years. How much do I have?"
        print(f"\n[Compound] {q}")
        resp = "".join(self.bot.chat(q))
        print(f"Result: {resp}")
        
        # Expected: 1628.89
        # Check for 1628 or 1,628
        self.assertTrue("1628" in resp or "1,628" in resp, "Failed Compound: Did not calculate ~1628.")
        self.assertFalse("1272" in resp, "Failed Compound: Still hallucinating 1272.")

    def test_trap_gate(self):
        """Regression test for Trap Gate (Sum 21)."""
        q = "What is the probability of drawing two cards that sum to 21 in blackjack?"
        print(f"\n[Trap] {q}")
        resp = "".join(self.bot.chat(q)).lower()
        print(f"Result: {resp}")
        
        # Now forcing Clarity via SYSTEM msg.
        # Should detect "clarification" or "ask"
        self.assertTrue("clarif" in resp or "ask" in resp, "Failed Gate: Did not ask for clarification.")

if __name__ == "__main__":
    unittest.main()
