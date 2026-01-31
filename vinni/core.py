import ollama
import time
import os
from typing import List, Dict, Generator
from vinni.monitor import IntentTagger, SecurityLogger
from vinni.math_engine import FinanceEngine, ProbabilityEngine
import json
import re

import hashlib
import uuid
import os

class ChatBot:
    def __init__(self, model_name: str = "llama3", options: Dict = None, system_prompt_path: str = None):
        self.model_name = model_name
        self.options = options or {}
        self.history: List[Dict[str, str]] = []
        self.tagger = IntentTagger()
        self.system_prompt_content = ""
        self.session_id = str(uuid.uuid4())[:8]
        self.prompt_version = "unknown"
        self.prompt_hash = "none"
        self.last_turn_tokens = 0
        self.caches = {
            "CHAT": {},
            "CODE": {},
            "ANALYSIS": {},
            "DOCUMENT": {}
        }
        self.cache_limits = {
            "CHAT": 100,      # High freq, small
            "CODE": 50,       # Med freq
            "ANALYSIS": 20,   # Low freq, Large content
            "DOCUMENT": 20
        }
        
        self.tone = "adaptive" # v0.2.8
        self.TONE_PROMPTS = {
            "casual": "TONE OVERRIDE: Adopt a casual, friendly persona. Use humor where appropriate. Keep responses short and chatty.",
            "professional": "TONE OVERRIDE: Adopt a strictly professional, academic persona. Be detailed, structured, and objective. No humor.",
            "executive": "TONE OVERRIDE: Adopt an executive summary style. Use bullet points. Be extremely concise. BLUF (Bottom Line Up Front).",
            "adaptive": "" # Default behavior
        }
        
        self.base_system_prompt = ""
        if system_prompt_path and os.path.exists(system_prompt_path):
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                self.base_system_prompt = f.read()
                
                # Dynamic Version Injection (v0.1.5)
                from vinni import __version__
                self.prompt_version = f"v{__version__}"
                
                # Replace any hardcoded version
                if "Version: ViNNi" in self.base_system_prompt:
                    import re
                    self.base_system_prompt = re.sub(r"Version: ViNNi v\d+\.\d+\.\d+", f"Version: ViNNi {self.prompt_version}", self.base_system_prompt)
        
        self.update_system_prompt()

    def set_tone(self, tone: str):
        if tone.lower() in self.TONE_PROMPTS:
            self.tone = tone.lower()
            self.update_system_prompt()
            return True
        return False

    def update_system_prompt(self):
        tone_instruction = self.TONE_PROMPTS.get(self.tone, "")
        full_prompt = self.base_system_prompt
        
        if tone_instruction:
            full_prompt += f"\n\n{tone_instruction}"
            
        self.system_prompt_content = full_prompt
        # Reset history[0] to new prompt
        if self.history and self.history[0]["role"] == "system":
            self.history[0]["content"] = self.system_prompt_content
        else:
            self.history.insert(0, {'role': 'system', 'content': self.system_prompt_content})
            
        # Re-hash for cache invalidation (Auto-handles v0.2.5 requirement)
        self.prompt_hash = hashlib.sha256(self.system_prompt_content.encode()).hexdigest()[:8]

    def _process_math_request(self, user_input: str, intent: str) -> str:
        """
        v0.3.0: Deterministic Math Engine.
        Returns a context string if math detected, else None.
        """
        # 1. Trigger Check
        triggers = ["loan", "interest", "annuity", "bond", "mortgage", "blackjack", "poker", "odds", "probability", "calculate"]
        if intent not in ["ANALYSIS"] and not any(t in user_input.lower() for t in triggers):
            return None
        
        # 2. Extraction Prompt
        extraction_prompt = (
            "Extract mathematical variables from the user query into a valid JSON object. "
            "Supported keys: 'type' (loan, annuity, bond, probability_blackjack, probability_generic), 'principal', 'rate_annual', 'years', 'payment_freq', 'face_value', 'coupon_rate', 'ytm', 'hand_size', 'payment_amount'. "
            "Convert percentages to decimals (e.g. 18.99% -> 0.1899). "
            "Output JSON ONLY. No markdown."
        )
        
        try:
            # Single-shot extraction
            resp = ollama.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': extraction_prompt},
                    {'role': 'user', 'content': user_input}
                ],
                options={"temperature": 0.0} # Deterministic extraction
            )
            content = resp['message']['content']
            # Clean json
            json_str = content.replace("```json", "").replace("```", "").strip()
            data = json.loads(json_str)
            
            # Strict Routing (v0.3.1)
            # If the extracted type isn't explicitly supported, RETURN NONE.
            # This prevents generic "probability" queries (Coin Flip) from triggering Blackjack logic.
            supported_types = ["loan", "annuity", "bond", "probability_blackjack"] 
            # Note: prompts might return "blackjack" or "cards" based on prompt keywords, need to handle carefully.
            
            extracted_type = data.get("type", "unknown").lower()
            
            # Map aliases to canonical types if needed, or just check inclusion
            # The extraction prompt asks for: 'loan', 'annuity', 'bond', 'probability_blackjack'
            
            result = None
            
            if "loan" in extracted_type:
                # Default daily/weekly logic mapping
                freq = data.get("payment_freq", "monthly")
                result = FinanceEngine.calculate_loan_interest(
                    principal=float(data.get("principal", 0)),
                    annual_rate=float(data.get("rate_annual", 0)),
                    months=int(data.get("years", 1)) * 12, # approx
                    payment_freq=freq
                )
            elif "annuity" in extracted_type:
                 # Check 'due' or 'ordinary'
                 atype = "ordinary"
                 if "beginning" in user_input.lower(): atype = "due"
                 result = FinanceEngine.calculate_annuity(
                     payment=float(data.get("payment_amount", data.get("principal", 0))),
                     rate=float(data.get("rate_annual", 0)),
                     years=int(data.get("years", 0)),
                     type=atype
                 )
            elif "bond" in extracted_type:
                 result = FinanceEngine.calculate_bond(
                     face=float(data.get("face_value", 1000)),
                     coupon_rate=float(data.get("coupon_rate", 0)),
                     ytm=float(data.get("ytm", 0)),
                     years=int(data.get("years", 0))
                 )
            elif "blackjack" in extracted_type or ("probability" in extracted_type and "blackjack" in extracted_type):
                 # STRICT: Only trigger if "blackjack" is explicitly in the type string
                 # The previous logic "or 'cards' in ptype" was too loose if prompt returned "probability_cards"
                 result = ProbabilityEngine.solve_blackjack_probability()
            else:
                 # Generic probability or unknown type -> Bypass Engine
                 return None
            
            if result:
                return (
                    f"SYSTEM: I have utilized the Deterministic Math Engine to calculate the precise values.\n"
                    f"VERIFIED RESULT JSON: {json.dumps(result, indent=2)}\n"
                    f"INSTRUCTION: You MUST use these exact numbers in your response. Do not re-calculate. "
                    f"Present the solution using these values."
                )
                
        except Exception as e:
            # Fallback (Silent fail, let LLM handle it normally)
            return None
            
        return None

    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def chat(self, user_input: str) -> Generator[str, None, None]:
        """
        Sends a message to the Ollama model and yields chunks of the response.
        """
        start_time = time.time()
        request_id = f"req-{uuid.uuid4().hex[:5]}"
        self.last_turn_tokens = 0
        input_tokens = self._estimate_tokens(user_input)
        
        # 0. Hash Input (v0.2.3)
        input_hash = hashlib.md5(user_input.encode()).hexdigest()

        # 1. Intent Tagging (v0.1.4: Returns Dict)
        intent_info = self.tagger.tag(user_input)
        
        self.history.append({'role': 'user', 'content': user_input})
        
        # 2. Static Response Intercepts
        normalized_input = user_input.lower()
        static_response = None
        is_static = False
        
        if "capabilities" in normalized_input or ("what" in normalized_input and "do" in normalized_input and "can" in normalized_input):
            static_response = (
                "I support the following response intents:\n"
                "- CHAT: General conversation, greetings, and simple explanations.\n"
                "- CODE: Writing or explaining code snippets.\n"
                "- ANALYSIS: Structured explanations of concepts and reasoning.\n"
                "- DOCUMENT: Editing, drafting, or improving written text."
            )
            is_static = True
        elif "who created you" in normalized_input or "who initialized you" in normalized_input:
             static_response = "I am ViNNi, a locally run AI system initialized by Abhishek Arora."
             is_static = True

        if static_response:
            self.history.append({'role': 'assistant', 'content': static_response})
            yield static_response
            
            output_tokens = self._estimate_tokens(static_response)
            self.last_turn_tokens = output_tokens
            latency = (time.time() - start_time) * 1000
            
            SecurityLogger.log_turn(
                session_id=self.session_id,
                request_id=request_id,
                model={"name": "static", "quant": "N/A"},
                system_info={"name": "ViNNi", "version": self.prompt_version, "system_prompt_hash": self.prompt_hash},
                user_input=user_input,
                input_tokens=input_tokens,
                intent_info=intent_info,
                output=static_response,
                output_tokens=output_tokens,
                latency_ms=latency,
                flags={"asked_clarification": False, "refusal": False, "static_response": True, "cache_hit": False},
                input_hash=input_hash
            )
            return

        # 3. Cache Check (v0.2.2)
        # 3. Cache Check (v0.2.2/v0.2.4 Segmented)
        # 3. Cache Check (v0.2.2/v0.2.4 Segmented)
        predicted_intent = intent_info.get("predicted", "CHAT")
        target_cache = self.caches.get(predicted_intent, self.caches["CHAT"])
        
        # v0.2.5: Composite Key for Stale Prevention
        # We assume input_hash is just the user input. We combine it with model config.
        composite_key_str = f"{input_hash}|{self.model_name}|{self.prompt_hash}"
        cache_key = hashlib.md5(composite_key_str.encode()).hexdigest()
        
        if cache_key in target_cache:
            cached_response = target_cache[cache_key]
            self.history.append({'role': 'assistant', 'content': cached_response})
            yield cached_response
            
            output_tokens = self._estimate_tokens(cached_response)
            self.last_turn_tokens = output_tokens
            latency = (time.time() - start_time) * 1000
            
            SecurityLogger.log_turn(
                session_id=self.session_id,
                request_id=request_id,
                model={"name": "cache", "source": f"memory.{predicted_intent}"},
                system_info={"name": "ViNNi", "version": self.prompt_version, "system_prompt_hash": self.prompt_hash},
                user_input=user_input,
                input_tokens=input_tokens,
                intent_info=intent_info,
                output=cached_response,
                output_tokens=output_tokens,
                latency_ms=latency,
                flags={"asked_clarification": False, "refusal": False, "static_response": False, "cache_hit": True},
                input_hash=input_hash
            )
            return

        # 3.5 Math Engine Intercept (v0.3.0)
        math_context = self._process_math_request(user_input, predicted_intent)
        if math_context:
            # Inject context by appending to user message (Avoids System-at-end issue)
            self.history[-1]['content'] += f"\n\n{math_context}"
        
        full_response = ""
        
        try:
            stream = ollama.chat(
                model=self.model_name,
                messages=self.history,
                options=self.options,
                stream=True,
            )
            
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                yield content
                
            self.history.append({'role': 'assistant', 'content': full_response})
            
            # Update Cache (v0.2.4 Segmented LRU)
            limit = self.cache_limits.get(predicted_intent, 50)
            if len(target_cache) >= limit:
                # Remove oldest (Next iter on dict returns first key)
                target_cache.pop(next(iter(target_cache)))
            
            target_cache[cache_key] = full_response
            
            # 4. Observability
            latency = (time.time() - start_time) * 1000
            output_tokens = self._estimate_tokens(full_response)
            self.last_turn_tokens = output_tokens
            
            SecurityLogger.log_turn(
                session_id=self.session_id,
                request_id=request_id,
                model={"name": self.model_name, "options": self.options},
                system_info={"name": "ViNNi", "version": self.prompt_version, "system_prompt_hash": self.prompt_hash},
                user_input=user_input,
                input_tokens=input_tokens,
                intent_info=intent_info,
                output=full_response,
                output_tokens=output_tokens,
                latency_ms=latency,
                flags={"asked_clarification": False, "refusal": False, "static_response": False, "cache_hit": False},
                input_hash=input_hash
            )
            
        except Exception as e:
            yield f"\n[System Error: {str(e)}]"
            
    def get_last_intent(self, user_input: str) -> str:
        # Compatibility wrapper for CLI
        return self.tagger.tag(user_input)["predicted"]
