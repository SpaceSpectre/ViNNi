import json
import logging
import hashlib
import time
from typing import Dict, Any

# Configure structured logger
logger = logging.getLogger("vinni_audit")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
file_handler = logging.FileHandler('vinni.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class IntentTagger:
    """
    Minimal deterministic intent tagger for v0.1.
    """
    def tag(self, user_input: str) -> str:
        text = user_input.lower()
        
        # Simple heuristics for zero-latency tagging
        
        # CODE: prioritize structural keywords
        if any(w in text for w in ['def ', 'class ', 'import ', 'print(', 'return ', 'code', 'function', 'bug', 'error', 'script']):
            return "CODE"
            
        # ANALYSIS: stricter check to avoid "how are you"
        # "how to" triggers analysis, "how are" triggers chat
        if "how are you" in text or "how's it going" in text:
            return "CHAT"
            
        if any(w in text for w in ['why', 'explain', 'analyze', 'what is', 'compare', 'difference']):
            return "ANALYSIS"
        if "how" in text and "how are" not in text: # rudimentary check for "how do I..."
             return "ANALYSIS"
             
        # DOCUMENT: creation/editing
        if any(w in text for w in ['write', 'draft', 'edit', 'summarize', 'poem', 'story', 'email']):
            return "DOCUMENT"
        
        return "CHAT"

class SecurityLogger:
    """
    Handles observability and audit logging.
    """
    @staticmethod
    def log_turn(model: str, system_prompt: str, user_input: str, intent: str, output: str, latency_ms: float):
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model": model,
            "prompt_hash": hashlib.sha256(system_prompt.encode()).hexdigest() if system_prompt else "none",
            "input_len": len(user_input),
            "intent": intent,
            "latency_ms": round(latency_ms, 2),
            "output_len": len(output)
        }
        # We log the metadata, avoiding logging full PII content in the structured log for now 
        # (or typically you might log content if this is a local opaque system).
        # For v0.1 we will log the full input/output for debugging as it's local.
        entry["input"] = user_input
        entry["output"] = output
        
        logger.info(json.dumps(entry))
