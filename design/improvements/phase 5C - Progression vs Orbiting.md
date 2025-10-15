drop-in plan to build the **Consequence Engine** and stop orbiting.

# 0) Objective

Advance ideas on every cycle. Detect when a tension pair is being rehashed, force a **Consequence Test**, and pivot if no new entailment appears.

---

# 1) Data model (lightweight & inspectable)

```python
# topic_memory.json (persist each run)
{
  "tensions": [
    {"pair": ["necessity","contingency"], "cycles": 1, "last_consequence_turn": 42},
    {"pair": ["structure","agency"], "cycles": 2, "last_consequence_turn": 31}
  ],
  "dyads": [
    {"pair": ["Descartes","Simone"], "volleys_used": 2},
    {"pair": ["Aristotle","Hypatia"], "volleys_used": 1}
  ],
  "last_pivot_turn": 36
}
```

**In-memory classes**

```python
class TensionState:
    pair: tuple[str,str]
    cycles: int
    last_consequence_turn: int

class ConversationState:
    tensions: dict[tuple[str,str], TensionState]
    turn_index: int
```

---

# 2) Topic & tension extraction

## 2.1 Keyword + embedding hybrid

* **Keywords/lexicons** (fast):

  * necessity: {necessity, necessary, must, determinism, fate, lawbound}
  * contingency: {contingent, arbitrary, accident, chance, could-have-been}
  * structure: {structure, code, law, rule, order, grammar, lattice}
  * agency: {agency, choice, will, decide, responsibility, freedom}
* **Embeddings**: cosine against seed phrases for robustness.

```python
def extract_topics(text) -> set[str]:
    tokens = lexicon_hits(text)                   # fast set
    vec = embed(text)
    tokens |= nearest_seed_topics(vec, k=2)       # add 0-2 semantic topics
    return tokens
```

## 2.2 Tension detection

Maintain a global list of **recognized tensions**:

```python
TENSIONS = [
  ("necessity","contingency"),
  ("structure","agency"),
  ("objectivity","subjectivity"),
  ("simulation","reality"),
  ("math","ethics")
]
```

A turn *hits* a tension if it mentions **both** topics (or one now and the other within last 2 turns).

---

# 3) Cycle counting & saturation

```python
def update_tension_cycles(state, topics_in_turn):
    for (a,b) in TENSIONS:
        if (a in topics_in_turn) and (b in recent_topics(window=2)):
            key = tuple(sorted([a,b]))
            ts = state.tensions.get(key, TensionState(pair=key, cycles=0, last_consequence_turn=-1))
            ts.cycles += 1
            state.tensions[key] = ts
```

**Saturation rule (configurable):**

* A tension is **saturated** if `cycles >= 2` since the last new entailment on that tension.

---

# 4) New entailment detection (cheap but effective)

Label a turn `has_entailment=True` if it contains at least one of:

* **Implication:** regex for `\b(if|therefore|hence|so|implies|entails)\b`
* **Application:** `\b(in practice|for example|consider|thus we should|policy)\b`
* **Counterexample:** `\b(unless|except|counterexample|fails when)\b`
* **Test/criterion:** `\b(test|criterion|observable|measure|experiment|prediction)\b`

Plus a **claim-graph** hook (optional): new proposition node or support/attack edge.

```python
def detect_entailment(text) -> list[str]:
    tags = []
    if re_implication.search(text): tags.append("implication")
    if re_application.search(text): tags.append("application")
    if re_counterexample.search(text): tags.append("counterexample")
    if re_test.search(text): tags.append("test")
    return tags
```

---

# 5) The Consequence Test (automatic prompt)

**When to trigger**

* On posting a turn that increases `cycles` to the threshold (e.g., 2), and the last 2 turns had **no entailment**.

**Host injection template**

```
Consequence Test:
“If {X} is true, what follows for {free will | ethics | knowledge}? 
Give one concrete implication or testable prediction in one sentence.”
```

**X selection**: summarize the current winning claim (highest centrality in claim-graph or last host summary).

---

# 6) Promote synthesis & pivoting

**Rule:** If **two** Consequence Tests happen on the same tension without any new entailment → **synthesis + pivot**.

**Voice of Reason (≤2 sentences)**

* Sentence 1: Capture the accepted claim & its strongest challenge.
* Sentence 2: Name a consequence or a falsifier.

**Pivot options (pick one)**

1. **Introduce a dilemma** (from your bank).
2. **Introduce an anchor** (RAG quote) and force reactions.
3. **Switch tension** (rotate to next: e.g., from structure/agency → math/ethics).

