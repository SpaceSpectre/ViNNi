import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vinni.snapshot import RegressionSnapshot

print("[Checking Snapshot Save]")
path = RegressionSnapshot.save(
    question="Test",
    engine_input={},
    engine_output={"k":"v"},
    final_response="Test Resp",
    model_config={},
    assumptions=["Test"]
)
print(f"Path: {path}")
if path and os.path.exists(path):
    print("PASS")
else:
    print("FAIL")
