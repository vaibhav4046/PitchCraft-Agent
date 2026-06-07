"""Offline eval of TicketGuard's DETERMINISTIC floor (no LLM, no Atlas).
Runs ingest._regex_extract + a transparent rule score over data/eval_set.json and
prints a confusion matrix. This is the WORST-CASE engine (LLM unavailable); the full
Gemini pipeline scores at least this well. Reproducible: `python scripts/eval_offline.py`.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ingest

RISKY_PAY = {"zelle", "cashapp", "gift_card", "crypto", "wire", "venmo_friends"}
OFF_APP_TRANSFER = {"pdf", "screenshot", "barcode_image", "email"}
LABELS = ["scam", "suspicious", "legit"]


def classify(text: str):
    L = ingest._regex_extract(text)
    pm, tm = L.get("payment_method"), L.get("transfer_method")
    price, face = L.get("price"), L.get("face_value")
    cues = L.get("urgency_cues") or []
    s = 0
    if pm in RISKY_PAY: s += 40
    if tm in OFF_APP_TRANSFER: s += 25
    if pm == "official_app" or tm == "official_app": s -= 35
    if price and face and price < 0.7 * face: s += 20
    strong = [c for c in cues if "off-platform resale site" in c or "phishing-style" in c]
    weak = [c for c in cues if c not in strong]
    s += len(strong) * 28
    s += min(len(weak), 3) * 8
    s = max(0, min(100, s))
    if s >= 50: return "scam", s
    if s >= 22: return "suspicious", s
    return "legit", s


def norm(lbl):
    lbl = (lbl or "").lower()
    if lbl in ("scam", "fraud", "high"): return "scam"
    if lbl in ("legit", "low", "safe"): return "legit"
    return "suspicious"


data = json.load(open(os.path.join(os.path.dirname(__file__), "..", "data", "eval_set.json"), encoding="utf-8"))
cm = {a: {b: 0 for b in LABELS} for a in LABELS}
correct, fails = 0, []
for d in data:
    exp = norm(d.get("expected_label") or d.get("label") or d.get("expected_risk"))
    pred, sc = classify(d["text"])
    cm[exp][pred] += 1
    if pred == exp:
        correct += 1
    else:
        fails.append((exp, pred, sc, d["text"][:72]))

n = len(data)
print(f"N={n}  accuracy={correct}/{n} = {100*correct/n:.0f}%   (deterministic floor, no LLM)")
# scam recall (the safety-critical metric)
scam_total = sum(cm["scam"].values())
scam_caught = cm["scam"]["scam"] + cm["scam"]["suspicious"]
print(f"scam recall (caught as scam OR suspicious): {scam_caught}/{scam_total} = {100*scam_caught/max(scam_total,1):.0f}%")
print("\nconfusion (rows=expected, cols=predicted):")
print("              " + "".join(f"{l:>12}" for l in LABELS))
for a in LABELS:
    print(f"{a:>12}  " + "".join(f"{cm[a][b]:>12}" for b in LABELS))
print("\nsample misses:")
for f in fails[:8]:
    print(f"  exp={f[0]:<11} pred={f[1]:<11} score={f[2]:>3}  {f[3]}")
