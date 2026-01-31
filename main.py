import sys
from vinni.core import ChatBot

def main():
    print("Welcome to ViNNi Local AI")
    print("-" * 50)
    print("Select Model to Init:")
    print("1. Llama 3.1 (8B) - [Optimized: GPU, Context: 8k, Temp: 0.6]")
    print("2. Qwen 2.5 (7B)  - [Default]")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    model_name = "llama3.1"
    options = {}
    
    if choice == "1":
        model_name = "llama3.1"
        options = {
            "num_ctx": 8192,
            "temperature": 0.6,
            "top_p": 0.9,
            # "num_gpu": 1 # Often auto-detected, but can be forced if needed
        }
    elif choice == "2":
        model_name = "qwen2.5"
        # Defaults
        options = {}
    else:
        print("Invalid choice, defaulting to Llama 3.1")
        model_name = "llama3.1"
        options = {
            "num_ctx": 8192,
            "temperature": 0.6,
            "top_p": 0.9,
        }

    print(f"\nInitializing ViNNi with model: {model_name}...")
    if options:
        print(f"Configuration: {options}")

    # Load v0.1.2 System Prompt
    prompt_path = "prompts/system_v0.1.2.md"
    
    try:
        bot = ChatBot(model_name=model_name, options=options, system_prompt_path=prompt_path)
    except Exception as e:
        print(f"Error initializing bot: {e}")
        return
    
    print("ViNNi v0.1.4 is ready. (Check vinni.log for audit)")
    print("-" * 50)

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # Get intent before chatting
            current_intent = bot.get_last_intent(user_input)
                
            print(f"ViNNi [{current_intent}]: ", end="", flush=True)
            
            for chunk in bot.chat(user_input):
                print(chunk, end="", flush=True)
            
            print(f"\n[Tokens: ~{bot.last_turn_tokens}]")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
