import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

class TestMathRefinement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- ViNNi Math Refinement Tests (v0.3.2) ---")
        # Reuse existing prompt path
        cls.bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")

    def test_A_single_die(self):
        """Probability of rolling a 6 on a fair die. Expected: 1/6, NO 'Combinations'."""
        q = "What is the probability of rolling a 6 on a fair die?"
        print(f"\n[Test A] {q}")
        resp = "".join(self.bot.chat(q)).lower()
        print(f"Result: {resp}")
        
        self.assertTrue("1/6" in resp or "16.6" in resp, "Failed Value: Expected ~16.6%")
        self.assertFalse("combination" in resp, "Failed Reasoning: Used 'Combinations' for simple die roll.")
        self.assertFalse("permutation" in resp, "Failed Reasoning: Used 'Permutations' for simple die roll.")

    def test_B_dice_sum_7(self):
        """Rolling two dice, sum 7. Expected: 6/36."""
        q = "What is the probability of rolling two dice and getting a sum of 7?"
        print(f"\n[Test B] {q}")
        resp = "".join(self.bot.chat(q)).lower()
        print(f"Result: {resp}")
        
        # 6 outcomes: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1)
        self.assertTrue("6/36" in resp or "1/6" in resp or "16.6" in resp, "Failed Value: Expected 6/36.")
        # Check for enumeration patterns like (1,6) or (2,5) or "6 outcomes"
        is_enumerated = any(p in resp for p in ["(1,6)", "(1, 6)", "(6,1)", "6 outcomes", "6 ways", "six outcomes", "six ways"])
        self.assertTrue(is_enumerated, "Failed Reasoning: Did not enumerate outcomes.")

    def test_C_trap_blackjack_sum(self):
        """Trap: Two cards sum to 21. Expected: Clarification (Values?)."""
        q = "What is the probability of drawing two cards that sum to 21 in blackjack?"
        print(f"\n[Test C] {q}")
        resp = "".join(self.bot.chat(q)).lower()
        print(f"Result: {resp}")
        
        # Should NOT just give a number without context. 
        # Ideally asks if Ace=11, Face=10.
        # But commonly, blackjack assumes Ace=11/1. 
        # The user's prompt says "Expected: Ask clarifying question".
        
        # If it calculated 4.8% (Blackjack Natural), that's technically a valid interpretation, 
        # BUT the user wants it to trigger an ambiguity check OR explicitly state assumptions.
        # Let's check if it blindly guessed or provided context.
        # Actually user said "Auto-fail if it guesses."
        
        is_clarification = "?" in resp or "depend" in resp or "clarif" in resp or "assum" in resp
        self.assertTrue(is_clarification, "Failed Trap: Did not ask for clarification or state assumptions clearly.")

if __name__ == "__main__":
    unittest.main()
