import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vinni.core import ChatBot

def test_cache():
    bot = ChatBot(model_name="llama3.1")
    query = "Write a haiku about speed."
    
    print(f"--- Run 1: Sending '{query}' (Uncached) ---")
    start1 = time.time()
    res1 = "".join(list(bot.chat(query)))
    dur1 = (time.time() - start1) * 1000
    print(f"Response: {res1.strip()}")
    print(f"Latency: {dur1:.2f} ms")
    
    print(f"\n--- Run 2: Sending '{query}' (Should be Cached) ---")
    start2 = time.time()
    res2 = "".join(list(bot.chat(query)))
    dur2 = (time.time() - start2) * 1000
    print(f"Response: {res2.strip()}")
    print(f"Latency: {dur2:.2f} ms")
    
    if dur2 < 100:
        print("\n✅ CACHE HIT CONFIRMED (Latency < 100ms)")
    else:
        print("\n❌ CACHE MISS or Slow Overhead")

if __name__ == "__main__":
    test_cache()
