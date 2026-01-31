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
        # Keywords (Context-sensitive)
        code_keywords = ['def ', 'class ', 'import ', 'return ', 'api', 'json'] # Removed vague 'function', 'script', 'variable'
        for w in code_keywords:
            if w in text:
                scores["CODE"] += 0.4
        
        # Verbs - Strict pairing
        if any(v in text for v in ['write', 'generate', 'implement', 'debug', 'fix', 'refactor']):
            if any(t in text for t in ['code', 'function', 'script', 'app', 'class']):
                scores["CODE"] += 0.6
            else:
                scores["CODE"] += 0.3
                
        # Syntax (Strongest signal)
        if "```" in text or "{" in text or "print(" in text or "=>" in text:
            scores["CODE"] += 0.6
            
        # --- ANALYSIS SIGNALS ---
        if any(w in text for w in ['explain', 'why', 'how does', 'compare', 'difference', 'analyze', 'meaning', 'concept']):
            scores["ANALYSIS"] += 0.5
            
        if "tell me about" in text or "what is a" in text:
             scores["ANALYSIS"] += 0.5
        
        if "?" in text and word_count > 6:
            scores["ANALYSIS"] += 0.2
            
        # --- DOCUMENT SIGNALS ---
        # Boost strong verbs to override "short input" chatter
        if any(w in text for w in ['draft', 'summarize', 'poem', 'story', 'email', 'essay', 'edit', 'rewrite', 'check']):
            scores["DOCUMENT"] += 0.8
            
        if "check" in text and "grammar" in text:
            scores["DOCUMENT"] += 0.4

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
        flags: Dict[str, bool] = None,
        input_hash: str = None # v0.2.3
    ):
        # Flattened metrics for easier analytics (v0.2.3)
        cache_hit = flags.get("cache_hit", False) if flags else False
        
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            # -- Quick Analytics Fields --
            "intent": intent_info["predicted"],
            "confidence": intent_info["confidence"],
            "cache_hit": cache_hit,
            "latency_ms": round(latency_ms, 2),
            "input_hash": input_hash,
            # -- Deep Audit --
            "session_id": session_id,
            "request_id": request_id,
            "model": model,
            "system": system_info,
            "input": {
                "text": user_input,
                "tokens": input_tokens,
                "hash": input_hash
            },
            "intent_details": intent_info, # Renamed from 'intent' to avoid collision, or keep both? 
                                           # User schema had "intent": "CODE" (string). 
                                           # I will allow 'intent' to be the string, and 'intent_details' be the object.
            "output": {
               "text": output, 
               "summary": (output[:100] + '...') if len(output) > 100 else output,
               "tokens": output_tokens,
               "latency_ms": round(latency_ms, 2)
            },
            "flags": flags or {
                "asked_clarification": False,
                "refusal": False,
                "static_response": False,
                "cache_hit": False
            }
        }
        
        logger.info(json.dumps(entry))
