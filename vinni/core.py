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
        triggers = ["loan", "interest", "annuity", "bond", "mortgage", "blackjack", "poker", "odds", "probability", "calculate", "invest", "compound", "growth", "rate", "%", "return"]
        # v0.5.0: ALWAYS validation trigger if keywords present (removed ANALYSIS exclusion)
        if not any(t in user_input.lower() for t in triggers):
            return None
        
        # 2. Extraction Prompt
        extraction_prompt = (
            "Extract mathematical variables from the user query into a valid JSON object. "
            "Supported keys: 'type' (loan, annuity, bond, probability_blackjack, probability_generic, compound_interest, simple_interest), 'principal', 'rate_annual', 'years', 'payment_freq', 'compounding_freq', 'face_value', 'coupon_rate', 'ytm', 'hand_size', 'payment_amount'. "
            "Nuances: 'invest' -> compound_interest usually. 'mortgage' -> loan. 'calculated annually' -> compounding_freq='annually'. "
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
                options={"temperature": 0.0}
            )
            content = resp['message']['content']
            # Clean json
            json_str = content.replace("```json", "").replace("```", "").strip()
            # Attempt to find '{' and '}' if extra text exists
            start = json_str.find("{")
            end = json_str.rfind("}")
            if start != -1 and end != -1:
                json_str = json_str[start:end+1]
            
            data = json.loads(json_str)
        except Exception as e:
            print(f"[DEBUG] Extraction Failed: {e}")
            data = {} 
        
        # Logic Flow continues even if extraction failed (using Force Logic)
        
        # Strict Routing (v0.3.1)
            # If the extracted type isn't explicitly supported, RETURN NONE.
            # This prevents generic "probability" queries (Coin Flip) from triggering Blackjack logic.
            supported_types = ["loan", "annuity", "bond", "probability_blackjack", "compound_interest", "simple_interest"] 
            # Note: prompts might return "blackjack" or "cards" based on prompt keywords, need to handle carefully.
            
            extracted_type = data.get("type", "unknown").lower()
            
            # Alias Mapping
            if "mortgage" in extracted_type: extracted_type = "loan"
            if "invest" in extracted_type: extracted_type = "compound_interest"
            if "deposit" in extracted_type: extracted_type = "compound_interest"
            
            # v0.4.1 FORCE LOGIC: If input has "invest" or "compound" and type is unknown, force compound_interest
            if (extracted_type == "unknown" or extracted_type == "" or "probability" in extracted_type or "calculation" in extracted_type) and ("invest" in user_input.lower() or "compound" in user_input.lower()):
                 extracted_type = "compound_interest"

            # v0.4.2 FORCE LOGIC: Aggressive Loan Override
            # If input explicitly mentions "loan" or "mortgage", force type to loan regardless of extraction error
            if "loan" in user_input.lower() or "mortgage" in user_input.lower():
                 extracted_type = "loan"
            # The extraction prompt asks for: 'loan', 'annuity', 'bond', 'probability_blackjack'
            
            result = None
            
            # AMBIGUITY GATE (v0.4.0)
            # If Blackjack sum query detected, bypass Engine AND force Clarification.
            if ("blackjack" in extracted_type or "cards" in user_input) and ("sum" in user_input.lower() or "total" in user_input.lower()):
                 return (
                     "SYSTEM: This query is AMBIGUOUS regarding card values (Ace=1/11? 10-cards?). "
                     "INSTRUCTION: You MUST ask the user for clarification before calculating. "
                     "Do not attempt to answer."
                 ), None, None

            # v0.9.0 Assumption Tracking
            assumptions = []
            
            if "loan" in extracted_type:
                # Default defaults
                freq = data.get("payment_freq")
                if not freq:
                    freq = "monthly"
                    assumptions.append("Payment Frequency: Monthly (Default)")
                    
                comp_freq = data.get("compounding_freq")
                if not comp_freq:
                    comp_freq = "monthly"
                    # Only log if relevant (not usually logged for US loans unless ambiguous)
                    # assumptions.append("Compounding: Monthly (Default)")
                
                # v0.4.2 Hard Override for Compounding Text
                if "calculated annually" in user_input.lower() or "compounded annually" in user_input.lower():
                    comp_freq = "annually"
                if "compounded semi-annually" in user_input.lower() or "semi-annual" in user_input.lower():
                    comp_freq = "semi-annually"
                if "canadian" in user_input.lower() and "mortgage" in user_input.lower():
                    comp_freq = "semi-annually"
                    assumptions.append("Compounding: Semi-Annually (Canadian Convention detected)")

                # v0.5.0 Parameter Validation
                principal_raw = data.get("principal", 0)
                principal = float(principal_raw)
                if principal <= 0:
                     return "SYSTEM ERROR: Loan detected but Principal amount is missing or zero. INSTRUCTION: Ask user for the loan amount explicitly.", None, None

                # v0.8.0 Advanced Finance Features
                # Extra Payment Extraction (Regex)
                extra_payment = 0.0
                extra_match = re.search(r"extra.*\$([\d,]+)", user_input.lower())
                if extra_match:
                     extra_payment = float(extra_match.group(1).replace(",", ""))
                
                # v0.7.0 Multi-Scenario Calculation (Super-Context)
                scenarios = {}
                
                # 1. Primary Request
                scenarios["PRIMARY_REQUEST"] = FinanceEngine.calculate_loan_interest(
                    principal=principal,
                    annual_rate=float(data.get("rate_annual", 0)),
                    months=int(data.get("years", 1)) * 12, # approx
                    payment_freq=freq,
                    compounding_freq=comp_freq,
                    extra_payment=extra_payment
                )
                
                # 2. Contextual Monthly (if needed)
                if freq != "monthly":
                    scenarios["CONTEXT_MONTHLY"] = FinanceEngine.calculate_loan_interest(
                        principal=principal,
                        annual_rate=float(data.get("rate_annual", 0)),
                        months=int(data.get("years", 1)) * 12,
                        payment_freq="monthly",
                        compounding_freq=comp_freq
                    )
                    
                # 3. Contextual Bi-weekly (if needed - Auto-Comparison for "Part d")
                if "biweekly" not in freq and "bi-weekly" not in freq:
                     scenarios["CONTEXT_BIWEEKLY"] = FinanceEngine.calculate_loan_interest(
                        principal=principal,
                        annual_rate=float(data.get("rate_annual", 0)),
                        months=int(data.get("years", 1)) * 12,
                        payment_freq="biweekly",
                        compounding_freq=comp_freq
                    )
                
                result = scenarios
            elif "compound" in extracted_type:
                 # Default frequency 1 (annual)
                 result = FinanceEngine.calculate_compound_interest(
                     principal=float(data.get("principal", 0)),
                     rate_annual=float(data.get("rate_annual", 0)),
                     years=int(data.get("years", 0)),
                     freq=1 # explicit default
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
                 result = ProbabilityEngine.solve_blackjack_probability()
            else:
                 # Generic probability or unknown type -> Bypass Engine
                 return None, None, None
            
            if result:
                # v0.9.0 Enhanced Context Injection
                assumption_text = ""
                if assumptions:
                    assumption_text = f"\nASSUMPTIONS APPLIED: {', '.join(assumptions)}. User did not specify these, but I used defaults. MENTION THIS."
                
                return (
                    f"SYSTEM: I have utilized the underlying math engine to provide accurate calculations.\n"
                    f"VERIFIED RESULT JSON: {json.dumps(result, indent=2)}\n"
                    f"{assumption_text}\n"
                    f"INSTRUCTION: Start with a 'TL;DR' summary (2 lines). Then provide a 'Detailed Breakdown'.\n"
                    f"INSTRUCTION: You MUST use these exact numbers. Do not re-calculate.\n"
                    f"INSTRUCTION: At the end of your response, append exactly: '[Confidence: 1.0 (Deterministic Math)]'\n",
                    result,
                    assumptions
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
        
        # v0.7.1: Strict Phrase Matching (Fixes "Canadian" trigger loop)
        help_phrases = ["what can you do", "your capabilities", "list intents", "what are your features", "help me understand what you do"]
        if any(p in normalized_input for p in help_phrases) or normalized_input.strip() == "help":
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
        math_result_pkg = self._process_math_request(user_input, predicted_intent)
        math_context = None
        engine_data = None
        assumptions = []
        
        if math_result_pkg:
            if isinstance(math_result_pkg, tuple):
                 math_context, engine_data, assumptions = math_result_pkg
            else:
                 # Legacy string support (e.g. error messages)
                 math_context = math_result_pkg
            
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
            
            # v0.4.0 MathVerifier (Post-Generation Check)
            # Only verify if we triggered Math Engine OR if "probability"/"calculate" in query
            triggers = ["loan", "interest", "annuity", "bond", "blackjack", "probability", "calculate"]
            if any(t in user_input.lower() for t in triggers):
                 from vinni.verifier import MathVerifier
                 verifier = MathVerifier(model_name=self.model_name)
                 v_result = verifier.verify(user_input, full_response)
                 
                 if v_result.get("status") == "FAIL":
                      rule_id = v_result.get("rule_id", "MV-XXX")
                      severity = v_result.get("severity", "HARD")
                      warning = f"\n\n⚠️ [MathVerifier] {rule_id} ({severity}): {v_result.get('reason')} RESULT IS INVALID."
                      yield warning
                      full_response += warning
                      # Update history with warning included?
                      self.history[-1]['content'] = full_response
                      
            # v0.9.0 Regression Snapshot
            if engine_data:
                 from vinni.snapshot import RegressionSnapshot
                 RegressionSnapshot.save(
                     question=user_input,
                     engine_input=intent_info, # Log extracted data
                     engine_output=engine_data,
                     final_response=full_response,
                     model_config={"name": self.model_name, "ver": self.prompt_version},
                     assumptions=assumptions
                 )
            
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
