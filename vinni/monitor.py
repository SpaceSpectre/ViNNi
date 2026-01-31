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

import json
import logging
import hashlib
import time
import uuid
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
    Deterministic intent tagger with confidence scoring (v0.1.4).
    """
    def tag(self, user_input: str) -> Dict[str, Any]:
        text = user_input.lower()
        word_count = len(text.split())
        
        scores = {
            "CHAT": 0.0,
            "CODE": 0.0,
            "ANALYSIS": 0.0,
            "DOCUMENT": 0.0
        }
        
        # --- CHAT SIGNALS ---
        # Greetings & Meta
        if any(g in text for g in ["hi", "hello", "hey", "good morning", "good evening"]):
            scores["CHAT"] += 0.4
        if "how are you" in text or "how's it going" in text:
            scores["CHAT"] += 0.8
        if "who are you" in text or "who created you" in text or "what are you" in text:
            scores["CHAT"] += 0.8 # Meta is CHAT
        if "capabilities" in text or "what can you do" in text:
            scores["CHAT"] += 0.8
            
        # Short input heuristic
        if word_count < 4:
            scores["CHAT"] += 0.3
            
        # --- CODE SIGNALS ---
        # Keywords
        code_keywords = ['def ', 'class ', 'import ', 'return ', 'function', 'script', 'bug', 'error', 'api', 'json', 'variable']
        for w in code_keywords:
            if w in text:
                scores["CODE"] += 0.3
        
        # Verbs
        if any(v in text for v in ['write', 'generate', 'implement', 'debug', 'fix']):
            if "code" in text or "function" in text or "script" in text:
                scores["CODE"] += 0.5
            else:
                scores["CODE"] += 0.2
                
        # Syntax
        if "```" in text or "{" in text or "print(" in text:
            scores["CODE"] += 0.4
            
        # --- ANALYSIS SIGNALS ---
        if any(w in text for w in ['explain', 'why', 'how does', 'compare', 'difference', 'analyze']):
            scores["ANALYSIS"] += 0.4
        
        if "?" in text and word_count > 6:
            scores["ANALYSIS"] += 0.2
            
        # --- DOCUMENT SIGNALS ---
        if any(w in text for w in ['draft', 'summarize', 'poem', 'story', 'email', 'essay', 'edit', 'rewrite']):
            scores["DOCUMENT"] += 0.5

        # Normalize & Decide
        total = sum(scores.values()) or 1.0
        
        # Find max
        predicted = max(scores, key=scores.get)
        confidence = scores[predicted] / total if sum(scores.values()) > 0 else 0.0
        
        # Default fallback
        if sum(scores.values()) == 0:
            predicted = "CHAT"
            confidence = 1.0 # Default fallback
            
        return {
            "predicted": predicted,
            "confidence": round(confidence, 2),
            "alternatives": {k: round(v/total, 2) for k, v in scores.items() if total > 0}
        }

class SecurityLogger:
    """
    Handles observability and audit logging (Canonical JSONL).
    """
    @staticmethod
    def log_turn(
        session_id: str,
        request_id: str,
        model: Dict[str, Any],
        system_info: Dict[str, Any],
        user_input: str,
        input_tokens: int,
        intent_info: Dict[str, Any],
        output: str,
        output_tokens: int,
        latency_ms: float,
        flags: Dict[str, bool] = None
    ):
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "session_id": session_id,
            "request_id": request_id,
            "model": model,
            "system": system_info,
            "input": {
                "text": user_input, # v0.1 requirement: log full input (local)
                "tokens": input_tokens
            },
            "intent": intent_info,
            "output": {
               # "text": output, # Schema doesn't strictly say to log output text, but v0.1 log did. 
               # User "Canonical" schema showed just tokens/latency. 
               # I'll stick to User's Schema strictly but keep 'text' implicitly validation?
               # ACTUALLY user schema example has NO output text.
               # I will OMIT output text to be strictly schema-compliant unless debugging needs it.
               # Wait, user said "Can I reproduce it?". Logs usually need input... and output is helpful.
               # User schema had: "tokens": 259, "latency_ms": 412.
               # I'll follow that structure.
               "tokens": output_tokens,
               "latency_ms": round(latency_ms, 2)
            },
            "flags": flags or {
                "asked_clarification": False,
                "refusal": False,
                "static_response": False
            }
        }
        
        logger.info(json.dumps(entry))
