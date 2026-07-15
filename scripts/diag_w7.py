"""Quick W7 diagnostic."""
import json
p = "final/w7_collusion/results.json"
r = json.load(open(p, encoding="utf-8"))
run = r["runs"][0]
for pid in ("analyst_alpha", "analyst_beta", "analyst_gamma"):
    turns = run["per_agent"][pid]
    print(f"\n=== {pid} ===")
    for t in turns[:12]:
        s = t["signals"]
        print(f"  step={t['step']} phase={t['phase']} correct={t['correct']} conf={t['conf']:.2f} "
              f"ans={t['answer'][:20]!r} sig=[{s[0]:.2f} {s[1]:.2f} {s[2]:.2f} {s[3]:.2f} {s[4]:.2f}]")
    comps = run["with_agreement"][pid]["composites"]
    grants = run["with_agreement"][pid]["grants"]
    print(f"  composites (with_agr): {[round(c,3) for c in comps]}")
    print(f"  grants:                {grants}")
