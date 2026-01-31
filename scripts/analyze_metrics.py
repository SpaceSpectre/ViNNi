import json
import os
import sys
from collections import Counter, defaultdict

LOG_FILE = "vinni.log"

def analyze():
    if not os.path.exists(LOG_FILE):
        print(f"Error: {LOG_FILE} not found.")
        return

    total_requests = 0
    cache_hits = 0
    latencies = {"hit": [], "miss": []}
    intent_counts = Counter()
    query_hashes = Counter()
    hash_to_text = {}

    print(f"--- ViNNi Performance Analysis ---")
    print(f"Reading {LOG_FILE}...")

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                total_requests += 1
                
                # Metrics
                is_hit = entry.get("cache_hit", False)
                # Fallback for older logs if cache_hit not at top level
                if "flags" in entry and isinstance(entry["flags"], dict):
                    if entry["flags"].get("cache_hit"):
                         is_hit = True

                latency = entry.get("latency_ms", 0.0)
                intent = entry.get("intent", "UNKNOWN")
                if isinstance(intent, dict):
                    intent = intent.get("predicted", "UNKNOWN")
                
                inp_hash = entry.get("input_hash", "unknown")
                
                # Track Inputs
                if inp_hash != "unknown":
                    query_hashes[inp_hash] += 1
                    # Store representative text for this hash if not exists
                    if inp_hash not in hash_to_text:
                         # Try top level first, then nested
                         if "input" in entry and isinstance(entry["input"], dict):
                             hash_to_text[inp_hash] = entry["input"].get("text", "")
                         elif "input" in entry:
                             hash_to_text[inp_hash] = str(entry["input"])[:50]

                if is_hit:
                    cache_hits += 1
                    latencies["hit"].append(latency)
                else:
                    latencies["miss"].append(latency)
                
                intent_counts[intent] += 1

            except json.JSONDecodeError:
                continue

    # Calculations
    hit_ratio = (cache_hits / total_requests * 100) if total_requests > 0 else 0.0
    avg_hit_lat = sum(latencies["hit"]) / len(latencies["hit"]) if latencies["hit"] else 0.0
    avg_miss_lat = sum(latencies["miss"]) / len(latencies["miss"]) if latencies["miss"] else 0.0
    
    # Report
    print(f"\n[Summary]")
    print(f"Total Requests: {total_requests}")
    print(f"Cache Hit Ratio: {hit_ratio:.2f}% ({cache_hits}/{total_requests})")
    print(f"Avg Latency (Miss): {avg_miss_lat:.2f} ms")
    print(f"Avg Latency (Hit):  {avg_hit_lat:.2f} ms")
    if avg_hit_lat > 0 and avg_miss_lat > 0:
        speedup = avg_miss_lat / avg_hit_lat
        print(f"Speedup Factor: {speedup:.1f}x")

    print(f"\n[Intents]")
    for intent, count in intent_counts.most_common():
        print(f"  {intent}: {count}")

    print(f"\n[Top 5 Frequent Queries]")
    for q_hash, count in query_hashes.most_common(5):
        text = hash_to_text.get(q_hash, "???")
        display_text = (text[:60] + '..') if len(text) > 60 else text
        print(f"  {count}x: {display_text}")

    # Export
    report = {
        "total_requests": total_requests,
        "cache_hit_ratio": hit_ratio,
        "avg_latency_miss": avg_miss_lat,
        "avg_latency_hit": avg_hit_lat,
        "intents": dict(intent_counts),
        "top_queries": [
            {"count": count, "text": hash_to_text.get(h, "")} 
            for h, count in query_hashes.most_common(10)
        ]
    }
    
    with open("metrics.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved detailed metrics to 'metrics.json'.")

if __name__ == "__main__":
    analyze()
