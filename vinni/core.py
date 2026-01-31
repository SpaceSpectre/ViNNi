import ollama
import time
import os
from typing import List, Dict, Generator
from vinni.monitor import IntentTagger, SecurityLogger

import uuid

class ChatBot:
    def __init__(self, model_name: str = "llama3", options: Dict = None, system_prompt_path: str = None):
        self.model_name = model_name
        self.options = options or {}
        self.history: List[Dict[str, str]] = []
        self.tagger = IntentTagger()
        self.system_prompt_content = ""
        self.session_id = str(uuid.uuid4())[:8] # Short session ID
        self.prompt_version = "unknown"
        self.last_turn_tokens = 0 # store roughly
        
        if system_prompt_path and os.path.exists(system_prompt_path):
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt_content = f.read()
                self.history.append({'role': 'system', 'content': self.system_prompt_content})
                # Extract version if possible
                if "Version: ViNNi" in self.system_prompt_content:
                    try:
                        self.prompt_version = self.system_prompt_content.split("Version: ViNNi")[-1].strip()
                    except:
                        pass

    def _estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def chat(self, user_input: str) -> Generator[str, None, None]:
        """
        Sends a message to the Ollama model and yields chunks of the response.
        """
        start_time = time.time()
        self.last_turn_tokens = 0
        input_tokens = self._estimate_tokens(user_input)
        
        # 1. Intent Tagging
        intent = self.tagger.tag(user_input)
        
        self.history.append({'role': 'user', 'content': user_input})
        
        # 2. Static Response Intercepts (v0.1.3)
        normalized_input = user_input.lower()
        static_response = None
        
        if "capabilities" in normalized_input or ("what" in normalized_input and "do" in normalized_input and "can" in normalized_input):
            static_response = (
                "I support the following response intents:\n"
                "- CHAT: General conversation, greetings, and simple explanations.\n"
                "- CODE: Writing or explaining code snippets.\n"
                "- ANALYSIS: Structured explanations of concepts and reasoning.\n"
                "- DOCUMENT: Editing, drafting, or improving written text."
            )
        elif "who created you" in normalized_input or "who initialized you" in normalized_input:
             static_response = "I am ViNNi, a locally run AI system initialized by Abhishek Arora."

        if static_response:
            self.history.append({'role': 'assistant', 'content': static_response})
            yield static_response
            
            output_tokens = self._estimate_tokens(static_response)
            self.last_turn_tokens = output_tokens
            
            latency = (time.time() - start_time) * 1000
            SecurityLogger.log_turn(
                session_id=self.session_id,
                model="static-rule",
                system_prompt_version=self.prompt_version,
                user_input=user_input,
                intent="SYSTEM",
                output=static_response,
                latency_ms=latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens
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
            
            # 3. Observability
            latency = (time.time() - start_time) * 1000
            output_tokens = self._estimate_tokens(full_response)
            self.last_turn_tokens = output_tokens
            
            SecurityLogger.log_turn(
                session_id=self.session_id,
                model=self.model_name,
                system_prompt_version=self.prompt_version,
                user_input=user_input,
                intent=intent,
                output=full_response,
                latency_ms=latency,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            
        except Exception as e:
            yield f"\n[System Error: {str(e)}]"
            
    def get_last_intent(self, user_input: str) -> str:
        return self.tagger.tag(user_input)