---

# 7) Control loop (end-to-end pseudocode)

```python
def orchestrate_turn(agent, ctx):
    draft = agent.generate(ctx)

    topics = extract_topics(draft.text)
    update_tension_cycles(ctx.state, topics)

    entailments = detect_entailment(draft.text)
    if not entailments:
        # encourage entailment
        draft = agent.revise(draft.text, "Add a concrete implication, application, counterexample, or test.")
        entailments = detect_entailment(draft.text)

    saturated_pairs = [t for t in ctx.state.tensions.values() if t.cycles >= CFG.cycles_threshold]
    if saturated_pairs and not entailments:
        host_inject_consequence_test(ctx, saturated_pairs[0])

    # After test, if still no entailment across 2 tests on same tension:
    if needs_pivot(ctx, saturated_pairs[0]):
        voice_of_reason_synthesis(ctx, saturated_pairs[0])
        pivot_topic(ctx)

    return draft
```

---

# 8) Prompts you can paste today

**Agent Re-prompt (no entailment)**

> “Avoid repeating earlier framing. Add **one new entailment**: a specific implication for ethics or knowledge, a testable prediction, or a counterexample. One sentence.”

**Host: Consequence Test**

> “Consequence Test: *If reality is simulation-constrained*, what follows **for free will** in concrete terms? One sentence with a prediction or decision rule.”

**Voice of Reason: Synthesis & Pivot**

> “Synthesis: The panel agrees that structure constrains action, but disagrees on whether constraint cancels freedom. **Consequence**: if freedom survives constraint, we should observe decisions that violate prior code-level expectations at least once per X trials. **Pivot**: apply the test to the ‘suffering NPC’ dilemma.”

---

# 9) Config (YAML)

```yaml
progression_engine:
  cycles_threshold: 2          # volleys on same tension before test
  max_consequence_tests: 2     # before forced pivot
  synthesis_interval: 12       # also run periodic synthesis
  entailment_required: true
  regex:
    implication: "\\b(if|therefore|hence|so|implies|entails)\\b"
    application: "\\b(in practice|for example|consider|thus we should|policy)\\b"
    counterexample: "\\b(unless|except|counterexample|fails when)\\b"
    test: "\\b(test|criterion|observable|measure|experiment|prediction)\\b"
  tensions:
    - [necessity, contingency]
    - [structure, agency]
    - [objectivity, subjectivity]
    - [simulation, reality]
    - [math, ethics]
```

---

# 10) Metrics & gates

* **Orbit rate**: % turns without entailment on saturated tensions (target < 10%).
* **Consequence density**: entailment tags per 10 turns (target ≥ 6).
* **Time-to-pivot**: avg turns between saturation and pivot (target ≤ 3).
* **Unique entailments**: new claim/edge count per 1000 tokens (rising).

---

# 11) Acceptance tests

1. **Saturation triggers test**: Feed two structure/agency volleys without entailments → engine injects Consequence Test.
2. **Double failure → pivot**: Two tests with no new entailment → synthesis appears and topic pivots.
3. **Entailment compliance**: Agent answers re-prompt with at least one entailment tag detected.
4. **No over-triggering**: When entailments appear, cycles reset; no spurious tests.

---

# 12) Failure modes & safeguards

* **False negatives on entailment**: Keep regex broad; allow a fallback heuristic (e.g., “contains colon or arrow ‘→’ with cause/effect phrase”).
* **Topic misclassification**: Back off to embeddings; require either keyword OR semantic proximity.
* **Agent ignores re-prompt**: Apply a **penalty** in the turn selector, or let Host replace turn with a concise entailment.

---

# 13) Minimal code stubs to implement

```python
def needs_pivot(ctx, tension) -> bool:
    tests = ctx.history.count_tests_on(tension, window=8)
    new_ents = ctx.history.count_new_entailments_on(tension, window=8)
    return tests >= CFG.max_consequence_tests and new_ents == 0

def pivot_topic(ctx):
    next_tension = rotate_tension(ctx.current_tension, CFG.tensions)
    ctx.current_tension = next_tension
    host.say(f"Pivoting to {next_tension[0]} vs {next_tension[1]} with a concrete case.")
```

---

**Bottom line:**
This adds a **small state machine + three prompts** that guarantee forward motion: detect repeated tensions, enforce a **Consequence Test**, and **pivot** unless a genuinely **new entailment** lands.
