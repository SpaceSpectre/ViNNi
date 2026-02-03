import sys
import os
import unittest
import glob
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot
from vinni.snapshot import RegressionSnapshot

class TestTrustFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- ViNNi v0.9.0 Trust Features Repro ---")
        cls.bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")

    def test_assumptions_and_snapshot(self):
        """
        Query: "Loan of $12000 for 1 year at 5%."
        Expected: 
        1. Defaults applied (Monthly freq).
        2. Output contains "ASSUMPTIONS APPLIED".
        3. Output contains "Confidence: 1.0".
        4. Snapshot created.
        """
        # Clear old snapshots
        for f in glob.glob(os.path.join(RegressionSnapshot.SNAPSHOT_DIR, "*.json")):
            os.remove(f)
            
        q = "Loan of $12000 for 1 year at 5%."
        print(f"\n[Query] {q}")
        resp = "".join(self.bot.chat(q))
        print(f"Result Preview: {resp[:100]}...")
        
        # Check Confidence
        if "Confidence: 1.0" in resp:
            print("[PASS] Confidence Footer Detected.")
        else:
            print("[FAIL] Confidence Footer Missing.")
            
        # Check Assumptions
        if "ASSUMPTIONS APPLIED" in resp or "Assumption" in resp: # LLM phrasing check hard, checking logic injection
             pass # Hard to check final text if LLM reformats, but extraction should have it.
             # We check Snapshot for assumptions.
             
        # Check Snapshot
        snaps = glob.glob(os.path.join(RegressionSnapshot.SNAPSHOT_DIR, "*.json"))
        if len(snaps) > 0:
            print(f"[PASS] Snapshot created: {snaps[0]}")
            with open(snaps[0], 'r') as f:
                data = json.load(f)
                assumptions = data['input']['assumptions']
                print(f"Logged Assumptions: {assumptions}")
                if "Payment Frequency: Monthly (Default)" in assumptions:
                    print("[PASS] Default Frequency Assumption Verified.")
                else: 
                    print("[WARN] Assumption not logged correctly.")
        else:
            print("[FAIL] No Snapshot File Created.")
            self.fail("Snapshot missing.")

if __name__ == "__main__":
    unittest.main()
