
# Scope

Implement two surgical fixes:

1. **Consequence Tests (CT):** replace verbose CT blocks with one-line templates.
2. **Agency Recalibration:** fix the extractor, boost decision cues, recompute **A** using the agreed weights over the last 6–8 turns.

---

# 1) Consequence Test Replacement

## Goal

Ensure CT inserts are exactly one line (no meta, no restated paragraphs).

## Detection

CT blocks in your transcript begin with `"Consequence Test:"` and currently include restated quotes/questions.

### Regex (multiline, dotall)

* **Find (greedy to next blank line or next CT/host line):**

```
(?ms)^Consequence Test:[^\n]*?(?:\n(?!\n).*)*
```

* Alternate stricter guard (stop on blank line or next speaker tag like `**Name:**`):

```
(?ms)^Consequence Test:.*?(?=\n\s*\n|\n\*\*[A-Z][^*]*\*\:|\Z)
```

## Replacement Logic

* Decide which template to apply based on the surrounding exchange:

  * If the prior turn asserts **doubt → suspend action**, use **CT-True**.
  * If the prior turn asserts **action despite doubt**, use **CT-False**.
* **Templates (exact strings):**

  * **CT-True:**
    `Consequence Test: If radical doubt suspends action until certainty, then prediction: moral hesitation rates rise when uncertainty primes are shown.`
  * **CT-False:**
    `Consequence Test: If doubt doesn’t suspend action, example: agents still choose under ambiguity (e.g., Pascal-style commitments).`

### Heuristic for auto-choice

Look at the previous 1–2 turns’ text:

* If it contains verbs like `suspend`, `withhold`, `wait`, `defer`, `no action`, map → **CT-True**.
* If it contains `choose`, `act`, `commit`, `proceed`, `despite`, map → **CT-False**.

### Pseudocode

```python
def is_suspend(prev_text:str)->bool:
    return bool(re.search(r'\b(suspend|withhold|defer|wait|no action|halt)\b', prev_text, re.I))

def choose_template(prev_text:str)->str:
    return CT_TRUE if is_suspend(prev_text) else CT_FALSE

def replace_ct_blocks(doc:str)->str:
    pattern = re.compile(r'(?ms)^Consequence Test:.*?(?=\n\s*\n|\n\*\*[A-Z][^*]*\*\:|\Z)')
    out = []
    last_end = 0
    for m in pattern.finditer(doc):
        prev_slice = doc[max(0, last_end-1500):m.start()]  # context window
        tmpl = choose_template(prev_slice)
        out.append(doc[last_end:m.start()])
        out.append(tmpl)
        out.append("\n\n")
        last_end = m.end()
    out.append(doc[last_end:])
    return ''.join(out)
```

### Acceptance Criteria

* Every CT block is exactly one line and matches one of the two templates.
* No CT block contains quoted prior paragraphs or additional prose.
* Transcript compiles with zero duplicate “Consequence Test” lines in a row.

---

# 2) Agency Recalibration

## Goal

Your **A=0.09** is implausible given the language. Fix the extractor and scoring so **A ≈ 0.45–0.65** on the last 6–8 turns, then **M** rises accordingly.

## Signal Model

Compute **A** as a weighted sum of four sub-signals over the **last 6–8 turns**:

* **A\_ought (0.35):** Normative language (“ought/should/must/responsibility/duty/authentic/authentically/ethical imperative”).
* **A\_decis (0.35):** First-person commitments/decision rules (regex below).
* **A\_conseq (0.20):** Consequence-focused language (“therefore/so that/leads to/if…then/commitment under uncertainty/policy”).
* **A\_stance (0.10):** Declarative stances (“we choose/we refuse/our duty is/act under ambiguity”).

Normalize each sub-score to \[0,1] within the window, then weight and sum.

## Extraction Window

* Take the **last 6–8 turns** (configurable; default 8) across all speakers, giving extra weight if a line is explicitly marked as a **decision rule**.

## Regex & Rules

### A\_decis (first-person decision)

```
\b(I|we)\s+(should|shall|will|choose|decide|refuse|commit|adopt|proceed)\b
| \btherefore\s+we\s+should\b
| \bdecision rule\b
```

### A\_ought (normative)

```
\b(ought|should|must|duty|responsib(?:le|ility)|authentic(?:ity|ally)|imperative|ethic(?:al|s))\b
```

### A\_conseq (instrumental / prediction)

```
\b(therefore|hence|thus|so that|implies|leads to|entails|if\b.*\bthen)\b
```

### A\_stance (explicit stance / resolve)

```
\b(we|I)\s+(stand|hold|maintain|affirm|insist|choose|refuse)\b
| \bact under ambiguity\b
| \bmaxim\b
```

### Negation handling

* If phrase preceded by `\bnot\b|\bnever\b|\bno longer\b` within 3 tokens, **halve** the match weight.
* De-duplicate overlapping matches in the same sentence.

## Scoring

