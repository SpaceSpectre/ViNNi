import ollama
import json

class MathVerifier:
    def __init__(self, model_name: str = "llama3"):
        self.model_name = model_name

    def verify(self, question: str, answer: str) -> dict:
        """
        Verifies the mathematical correctness of an answer.
        Returns check status and reason.
        """
        # Triggers: Only run on math-heavy queries?
        # For v0.4.0, we call it manually or Core calls it.
        
        # v1.0 MathVerifier Rule Table
        # Returns {status, reason, rule_id, severity}
        
        lower_q = question.lower()
        lower_a = answer.lower()
        
        # --- SECTION 2: CLASSIFICATION ---
        # MV-012: Loan != Simple Interest
        if "loan" in lower_q or "mortgage" in lower_q:
            if "total interest" in lower_a and any(x in lower_a for x in ["p * r * n", "p * i * n", "p × i × n"]):
                return {"status": "FAIL", "rule_id": "MV-012", "severity": "HARD", "reason": "Used Simple Interest formula (P*r*n) for Amortized Loan."}

        # --- SECTION 3: RATE & FREQUENCY ---
        # MV-023: Bi-weekly = 26 payments
        if "bi-weekly" in lower_q or "biweekly" in lower_q:
            if "24 payments" in lower_a:
                return {"status": "FAIL", "rule_id": "MV-023", "severity": "HARD", "reason": "Bi-weekly implies 26 payments/year, not 24."}
            if "13 bi-weekly" in lower_a or "13 payments" in lower_a or "13 periods" in lower_a:
                 return {"status": "FAIL", "rule_id": "MV-023", "severity": "HARD", "reason": "Bi-weekly implies 26 payments/year, not 13 (which is 4-weekly)."}
            if "divide by 1.5" in lower_a:
                return {"status": "FAIL", "rule_id": "MV-023", "severity": "HARD", "reason": "Heuristic division (1.5) detected."}

        # --- SECTION 6: DOMINANCE ---
        # MV-050: More frequent payments -> <= Interest
        if ("bi-weekly" in lower_q or "biweekly" in lower_q) and "total interest" in lower_a:
            if ("increase" in lower_a or "higher" in lower_a) and "paid" in lower_a:
                 return {"status": "FAIL", "rule_id": "MV-050", "severity": "HARD", "reason": "Bi-weekly payments should REDUCE interest, not increase it."}

        # --- SECTION 5: INVARIANTS & EXTRACTION ---
        import re
        
        # Helper to extract money
        def extract_money(text, label):
            # Try specific label first
            m = re.findall(rf"{label}\s*[≈=:]\s*\$([\d,]+\.?\d*)", text, re.IGNORECASE)
            if m: return float(m[-1].replace(",", ""))
            return None

        # MV-040: Total Paid ~= Payment * N
        # MV-041: Interest = Total - Principal
        
        # Extract Principal from Question (Heuristic)
        principal = None
        p_match = re.search(r"\$([\d,]+\.?\d*)", question)
        if p_match:
             principal = float(p_match.group(1).replace(",", ""))

        # Extract Output Values
        # M (Payment)
        m_val = extract_money(answer, "M") or extract_money(answer, "Payment")
        # N (Count)
        n_match = re.search(r"(\d+)\s*payments", lower_a)
        n_val = float(n_match.group(1)) if n_match else None
        # Total Paid
        total_paid = extract_money(answer, "Total Amount Paid") or extract_money(answer, "Total Paid")
        # Total Interest
        total_interest = extract_money(answer, "Total Interest Paid") or extract_money(answer, "Total Interest")

        if m_val and n_val and total_paid:
             calc_total = m_val * n_val
             if abs(calc_total - total_paid) > 10.0:
                 return {"status": "FAIL", "rule_id": "MV-040", "severity": "HARD", "reason": f"Invariant Failed: Pmt({m_val}) * N({n_val}) != Total({total_paid})."}

        if total_paid and principal and total_interest:
             calc_interest = total_paid - principal
             if abs(calc_interest - total_interest) > 10.0:
                  return {"status": "FAIL", "rule_id": "MV-041", "severity": "HARD", "reason": f"Invariant Failed: Interest({total_interest}) != Total({total_paid}) - Principal({principal})."}

        # --- SECTION 7: SANITY BOUNDS ---
        # MV-060: Interest Explosion Check
        # Rule: Interest < Principal * Rate * Years * 1.5 (Rough Upper Bound for Amortization)
        # We need Rate and Years from Question.
        if principal and total_interest:
             # Extract approx rate (look for %)
             r_match = re.search(r"(\d+\.?\d*)%", question)
             y_match = re.search(r"(\d+)\s*years", lower_q)
             
             if r_match and y_match:
                  r = float(r_match.group(1)) / 100.0
                  y = float(y_match.group(1))
                  
                  # Simple Interest Cap (Amortization interest is generally < Simple Interest total)
                  # Total Interest on Loan < P * r * n (Simple) is usually true? 
                  # Actually, roughly P * r * n / 2.
                  # Safe Bound: P * r * n * 1.5 (Very generous).
                  upper_bound = principal * r * y * 1.5
                  
                  if total_interest > upper_bound:
                       return {"status": "FAIL", "rule_id": "MV-060", "severity": "HARD", "reason": f"Interest ({total_interest}) exceeds sanity bound ({upper_bound:.0f}). Hallucination likely."}

        # --- LLM FALLBACK ---
        prompt = (
            f"You are a Mathematical Validator. Your job is to check the Answer against the Question for correctness.\n"
            f"Question: {question}\n"
            f"Answer: {answer}\n\n"
            f"Requirements:\n"
            f"1. Check if the formula used is correct.\n"
            f"2. Check if assumptions are stated (e.g. Ace values, Interest frequency).\n"
            f"3. Check if the final number is directionally plausible.\n"
            f"4. Ignore minor rounding differences.\n\n"
            f"Output JSON ONLY: {{'status': 'PASS' or 'FAIL', 'reason': 'Short explanation', 'confidence': 0.0-1.0}}"
        )
        
        try:
            resp = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.0}
            )
            content = resp['message']['content']
            json_str = content.replace("```json", "").replace("```", "").strip()
            return json.loads(json_str)
        except Exception as e:
            return {"status": "ERROR", "reason": str(e), "confidence": 0.0}
        
        try:
            resp = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={"temperature": 0.0}
            )
            content = resp['message']['content']
            json_str = content.replace("```json", "").replace("```", "").strip()
            return json.loads(json_str)
        except Exception as e:
            return {"status": "ERROR", "reason": str(e), "confidence": 0.0}
