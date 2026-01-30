import ollama
from typing import List, Dict, Generator

class ChatBot:
    def __init__(self, model_name: str = "llama3", options: Dict = None, system_prompt: str = None):
        self.model_name = model_name
        self.options = options or {}
        self.history: List[Dict[str, str]] = []
        if system_prompt:
            self.history.append({'role': 'system', 'content': system_prompt})

    def chat(self, user_input: str) -> Generator[str, None, None]:
        """
        Sends a message to the Ollama model and yields chunks of the response.
        Updates history automatically.
        """
        self.history.append({'role': 'user', 'content': user_input})
        
        try:
            stream = ollama.chat(
                model=self.model_name,
                messages=self.history,
                options=self.options,
                stream=True,
            )
            
            full_response = ""
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                yield content
                
            self.history.append({'role': 'assistant', 'content': full_response})
            
        except ollama.ResponseError as e:
            yield f"\n[Error: {e.error}]"
        except Exception as e:
            yield f"\n[System Error: {str(e)}]"

    def clear_history(self):
        self.history = []
