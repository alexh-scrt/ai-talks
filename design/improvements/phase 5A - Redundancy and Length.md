**plug-and-play plan** to cut redundancy and control length without losing depth.

# Goals

1. Cap repetitive back-and-forths.
2. Force **new entailments** (implications, examples, or decisions) each turn.
3. Keep the show tight with auto-pivots and compressive syntheses.

---

# Policies (ready to adopt)

## A. Turn budget per dyad

* **Rule:** Any two agents can volley at most **2 rounds** (A→B→A→B).
* **After budget is spent:** The Host must either (a) call on a **new agent** or (b) invoke **Voice of Reason** to summarize and pivot.

## B. New-entailment requirement

Every turn must add at least one of:

* **Implication:** “If X, then Y for {ethics/free will/knowledge}.”
* **Application:** “In case Z, we should…”
* **Counterexample or concession**
* **Operational test/criterion**

If none is present, the system re-prompts the agent:

> “Revise by adding a **new entailment** (implication, application, counterexample, or test).”

## C. Topic rotation & pivot triggers

* If the current **tension pair** (e.g., necessity vs contingency) exceeds **2 cycles** without new entailments → **forced pivot**.
* Pivot options: introduce a **dilemma**, a **retrieved anchor**, or a **different tension pair**.

## D. Synthesis cadence

Every **12 turns**: Voice of Reason must deliver a **≤3-sentence synthesis + next step**.

---

# Data structures

```python
class Turn:
    speaker: str
    text: str
    claims: list[str]
    entailments: list[str]  # auto-detected tags: implication|application|counterexample|test
    topics: set[str]        # extracted: 'necessity','contingency','agency','structure', etc.

class DyadState:
    pair: tuple[str,str]        # ('Descartes','Simone')
    volleys_used: int           # 0..2

class TensionState:
    pair: tuple[str,str]        # ('necessity','contingency')
    cycles: int                 # increments when both sides referenced in last 2 turns
    last_new_entailment_turn: int

class SessionState:
    dyads: dict[tuple,str] -> DyadState
    tensions: dict[tuple,str] -> TensionState
    turn_count: int
```

---

# Novelty & redundancy checks

## 1) Semantic similarity guard

* Compute cosine similarity of current draft vs last 3 turns (**SBERT** or equivalent).
* If **sim ≥ 0.85**, mark as “likely repetition”.

## 2) Entailment detector (cheap heuristic)

Look for patterns:

* Implication: “if”, “therefore”, “so that”, “entails”, “means that”
* Application: “in practice”, “for example”, “consider”, “therefore we should”
* Counterexample: “unless”, “except when”, “counterexample”, “not if”
* Test/criterion: “we could test”, “criterion”, “measure”, “observable”

If none found → re-prompt.

## 3) Claim-graph increment

* Extract propositions (simple triples or key sentences).
* **New node or new edge?** If not, penalize the candidate and prefer a turn that adds one.

---

# Control loop (pseudo-code)

```python
def propose_turn(agent, context):
    draft = agent.generate(context)

    if is_redundant(draft, context.last_turns):              # sim check
        draft = agent.revise(draft, instruction="Avoid repetition. Add a new entailment.")

    entailments = detect_entailments(draft)
    if not entailments:
        draft = agent.revise(draft, instruction="Add at least one new entailment: implication, application, counterexample, or test.")

    if not adds_to_claim_graph(draft, context.claim_graph):
        draft = agent.revise(draft, instruction="Introduce a new claim, consequence, or criterion not yet stated.")

    return finalize(draft)
```

---

# Host/Moderator prompts (drop-in)

**After 2 volleys in a dyad**

> “We’ve done two rounds on {TENSION}. One **new entailment** or we **pivot**. {Next agent}, show a consequence or a test.”

**Forced pivot**

> “We’ve circled the same tension. Here’s a concrete case: *Should we unplug a suffering NPC?* Each of you: **one sentence**, with a consequence.”

**Synthesis checkpoint (every 12 turns)**

> “Synthesis: (1) what advanced? (2) one actionable implication. **Next**: evaluate against {anchor/dilemma}.”

---

# Config (YAML)

```yaml
limits:
  dyad_max_volleys: 2
  synthesis_interval: 12
  max_total_turns: 48

novelty:
  similarity_threshold: 0.85
  require_entailment: true
  claim_graph_required: true

entailment_types:
  - implication
  - application
  - counterexample
  - test

pivots:
  on_tension_cycles: 2
  inject_dilemma: true
  inject_retrieved_anchor: true
```

---

# Acceptance tests (quick)

1. **Dyad budget**: Simulate A↔B for 3 volleys → verify 3rd is blocked and pivot fires.
2. **Entailment enforcement**: Feed a paraphrase of prior turn → verify re-prompt and final output includes “If X then Y…”
3. **Synthesis cadence**: At turn 12 → Voice of Reason appears with ≤3 sentences and a next step.
4. **Compression metric**: `unique_concepts/total_tokens ≥ 0.25` over the run.
5. **Length cap**: `max_total_turns` respected; ending summary generated.

---

# Editor’s checklist (run-time)

* [ ] No dyad exceeds **2 volleys**.
* [ ] Every turn tagged with **≥1 entailment**.
* [ ] Every 12 turns → synthesis + next step.
* [ ] At least one **dilemma or retrieved anchor** per act.
* [ ] Final output ≤ configured **max\_total\_turns**.

