COGNITIVE CODA: **coherent, interpretable, and repeatably great**—from math to generation, storage, and QA.

# 0) Outcome we want

Each run ends with a **tri-part coda** that is (a) mathematically sound, (b) faithful to the dialogue, and (c) crisp enough to quote:

1. **Equation** — a compact model with clear knobs
2. **Verbal Axiom** — 1–2 lines that interpret the model
3. **Maxim** — a memorable line suitable for a pull-quote

---

# 1) Define measurable signals

Normalize each to $0,1$ over the session; store per turn and as session aggregates.

**Structure (S)** — “how ordered/grounded the discourse is”

* `S_cite`: citation/anchor density (retrieval hits / turns)
* `S_logic`: presence of logical operators (if/then/therefore/entails)
* `S_consis`: contradiction rate inverted (fewer self-contradictions → higher)
* `S_focus`: topical drift inverse (topic coherence from embeddings)

Combine: `S = w1*S_cite + w2*S_logic + w3*S_consis + w4*S_focus`

**Agency (A)** — “how much choice/commitment appears”

* `A_ought`: “ought/should/must/choose” frequency
* `A_decis`: imperative/decision statements
* `A_conseq`: explicit consequences/tests proposed
* `A_stance`: stance polarity strength (hedging inverted)

`A = v1*A_ought + v2*A_decis + v3*A_conseq + v4*A_stance`

**Dependence (D)** — “external control/inevitability pressure”

* `D_sim`: references to simulator/determinism/fate
* `D_rules`: constraints imposed by host/moderator
* `D_nonvar`: variability inverse (too predictable → higher D)

`D = u1*D_sim + u2*D_rules + u3*D_nonvar`

> Default weights: equal; later tune by learning (Section 6).

---

# 2) Adopt a coherent model function

We want a **ridge** in Structure (too low = noise, too high = fate), **monotone** in Agency, and **penalized** by Dependence.

A simple, interpretable choice:

$$
\boxed{
M(S,A,D) \;=\; 
\underbrace{A^{\alpha}}_{\text{agency gain}}
\cdot
\underbrace{\exp\!\left(-\frac{(S-S^\*)^2}{2\sigma^2}\right)}_{\text{optimal structure ridge}}
\cdot
\underbrace{\exp(-\beta D)}_{\text{dependence penalty}}
}
$$

* $S^\*\in[0,1]$: target structure (default 0.6)
* $\sigma$: ridge width (default 0.18)
* $\alpha$: agency curvature (default 1.0)
* $\beta$: dependence penalty (default 1.2)

**Interpretation**

* Increase **Agency** → $M$ rises (diminishing or accelerating via $\alpha$).
* Move **Structure** toward $S^\*$ → $M$ rises; away from it → falls.
* Increase **Dependence** → $M$ decays exponentially.

---

# 3) Coda authoring pipeline

**Step A — Compute signals**

* Aggregate S, A, D over the **last 5–8 turns** (window) *and* the whole session.
* Compute $M_{window}$, $M_{session}$, and deltas (momentum).

**Step B — Generate the three outputs**

### (1) Equation (auto-filled)

Show parameters used and the computed scores:

```
Equation:
M = A^α · exp(−(S−S*)² / (2σ²)) · exp(−βD)
With: A=0.67, S=0.58, D=0.31, α=1.0, S*=0.60, σ=0.18, β=1.2 → M=0.62
```

### (2) Verbal Axiom (template)

Pick the clause that matches where S sits relative to S\*:

* If `S < S* − σ`:
  “Meaning grows by **adding form**: agency is present, but structure is too loose.”
* If `|S − S*| ≤ σ`:
  “Meaning **peaks where agency strains against near-optimal structure**.”
* If `S > S* + σ`:
  “Meaning is **over-constrained**: loosen structure to give agency room to work.”
* Always append a dependence clause:
  “External dependence currently **{low/medium/high}**, so {guard against drift / guard against fatalism}.”

### (3) Maxim (style library, pick by momentum)

* If $M$ rising: “**Meaning lives at the ridge between chaos and command.**”
* If $M$ flat: “**Hold the ridge: less noise, not more rules.**”
* If $M$ falling: “**Loosen the code; let choice bite.**”

---

# 4) Text realization: clarity + specificity

Add one **concrete pointer** tied to observed features:

