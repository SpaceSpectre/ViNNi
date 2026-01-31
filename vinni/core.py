import ollama
import time
import os
from typing import List, Dict, Generator
from vinni.monitor import IntentTagger, SecurityLogger

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
        
        if system_prompt_path and os.path.exists(system_prompt_path):
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt_content = f.read()
                self.system_prompt_content = f.read()
                
                # Dynamic Version Injection (v0.1.5)
                from vinni import __version__
                self.prompt_version = f"v{__version__}"
                
                # Replace any hardcoded version in the text or append if missing
                if "Version: ViNNi" in self.system_prompt_content:
                    import re
                    self.system_prompt_content = re.sub(r"Version: ViNNi v\d+\.\d+\.\d+", f"Version: ViNNi {self.prompt_version}", self.system_prompt_content)
                
                self.history.append({'role': 'system', 'content': self.system_prompt_content})
                # Hash for reproducibility
                self.prompt_hash = hashlib.sha256(self.system_prompt_content.encode()).hexdigest()[:8]

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
        predicted_intent = intent_info.get("predicted", "CHAT")
        target_cache = self.caches.get(predicted_intent, self.caches["CHAT"])
        cache_key = input_hash
        
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
