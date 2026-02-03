import json
import os
import time
from datetime import datetime

class RegressionSnapshot:
    SNAPSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "snapshots")
    
    @classmethod
    def save(cls, question: str, engine_input: dict, engine_output: dict, final_response: str, model_config: dict, assumptions: list = None):
        """
        Saves a semantic snapshot of a math interaction for regression testing.
        """
        if not os.path.exists(cls.SNAPSHOT_DIR):
            os.makedirs(cls.SNAPSHOT_DIR)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snap_{timestamp}.json"
        filepath = os.path.join(cls.SNAPSHOT_DIR, filename)
        
        snapshot = {
            "id": f"math_turn_{timestamp}",
            "timestamp": datetime.now().isoformat(),
            "category": "Finance" if "loan" in str(engine_input) else "Math",
            "model": model_config,
            "input": {
                 "question": question,
                 "extracted_params": engine_input,
                 "assumptions": assumptions or []
            },
            "engine_result": engine_output,
            "final_response": final_response,
            "verification_guidance": "Ensure final_response matches engine_result values."
        }
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
            return filepath
        except Exception as e:
            print(f"[Snapshot Error] Could not save: {e}")
            return None
