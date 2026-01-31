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
    def log_turn(
        session_id: str,
        model: str, 
        system_prompt_version: str,
        user_input: str, 
        intent: str, 
        output: str, 
        latency_ms: float,
        input_tokens: int = 0,
        output_tokens: int = 0
    ):
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "session_id": session_id,
            "model": model,
            "system_prompt_version": system_prompt_version,
            "intent": intent,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": round(latency_ms, 2),
            # Full content logging for local debug; opaque in prod usually
            "input_snippet": user_input[:100], 
            "output_len": len(output) 
        }
        
        # Include full input/output for now as per v0.1 requirement
        entry["input"] = user_input
        entry["output"] = output
        
        logger.info(json.dumps(entry))