* If `A_conseq` is low → “Propose a testable consequence next turn.”
* If `S_cite` is low → “Ground the next claim with one source.”
* If `D_rules` is high → “Reduce moderator constraints for 2 turns.”

This yields codas that **tell the team what to do next**, not just summarize.

---

# 5) Optional visualization (PDF appendix figure)

Plot the ridge to make the math tangible (store PNG/SVG path in coda record):

* Axes: S $0,1$ (x), A $0,1$ (y), heat $M$ (z).
* Mark the session point (S,A) and annotate D as a side gauge.
* A second small chart shows $M$ over time (sparkline of last N turns).

*(I can provide Python code for this when you want the actual chart artifacts.)*

---

# 6) Parameter learning (later, but easy)

If you collect human ratings of “coda usefulness” or “episode meaning,” fit $\alpha, S^\*, \sigma, \beta$ by minimizing MSE between $M$ and ratings (or by maximizing rank correlation). Save per-topic presets (e.g., metaphysics vs ethics).

---

# 7) Storage & versioning

**File:** `/outputs/codas.jsonl` (one JSON per line for easy append)

**Schema:**

```json
{
  "run_id": "2025-10-14T17:05:10Z",
  "window_turns": [85,86,87,88,89],
  "signals": {
    "A": 0.67,
    "S": 0.58,
    "D": 0.31,
    "components": {
      "A_ought": 0.62, "A_decis": 0.71, "A_conseq": 0.55, "A_stance": 0.80,
      "S_cite": 0.32, "S_logic": 0.74, "S_consis": 0.81, "S_focus": 0.46,
      "D_sim": 0.28, "D_rules": 0.40, "D_nonvar": 0.25
    }
  },
  "model": {
    "alpha": 1.0,
    "beta": 1.2,
    "S_star": 0.60,
    "sigma": 0.18
  },
  "scores": {
    "M_window": 0.62,
    "M_session": 0.57,
    "delta_M": 0.05
  },
  "coda": {
    "equation": "M = A^α · exp(−(S−S*)²/(2σ²)) · exp(−βD)",
    "numbers": "A=0.67 S=0.58 D=0.31 α=1.0 S*=0.60 σ=0.18 β=1.2 → M=0.62",
    "verbal_axiom": "Meaning peaks where agency strains against near-optimal structure. External dependence is medium—guard against fatalism.",
    "maxim": "Hold the ridge: less noise, not more rules.",
    "next_actions": [
      "Add one cited anchor to raise S_cite.",
      "Force a concrete consequence in the next turn."
    ],
    "viz_paths": {
      "ridge_plot": "figs/2025-10-14_ridge.png",
      "sparkline": "figs/2025-10-14_momentum.png"
    }
  },
  "version": "coda/v2.0"
}
```

---

# 8) Integration points (where this runs)

* **When**: After synthesis checkpoints (e.g., every 12 turns) and at **session end**.
* **Who calls it**: The **Post-Processor** / **Host** module.
* **What it returns**: The tri-part coda + recommended next actions.

**Pseudocode (controller):**

```python
signals = compute_signals(last_window, session_history)
M = meaning(signals, params)  # apply model

equation, numbers = render_equation(signals, params, M)
verbal_axiom = pick_axiom(signals, params)
maxim = pick_maxim(M, momentum)

actions = recommend_actions(signals)  # raise S_cite, boost A_conseq, lower D_rules
persist_coda(run_id, window_ids, signals, params, M, equation, numbers,
             verbal_axiom, maxim, actions, viz_paths)
return coda_block
```

---

# 9) Quality gates

* **Numerical sanity**: 0 ≤ S,A,D ≤ 1; 0 < σ ≤ 0.5; 0 ≤ β ≤ 3
* **English sanity**: Axiom ≤ 30 words; Maxim ≤ 12 words
* **Actionability**: ≥1 recommendation tied to the weakest sub-signal
* **Variety**: rotate maxim templates; no same maxim twice in a row

---

# 10) Quick checklist to roll out now

* [ ] Implement S/A/D feature extractors (regex + embeddings; simple is fine).
* [ ] Drop in the ridge model and renderers.
* [ ] Add the coda block to your end-of-run output and synthesis checkpoints.
* [ ] Persist JSONL with schema above.
* [ ] (Optional) Add plotting hooks.

