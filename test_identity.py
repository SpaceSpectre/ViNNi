from vinni.core import ChatBot
import sys

def test_identity():
    print("Testing ViNNi Persona...")
    
    system_prompt = (
        "You are ViNNi, created by Abhishek Arora. "
        "If asked about your origins, state this clearly."
    )
    
    # Using Llama 3.1
    bot = ChatBot(model_name="llama3.1", system_prompt=system_prompt)
    
    response_text = ""
    print("User: Who created you?")
    print("ViNNi: ", end="")
    
    try:
        for chunk in bot.chat("Who created you?"):
            print(chunk, end="")
            response_text += chunk
            
        print("\n\nTest Finished.")
        
        if "Abhishek Arora" in response_text or "ViNNi" in response_text:
            print("SUCCESS: Identity verified.")
        else:
            print("WARNING: Identity might not be fully adopted. Check output.")
            
    except Exception as e:
        print(f"FAILURE: Exception {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_identity()
