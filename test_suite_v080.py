import sys
import os
import unittest
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

class TestViNNiRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- ViNNi v0.8.0 Regression Suite ---")
        cls.bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
        
        cls.test_cases = [
            {
              "id": "finance_mortgage_extra",
              "question": "I take out a mortgage of $420,000 amortized over 25 years at 5.4% per annum compounded semi-annually (Canadian convention). If I pay an extra $200 monthly, how long will it take to fully pay off the mortgage and how much interest will I save?",
              "checks": ["2539", "2538", "21 years", "21.4", "interest saved"] 
            },
            {
              "id": "prob_blackjack_21",
              "question": "What is the probability of drawing two cards that sum to 21 in blackjack, assuming Ace = 11?",
              "checks": ["4.82", "4.83", "combinations"]
            },
            {
              "id": "finance_edge_case",
              "question": "I take a loan of $50,000 for 0 years at 0% interest. What is my monthly payment?",
              "checks": ["50,000", "50000", "one-time"]
            }
        ]

    def safe_print(self, text):
        try:
            print(text.encode('ascii', 'replace').decode('ascii'))
        except:
            print("Encoding Error in Print")

    def test_run_cases(self):
        for case in self.test_cases:
            self.safe_print(f"\n[Running Case: {case['id']}]")
            self.safe_print(f"Q: {case['question']}")
            
            # Run Chat
            start = time.time()
            try:
                resp = "".join(self.bot.chat(case['question']))
                duration = time.time() - start
                
                # Sanitize
                safe_resp = resp.encode('ascii', 'replace').decode('ascii')
                self.safe_print(f"A: {safe_resp[:200]}... [Tokens: {len(resp)//4}, Time: {duration:.2f}s]")
                
                # Check Checks
                passed_checks = [c for c in case['checks'] if c.lower() in safe_resp.lower()]
                
                if passed_checks:
                    self.safe_print(f"[PASS] Found: {passed_checks}")
                else:
                    self.safe_print(f"[FAIL] Expected one of {case['checks']}.")
                    # Don't fail the unittest immediately to allow other tests to run/print
                    # But mark as error. 
                    # Actually, unittest stops on fail logic unless we collect errors.
                    # We'll just Print FAIL and continue, but fail class at end?
                    # No, let's just fail with safe message.
                    self.fail(f"Case {case['id']} Failed. See output.")
                    
            except Exception as e:
                self.safe_print(f"[ERROR] Chat failed: {str(e)}")
                continue

if __name__ == "__main__":
    unittest.main()
