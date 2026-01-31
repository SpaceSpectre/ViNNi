import ollama
import time
import os
from typing import List, Dict, Generator
from vinni.monitor import IntentTagger, SecurityLogger

class ChatBot:
    def __init__(self, model_name: str = "llama3", options: Dict = None, system_prompt_path: str = None):
        self.model_name = model_name
        self.options = options or {}
        self.history: List[Dict[str, str]] = []
        self.tagger = IntentTagger()
        self.system_prompt_content = ""
        
        if system_prompt_path and os.path.exists(system_prompt_path):
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                self.system_prompt_content = f.read()
                self.history.append({'role': 'system', 'content': self.system_prompt_content})

    def chat(self, user_input: str) -> Generator[str, None, None]:
        """
        Sends a message to the Ollama model and yields chunks of the response.
        """
        start_time = time.time()
        
        # 1. Intent Tagging
        intent = self.tagger.tag(user_input)
        
        # Yield metadata first (special format or just handle in UI? 
        # The generator contract expects strings. We'll yield the content.)
        # We can expose intent via a property or return tuple, but 
        # to keep the stream simple for main.py, we will just proceed.
        # Ideally, main.py should ask for the intent. 
        # Let's make this method yield the content, and we'll log at the end.
        
        self.history.append({'role': 'user', 'content': user_input})
        
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
            
            # 2. Observability Logging
            latency = (time.time() - start_time) * 1000
            SecurityLogger.log_turn(
                model=self.model_name,
                system_prompt=self.system_prompt_content,
                user_input=user_input,
                intent=intent,
                output=full_response,
                latency_ms=latency
            )
            
        except Exception as e:
            yield f"\n[System Error: {str(e)}]"
            
    def get_last_intent(self, user_input: str) -> str:
        return self.tagger.tag(user_input)
