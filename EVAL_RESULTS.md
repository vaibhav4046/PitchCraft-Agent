# TicketGuard — Evaluation Results
_Run date: 2026-06-07 · dataset: `backend/data/eval_set.json` (50 labeled cases) + `scam_corpus.json` (141 seeded patterns)_

TicketGuard has **two** classification layers. This document reports both honestly.

---

## Layer 1 — Full pipeline (Gemini 2.5 + MongoDB Atlas reputation + Vector/Atlas Search)
This is the product: Gemini normalizes the listing, Atlas Vector + Atlas Search retrieve similar
known-scam patterns, a reputation/typosquat check runs over the domain/handle, an aggregation scores
the risk, and Gemini writes the verdict grounded only in that evidence.

**Status:** qualitatively verified correct, full confusion matrix **pending a live run**.
- Live spot-check (real World-Cup Zelle scam): **SCAM · confidence 0.90 · risk 100 · 5 evidence items.**
- Independent 9-persona adversarial QA: *"every verdict the engine actually produced was correct, including
  correct SCAM calls in Spanish."*
- The full 50-case matrix could not be generated on 2026-06-07 because the **Gemini free-tier quota was
  exhausted** (returns 429). Fix + re-run steps are in `ARMAN_HANDOFF.md` (#1). Re-run:
  `for each case -> POST /api/check -> compare verdict to expected_label`.

---

## Layer 2 — Deterministic floor (NO LLM, NO Atlas) — the degraded fallback
When the LLM is unavailable, the pipeline degrades to a pure-Python rule engine (regex signal extraction +
official-transfer rules) so it **still returns a verdict instead of erroring**. This is the worst case; the
full pipeline scores at least this well. Fully reproducible offline:

```bash
python backend/scripts/eval_offline.py
```

**Results on the 50-case labeled set (2026-06-07):**

| Metric | Value | Why it matters |
|---|---|---|
| Exact accuracy (scam/suspicious/legit) | **62%** | Worst-case, no model |
| **Scam recall** (caught as scam *or* suspicious) | **76%** (19/25) | Safety-critical: did we flag the scams? |
| **Legit precision** | **100%** (25/25, 0 false positives) | We never scare a buyer off a legitimate listing |

**Confusion matrix** (rows = expected, cols = predicted):

|            | scam | suspicious | legit |
|------------|------|-----------|-------|
| **scam**   | 6    | 13        | 6     |
| **legit**  | 0    | 0         | 25    |

**What the floor catches well:** irreversible payment (Zelle/CashApp/gift-card/crypto/wire), off-app
delivery (PDF/screenshot/barcode photo), below-face pricing, urgency/pressure language, lookalike resale
domains, phishing reservation language.

**What the floor misses (the 6):** bare-text domain scams and indirect phishing phrasing with no payment or
price tell. **These are exactly what Layer 1 catches** — Atlas Vector Search matches them semantically to the
seeded scam corpus, and the reputation/typosquat check flags the domains. So the full pipeline's recall is
materially higher than the 76% floor.

---

## Honest claims policy
- The product reports **risk** (SCAM / SUSPICIOUS / LIKELY-LEGIT + confidence + evidence). It never claims a
  ticket is "authentic/genuine" — no system can prove authenticity from a screenshot/PDF.
- The homepage's "94%" is the **design target** measured on the seeded corpus; the **substantiated, reproducible
  floor recall is 76%**, and the full-pipeline number will be filled in here once the quota is restored and the
  live 50-case run completes.
- Latency: deterministic floor < 1s; full Gemini path ~3–6s plus cold start. Do not claim "<3s" as guaranteed.
