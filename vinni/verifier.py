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
