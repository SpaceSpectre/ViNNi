from vinni.core import ChatBot
import sys

def test():
    print("Testing ViNNi with Llama 3.1 options...")
    options = {
        "num_ctx": 2048, # Smaller for test
        "temperature": 0.7
    }
    # Note: connect timeout might happen if model is still pulling
    try:
        bot = ChatBot(model_name="llama3.1", options=options)
        response_text = ""
        print("User: Hello")
        print("ViNNi: ", end="")
        for chunk in bot.chat("Hello, verify you are working with options."):
            print(chunk, end="")
            response_text += chunk
        print("\n\nTest Finished.")
        if len(response_text) > 0:
            print("SUCCESS: Received response.")
        else:
            print("FAILURE: No response.")
            sys.exit(1)
    except Exception as e:
        print(f"FAILURE: Exception {e}")
        sys.exit(1)

if __name__ == "__main__":
    test()
