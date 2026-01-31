import time
import sys
import os

# Ensure we can import vinni
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vinni.core import ChatBot

def test_cache_invalidation():
    print("--- Testing Cache Invalidation (v0.2.5) ---")
    
    bot = ChatBot(model_name="llama3.1")
    prompt = "Tell me a random number between 1 and 100."
    
    # Run 1: Cold Start
    print(f"1. Sending: '{prompt}'")
    start = time.time()
    for _ in bot.chat(prompt): pass
    lat1 = (time.time() - start) * 1000
    print(f"   Latency: {lat1:.2f} ms (Miss)")
    
    # Run 2: Repeat (Should Hit)
    print(f"2. Sending: '{prompt}' (Expect Hit)")
    start = time.time()
    response2 = ""
    for chunk in bot.chat(prompt): response2 += chunk
    lat2 = (time.time() - start) * 1000
    print(f"   Latency: {lat2:.2f} ms")
    
    if lat2 > 100:
        print("   ❌ FAILED: Cache Hit too slow.")
        return False
    else:
        print("   ✅ CACHE HIT verified.")
        
    # Run 3: Change Hash (Simulate Model Update)
    print("3. Mutating System Prompt Hash (Simulating Update)...")
    original_hash = bot.prompt_hash
    bot.prompt_hash = "modified_hash_v999"
    
    # Run 4: Repeat (Should Miss bc Key Changed)
    print(f"4. Sending: '{prompt}' (Expect Miss)")
    start = time.time()
    response4 = ""
    for chunk in bot.chat(prompt): response4 += chunk
    lat4 = (time.time() - start) * 1000
    print(f"   Latency: {lat4:.2f} ms")
    
    if lat4 < 100:
        print("   ❌ FAILED: Should have missed cache (Stale response served).")
        return False
    else:
        print("   ✅ CACHE INVALIDATION verified (Latency high).")
        
    return True

if __name__ == "__main__":
    if test_cache_invalidation():
        print("\nSUCCESS: Cache Logic is Robust.")
    else:
        print("\nFAILURE: Cache Logic is Flawed.")
        sys.exit(1)
