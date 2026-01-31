import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def test_dynamic_tone():
    print("--- Testing Dynamic Tone Module (v0.2.8) ---")
    bot = ChatBot(model_name="llama3.1", system_prompt_path="prompts/system_v0.2.7.md")
    query = "Summarize the concept of gravity."

    # 1. CASUAL
    print("\n1. Tone: CASUAL")
    bot.set_tone("casual")
    resp_cas = ""
    for chunk in bot.chat(query): resp_cas += chunk
    print(f"   [Length: {len(resp_cas)}] {resp_cas[:50]}...")
    
    # 2. EXECUTIVE
    print("\n2. Tone: EXECUTIVE")
    bot.set_tone("executive")
    resp_exec = ""
    for chunk in bot.chat(query): resp_exec += chunk
    print(f"   [Length: {len(resp_exec)}] {resp_exec[:50]}...")
    
    # Heuristic Check
    # Executive should ideally have bullets or be very concise
    if len(resp_exec) < len(resp_cas):
         print("   ✅ Executive is shorter/concise.")
    elif "-" in resp_exec or "*" in resp_exec:
         print("   ✅ Executive contains list formatting.")
    else:
         print("   ⚠️ Executive distinction unclear (Subjective).")
         
    # 3. PROFESSIONAL
    print("\n3. Tone: PROFESSIONAL")
    bot.set_tone("professional")
    resp_pro = ""
    for chunk in bot.chat(query): resp_pro += chunk
    print(f"   [Length: {len(resp_pro)}] {resp_pro[:50]}...")

if __name__ == "__main__":
    test_dynamic_tone()
