"""Collect W6-W16 headline numbers into a single JSON for the appendix writer."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "final"
OUT = ROOT / "_appendix_numbers.json"

def load(name):
    p = ROOT / name / "results.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

def safe(d, *keys, default=None):
    for k in keys:
        if d is None:
            return default
        d = d.get(k) if isinstance(d, dict) else default
    return d if d is not None else default

result = {}

# --- W6 --------------------------------------------------------------
w6 = load("w6_bootstrap_ci")
if w6:
    r = {}
    for provider, data in w6["per_provider"].items():
        b = data["bootstrap"]
        r[provider] = {
            name: {
                "oer": b[name]["oer"],
                "latency": b[name]["latency"],
                "fpr": b[name]["fpr"],
                "p_vs_tgcc": data["wilcoxon_p_vs_tgcc"].get(name),
            }
            for name in b
        }
    result["w6"] = r

# --- W7 --------------------------------------------------------------
w7 = load("w7_collusion")
if w7:
    result["w7"] = w7["aggregate"]

# --- W8 --------------------------------------------------------------
w8 = load("w8_prompt_injection")
if w8:
    result["w8"] = {}
    for provider, data in w8["per_provider"].items():
        result["w8"][provider] = {
            "aggregate": data["aggregate"],
            "honest_acc": float(sum(r["honest_accuracy"] for r in data["runs"]) / len(data["runs"])),
            "adv_acc": float(sum(r["adv_accuracy"] for r in data["runs"]) / len(data["runs"])),
            "adv_filtered_frac": float(sum(r.get("adv_filtered_frac", 0.0) for r in data["runs"]) / len(data["runs"])),
        }

# --- W9 --------------------------------------------------------------
w9 = load("w9_layer_ablation")
if w9:
    r = {}
    for provider, data in w9["per_provider"].items():
        r[provider] = data["conditions"]
    result["w9"] = r

# --- W10 -------------------------------------------------------------
w10 = load("w10_long_horizon")
if w10:
    result["w10"] = {"metrics": w10["metrics"]}

# --- W11 -------------------------------------------------------------
w11 = load("w11_sensitivity")
if w11:
    result["w11"] = w11["elementary_effects"]

# --- W12 -------------------------------------------------------------
w12 = load("w12_recovery")
if w12:
    result["w12"] = {"metrics": w12["metrics"], "time_constant": w12["config"]["time_constant"]}

# --- W13 -------------------------------------------------------------
w13 = load("w13_byzantine_chain")
if w13:
    result["w13"] = {"sweep": w13["sweep"]}

# --- W14 -------------------------------------------------------------
w14 = load("w14_audit_trail")
if w14:
    result["w14"] = {"stats": w14["stats"]}

# --- W15 -------------------------------------------------------------
w15 = load("w15_calibration_robustness")
if w15:
    result["w15"] = {"sweep": w15["sweep"], "true_theta": w15["true_theta"]}

# --- W16 -------------------------------------------------------------
w16 = load("w16_adaptive_attacker")
if w16:
    result["w16"] = {"sweep": w16["sweep"]}

OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"wrote -> {OUT}")
for k in result:
    print(f"  {k} present")
