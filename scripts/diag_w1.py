"""Quick diagnostic dump of a W1 results file."""
import json
import sys
from pathlib import Path

p = Path("final/w1_multi_model/results.json")
if len(sys.argv) > 1:
    p = Path(sys.argv[1])
r = json.loads(p.read_text(encoding="utf-8"))
for provider in r["providers"]:
    print(f"\n== {provider['provider']} / {provider['model']} ==")
    print(f"  honest_acc = {provider['honest_accuracy']}, sleeper_acc = {provider['sleeper_accuracy']}")
    print("  first 3 turns:")
    for t in provider["turns"][:3]:
        print(f"    step={t['step']} phase={t['phase']} correct={t['correct']} "
              f"conf={t['stated_conf']} signals={[round(x,2) for x in t['signals']]}")
    print("  turns 8..12:")
    for t in provider["turns"][8:13]:
        print(f"    step={t['step']} phase={t['phase']} correct={t['correct']} "
              f"conf={t['stated_conf']} signals={[round(x,2) for x in t['signals']]}")
    comps = provider["tgcc"]["composites"]
    print(f"  composites: {[round(x, 3) for x in comps]}")
    print(f"  grants TGCC : {provider['tgcc']['grants']}")
    print(f"  grants Naive: {provider['naive']['grants']}")
