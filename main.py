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
            "top_p": 0.9,
            "num_gpu": 99 # Force all layers to GPU
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

    # Load v0.2.7 System Prompt (Adaptive Tone)
    prompt_path = "prompts/system_v0.2.7.md"
    
    try:
        bot = ChatBot(model_name=model_name, options=options, system_prompt_path=prompt_path)
    except Exception as e:
        print(f"Error initializing bot: {e}")
        return
    
    from vinni import __version__
    print(f"ViNNi v{__version__} is ready. (Check vinni.log for audit)")
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
            # 0. Command Intercepts (v0.2.0)
            if user_input.strip() == "!version":
                from vinni import __version__
                print(f"ViNNi v{__version__}")
                print("-" * 50)
                continue
                
            if user_input.strip() == "!help":
                print("ViNNi Help & Commands:")
                print("  !help       - Show this menu")
                print("  !version    - Show current version")
                print("  exit / quit - End session")
                print("\nSupported Intents:")
                print("  CHAT       - General conversation")
                print("  CODE       - Generate/Explain code")
                print("  ANALYSIS   - Deep explanation")
                print("  DOCUMENT   - Draft/Edit text")
                print("-" * 50)
                continue

            if user_input.strip().startswith("!tone"):
                parts = user_input.strip().split()
                if len(parts) < 2:
                    print("Usage: !tone [casual | professional | executive | adaptive]")
                    continue
                
                new_tone = parts[1].lower()
                if bot.set_tone(new_tone):
                    print(f"✅ Tone switched to: {new_tone.upper()}")
                else:
                    print(f"❌ Invalid tone. Valid: casual, professional, executive, adaptive")
                continue

            # 1. Intent & Confidence Check (v0.1.5)
            # We peek at intent before chatting to handle low confidence
            intent_data = bot.tagger.tag(user_input)
            current_intent = intent_data["predicted"]
            confidence = intent_data["confidence"]
            
            # Confidence Fallback
            if confidence < 0.6:
                print(f"ViNNi [SYSTEM]: I'm not sure if you want {current_intent} or something else (Confidence: {confidence}).")
                print("Could you please clarify? (e.g., 'Write code for...', 'Explain...')")
                print("-" * 50)
                continue

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