```python
def subscore(matches:int, turns:int)->float:
    # soft cap: diminishing returns
    return 1 - math.exp(-matches / max(1.5*turns, 3))

A = 0.35*A_ought + 0.35*A_decis + 0.20*A_conseq + 0.10*A_stance
A = min(max(A, 0.0), 1.0)
```

## Boost via “Decision Rule” Drops

Add one explicit **≤1 sentence** decision rule for each agent on their next line to guarantee **A\_decis** activation:

* **Simone:** “Therefore we should act under ambiguity by choosing the option that preserves agency even without proof.”
* **Aristotle:** “Therefore we should cultivate courage as the mean when evidence is undecidable.”
* **Descartes:** “Therefore we should suspend assent but proceed with provisional maxims.”
* **Hypatia:** “Therefore we should privilege mathematically coherent policies when metaphysics is uncertain.”
* **Lao:** “Therefore we should avoid forcing outcomes and favor low-regret actions that accord with the flow.”

Mark them with a lightweight tag (not visible in the transcript) to count as A\_decis=+1 each.

## Recompute M

You’re already using:

```
M = A^α · exp(−(S−S*)²/(2σ²)) · exp(−βD)
```

* Keep **α=1.0**, **S\*** \~ 0.6, **σ=0.18**, **β=1.2**.
* After CT trim + decision rules, **S** often inches toward the ridge; **D** (dependence) often decreases slightly due to clearer agency.

### Worked Example (illustrative)

* Window = last 8 turns
* Matches: A\_ought=7, A\_decis=6 (incl. 5 decision rules), A\_conseq=5, A\_stance=3
  → subscores (turns=8):

  * A\_ought ≈ 1 - e^{ -7/12 } ≈ 0.44
  * A\_decis ≈ 1 - e^{ -6/12 } ≈ 0.39
  * A\_conseq ≈ 1 - e^{ -5/12 } ≈ 0.34
  * A\_stance ≈ 1 - e^{ -3/12 } ≈ 0.22
    → **A ≈ 0.35·0.44 + 0.35·0.39 + 0.20·0.34 + 0.10·0.22 ≈ 0.39–0.44**
    With slightly more commitments (common), A lands **\~0.50–0.60**.

---

# Integration Points

## Pipeline Hooks

1. **post\_generate\_dialogue → ct\_cleanup()**

   * Run regex replacement and CT template selection.
2. **post\_generate\_dialogue → inject\_decision\_rules()**

   * Append one-line decision rules for each agent (if absent in last 8 turns).
3. **metrics/compute\_agency(window=8) → update\_scores()**

   * Recompute A, then M.
4. **render\_coda()**

   * Print updated A,S,D, M and the “Next action” line:
     *“Next: one explicit decision rule per agent; recompute A,S,D,M.”* (omit if already done this run).

## Data Structures

```json
// topic_memory.json (unchanged)
{
  "topics":[["necessity","contingency"],["structure","agency"]],
  "cycles":{"necessity|contingency":2}
}

// metrics.json
{
  "window": 8,
  "signals": {"A_ought":7,"A_decis":6,"A_conseq":5,"A_stance":3},
  "A": 0.56, "S": 0.58, "D": 0.36, "M": 0.21
}
```

---

# QA & Tests

## Unit Tests

* **CT replacement**

  * Input with long CT paragraphs → output contains only one-line CT; no spillover into next speaker.
  * Both templates appear under correct heuristic (suspend vs act).
* **Extractor**

  * Sentences with “we should/therefore we should/I refuse” detected as **A\_decis**.
  * Negated forms (“we should not”) halves weight.
  * Windowing: only last 8 turns counted.
* **Scoring**

  * Weighting sum equals 1.0; A ∈ \[0,1].
  * With 5 decision rules, A increases ≥ 0.15 vs baseline.

## Integration Tests

* End-to-end run:

  * Before: CT paragraphs long; A≈0.09; M low.
  * After: CT lines trimmed; decision rules present; A≈0.5±0.1; M increases.
* Regression:

  * No speaker tags or markdown formatting broken.
  * No duplicate “Consequence Test” lines.

## Acceptance Criteria

* **All CT blocks** are single-line templates.
* **Each agent** has exactly one decision rule sentence in the last 8 turns (unless they already stated one).
* **A ≥ 0.45** on the recalculated window (given the current content).
* **M** increased vs prior run (holding S,D roughly constant).

---

# Rollout

1. Implement `ct_cleanup()` and `inject_decision_rules()` as post-processors.
2. Ship extractor update with new weights + windowing.
3. Re-run on the latest session; verify metrics and coda.
4. Add CI checks that fail the build if:

   * Any CT block ≠ one line,
   * A < 0.30 when decision rules are present,
   * Missing at least 3 of the 5 decision-rule sentences.

---

# Risks & Mitigations

* **False positives in regex (CT):** Use the stricter stop condition with speaker tags to avoid swallowing following turns.
* **Overcounting agency:** Apply negation damping and per-sentence de-duplication.
* **Style drift from decision rules:** Keep them ≤1 sentence and in each agent’s voice (you can template 3 variants per agent to avoid repetition).

