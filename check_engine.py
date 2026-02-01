import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vinni.math_engine import FinanceEngine

res = FinanceEngine.calculate_loan_interest(
    principal=420000,
    annual_rate=0.054,
    months=300,
    payment_freq="monthly",
    compounding_freq="semi-annually"
)
print(f"Result: {res['payment_amount']}")
expected = 2538.47
if 2530 < res['payment_amount'] < 2550:
    print("PASS")
else:
    print("FAIL")
