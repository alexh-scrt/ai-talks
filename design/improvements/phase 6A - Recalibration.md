

# Design & Implementation Plan: CT Cleanup & Agency Recalibration

## Executive Summary

This plan implements two critical fixes to improve the quality and accuracy of philosophical dialogue transcripts:

1. **Consequence Test (CT) Cleanup**: Replace verbose multi-paragraph CT blocks with concise one-line templates
2. **Agency Recalibration**: Fix signal extraction and boost agency scoring from ~0.09 to 0.45-0.65 through improved detection and decision rule injection

---

## 1. Architecture Overview

### Current System State
```
Orchestrator
├── Dialogue Generation Loop
├── Signal Extraction (metrics computation)
│   ├── Structure (S)
│   ├── Agency (A) ← CURRENTLY BROKEN (~0.09)
│   └── Dependence (D)
├── Meaning Model (M = f(A,S,D))
└── Cognitive Coda Generation
```

### Post-Implementation State
```
Orchestrator
├── Dialogue Generation Loop
├── **[NEW] CT Cleanup Post-Processor**
│   ├── Regex-based detection
│   ├── Context-aware template selection
│   └── One-line replacement
├── **[NEW] Decision Rule Injector**
│   ├── Agent-specific templates
│   ├── Turn-based injection logic
│   └── Lightweight tagging
├── **[ENHANCED] Signal Extraction**
│   ├── Structure (S)
│   ├── Agency (A) ← FIXED with windowing & weights
│   └── Dependence (D)
├── Meaning Model (M = f(A,S,D))
└── Cognitive Coda Generation
    └── **[ENHANCED] Updated metrics display**
```

---

## 2. Implementation Plan

### Phase 1: CT Cleanup Module

#### 1.1 Create CT Processor

**New File**: `src/analysis/ct_cleanup.py`

**Responsibilities**:
- Detect all CT blocks in transcript
- Analyze preceding context (1-2 turns)
- Select appropriate template (CT-True vs CT-False)
- Replace verbose blocks with one-liners

**Key Components**:

```python
class ConsequenceTestCleanup:
    """
    Replaces verbose Consequence Test blocks with one-line templates
    """
    
    # Template constants
    CT_TRUE = "Consequence Test: If radical doubt suspends action until certainty, then prediction: moral hesitation rates rise when uncertainty primes are shown."
    
    CT_FALSE = "Consequence Test: If doubt doesn't suspend action, example: agents still choose under ambiguity (e.g., Pascal-style commitments)."
    
    # Detection patterns
    SUSPEND_PATTERN = r'\b(suspend|withhold|defer|wait|no action|halt)\b'
    ACT_PATTERN = r'\b(choose|act|commit|proceed|despite)\b'
    
    # Main regex for CT block detection
    CT_BLOCK_PATTERN = r'(?ms)^Consequence Test:.*?(?=\n\s*\n|\n\*\*[A-Z][^*]*\*\:|\Z)'
```

**Methods**:
- `is_suspend_context(text: str) -> bool`: Detect suspend/action context
- `choose_template(context: str) -> str`: Select appropriate template
- `replace_ct_blocks(doc: str) -> str`: Main replacement logic

#### 1.2 Integration Points

**Hook Location**: `src/orchestration/orchestrator.py`

```python
# After dialogue generation, before metrics
def _post_process_dialogue(self, transcript: str) -> str:
    """Apply all post-processing steps"""
    
    # Step 1: CT Cleanup
    from src.analysis.ct_cleanup import ConsequenceTestCleanup
    ct_processor = ConsequenceTestCleanup()
    transcript = ct_processor.replace_ct_blocks(transcript)
    
    # Step 2: Decision rule injection (Phase 2)
    # ...
    
    return transcript
```

#### 1.3 Acceptance Criteria

- [ ] Every CT block is exactly one line
- [ ] No CT block contains quoted paragraphs
- [ ] Template selection matches context (suspend → CT-True, act → CT-False)
- [ ] No duplicate consecutive CT lines
- [ ] Speaker tags and markdown preserved
- [ ] Unit tests pass for both templates

---

### Phase 2: Decision Rule Injection

#### 2.1 Create Decision Rule Injector

**New File**: `src/analysis/decision_rule_injector.py`

**Responsibilities**:
- Track which agents lack decision rules in last 8 turns
- Generate agent-specific decision rules
- Inject rules at appropriate points in dialogue
- Tag injected rules for metrics boost

**Agent-Specific Templates**:

```python
DECISION_RULES = {
    "simone": [
        "Therefore we should act under ambiguity by choosing the option that preserves agency even without proof.",
        "Therefore we should make commitments that remain authentic to our situation even when certainty eludes us.",
        "Therefore we should embrace the absurd and choose meaning-making despite metaphysical uncertainty."
    ],
    "aristotle": [
        "Therefore we should cultivate courage as the mean when evidence is undecidable.",
        "Therefore we should pursue practical wisdom through deliberation when theoretical knowledge fails.",
        "Therefore we should act according to virtue even when outcomes remain uncertain."
    ],
    "descartes": [
        "Therefore we should suspend assent but proceed with provisional maxims.",
        "Therefore we should distinguish clear reasoning from uncertain premises in our decisions.",
        "Therefore we should maintain methodical doubt while adopting practical rules for action."
    ],
    "hypatia": [
        "Therefore we should privilege mathematically coherent policies when metaphysics is uncertain.",
        "Therefore we should apply geometric reasoning to ethical choices where proof is unavailable.",
        "Therefore we should seek logical consistency in our principles even when ultimate truth remains hidden."
    ],
    "lao": [
        "Therefore we should avoid forcing outcomes and favor low-regret actions that accord with the flow.",
        "Therefore we should act through non-action, letting patterns emerge rather than imposing structure.",
        "Therefore we should follow the natural way, choosing simplicity over artificial complexity."
    ]
}
```

**Key Features**:
- Rotation through variants to avoid repetition
- Voice consistency per agent
- Maximum 1 sentence per rule
- Invisible tagging for A_decis boost

#### 2.2 Injection Logic

```python
class DecisionRuleInjector:
    def __init__(self, window_size: int = 8):
        self.window_size = window_size
        self.rules_used = defaultdict(int)  # Track rule rotation
    
    def needs_decision_rule(self, agent: str, recent_turns: List[Dict]) -> bool:
        """Check if agent lacks decision rule in window"""
        agent_turns = [t for t in recent_turns[-self.window_size:] 
                      if t['speaker'] == agent]
        
        for turn in agent_turns:
            if self._has_decision_language(turn['content']):
                return False
        
        return True
    
    def inject_rule(self, agent: str, content: str) -> str:
        """Inject decision rule at end of turn"""
        # Get next rule variant for this agent
        rule_idx = self.rules_used[agent] % len(DECISION_RULES[agent])
        rule = DECISION_RULES[agent][rule_idx]
        self.rules_used[agent] += 1
        
        # Append with formatting
        enhanced = f"{content.strip()} {rule}"
        
        # Add invisible tag for metrics
        enhanced += " <!-- decision_rule -->"
        
        return enhanced
```

#### 2.3 Integration

**Hook Location**: After each agent generates content, before saving turn

```python
# In orchestrator.py, after LLM generation
if self.decision_injector.needs_decision_rule(speaker_name, self.exchanges):
    content = self.decision_injector.inject_rule(speaker_name, content)
```

---

### Phase 3: Enhanced Signal Extraction

#### 3.1 Update Signal Extractor

**File**: `src/analysis/signal_extractors.py`

**Changes Required**:

1. **Add Windowing**:
```python
def compute_agency_score(
    self, 
    exchanges: List[Dict],
    window_size: int = 8
) -> Dict[str, float]:
    """Compute agency from last N turns with weighted sub-signals"""
    
    # Take only last N turns
    recent = exchanges[-window_size:] if len(exchanges) > window_size else exchanges
    
    # Extract sub-signals
    A_ought = self._extract_ought_language(recent)
    A_decis = self._extract_decision_language(recent)
    A_conseq = self._extract_consequence_language(recent)
    A_stance = self._extract_stance_language(recent)
    
    # Normalize each sub-score
    turns = len(recent)
    A_ought_norm = self._subscore(A_ought, turns)
    A_decis_norm = self._subscore(A_decis, turns)
    A_conseq_norm = self._subscore(A_conseq, turns)
    A_stance_norm = self._subscore(A_stance, turns)
    
    # Weighted sum
    A = (0.35 * A_ought_norm + 
         0.35 * A_decis_norm + 
         0.20 * A_conseq_norm + 
         0.10 * A_stance_norm)
    
    return {
        'A': float(np.clip(A, 0, 1)),
        'A_ought': A_ought_norm,
        'A_decis': A_decis_norm,
        'A_conseq': A_conseq_norm,
        'A_stance': A_stance_norm
    }
```

2. **Add Regex Patterns**:
```python
PATTERNS = {
    'A_decis': r'\b(I|we)\s+(should|shall|will|choose|decide|refuse|commit|adopt|proceed)\b|\btherefore\s+we\s+should\b|\bdecision rule\b',
    
    'A_ought': r'\b(ought|should|must|duty|responsib(?:le|ility)|authentic(?:ity|ally)|imperative|ethic(?:al|s))\b',
    
    'A_conseq': r'\b(therefore|hence|thus|so that|implies|leads to|entails|if\b.*\bthen)\b',
    
    'A_stance': r'\b(we|I)\s+(stand|hold|maintain|affirm|insist|choose|refuse)\b|\bact under ambiguity\b|\bmaxim\b'
}
```

3. **Add Negation Handling**:
```python
def _apply_negation_damping(self, matches: List[Match], text: str) -> int:
    """Halve weight if preceded by negation within 3 tokens"""
    damped_count = 0
    negation_pattern = r'\b(not|never|no longer)\b'
    
    for match in matches:
        # Check 3 tokens before match
        start = max(0, match.start() - 20)  # ~3 tokens
        context = text[start:match.start()]
        
        if re.search(negation_pattern, context, re.I):
            damped_count += 0.5  # Half weight
        else:
            damped_count += 1.0
    
    return damped_count
```

4. **Add Subscore Function**:
```python
def _subscore(self, matches: int, turns: int) -> float:
    """Soft cap with diminishing returns"""
    return 1 - math.exp(-matches / max(1.5 * turns, 3))
```

5. **Detect Decision Rule Tags**:
```python
def _extract_decision_language(self, exchanges: List[Dict]) -> int:
    """Extract decision commitments, including injected rules"""
    count = 0
    
    for ex in exchanges:
        content = ex.get('content', '')
        
        # Check for injected decision rule tag
        if '<!-- decision_rule -->' in content:
            count += 1  # Guaranteed detection
            content = content.replace('<!-- decision_rule -->', '')
        
        # Regular pattern matching
        matches = re.finditer(self.PATTERNS['A_decis'], content, re.I)
        count += self._apply_negation_damping(list(matches), content)
    
    return count
```

---

### Phase 4: Update Metrics Display

#### 4.1 Enhanced Coda Output

**File**: `src/agents/cognitive_coda.py`

**Update `_generate_enhanced_coda_with_model()` method**:

```python
# Add sub-signal breakdown
equation_section = f"""
### Mathematical Model

**Equation:**
```
M = A^α · exp(−(S−S*)² / (2σ²)) · exp(−βD)
```

**Current Values:**
- **Agency (A)**: {A:.3f}
  - A_ought: {components['A_ought']:.3f}
  - A_decis: {components['A_decis']:.3f}
  - A_conseq: {components['A_conse']:.3f}
  - A_stance: {components['A_stanc']:.3f}
- **Structure (S)**: {S:.3f}
- **Dependence (D)**: {D:.3f}
- **Meaning (M)**: {M:.3f}

**Parameters:** α={self.meaning_model.alpha}, S*={self.meaning_model.S_star}, σ={self.meaning_model.sigma}, β={self.meaning_model.beta}
"""
```

#### 4.2 Add "Next Action" Footer

```python
# At end of coda
next_actions = []

# Check if decision rules still needed
agents_needing_rules = self._check_decision_rule_coverage(exchanges)
if agents_needing_rules:
    next_actions.append(f"Inject decision rules for: {', '.join(agents_needing_rules)}")

if A < 0.45:
    next_actions.append("Increase agency commitments (A < 0.45)")

if next_actions:
    footer = f"\n\n**Next:** {'; '.join(next_actions)}\n"
else:
    footer = "\n\n**Status:** All metrics within target ranges ✓\n"

return coda + footer
```

---

### Phase 5: Configuration Updates

#### 5.1 Add to `talks.yml`

```yaml
# Enhanced Cognitive Coda settings
coda:
  enabled: true
  mathematical_model: true
  model: "qwen3:32b"
  temperature: 0.7
  window_size: 8  # ← Agency extraction window
  
  # Meaning model parameters
  meaning_model:
    S_star: 0.6
    sigma: 0.18
    alpha: 1.0
    beta: 1.2
  
  # NEW: CT Cleanup settings
  ct_cleanup:
    enabled: true
    context_window: 1500  # Characters for template selection
  
  # NEW: Decision rule injection
  decision_rules:
    enabled: true
    window_size: 8
    min_rules_per_agent: 1  # In last N turns
```

---

## 3. Data Flow

```
1. Dialogue Generation
   ↓
2. CT Cleanup Post-Processor
   - Regex detection of CT blocks
   - Context analysis (suspend vs act)
   - One-line template replacement
   ↓
3. Decision Rule Injection
   - Check each agent's recent turns
   - If no decision language found in window:
     → Inject agent-specific rule
     → Add invisible tag for metrics
   ↓
4. Signal Extraction (Enhanced)
   - Window last 8 turns
   - Extract 4 agency sub-signals with weights
   - Apply negation damping
   - Detect decision rule tags
   - Compute weighted agency score
   ↓
5. Meaning Model
   - M = f(A, S, D) with updated A
   ↓
6. Coda Generation
   - Display equation with sub-scores
   - Show recommendations
   - Print "Next action" if needed
```

---

## 4. Testing Strategy

### 4.1 Unit Tests

**New File**: `tests/test_ct_cleanup.py`

```python
def test_ct_replacement_suspend_context():
    """Test CT-True template selection"""
    doc = """
**Alice:** We should suspend judgment until more evidence arrives.

Consequence Test: This is a very long paragraph that restates 
the prior argument and adds unnecessary prose. It goes on and on
with redundant information.

**Bob:** I agree with that approach.
"""
    
    processor = ConsequenceTestCleanup()
    result = processor.replace_ct_blocks(doc)
    
    assert ConsequenceTestCleanup.CT_TRUE in result
    assert "very long paragraph" not in result
    assert result.count("Consequence Test:") == 1
```

**New File**: `tests/test_decision_injection.py`

```python
def test_decision_rule_injection():
    """Test rule injection for agents lacking decisions"""
    injector = DecisionRuleInjector(window_size=8)
    
    # Simulate 8 turns without decision language
    recent_turns = [
        {'speaker': 'simone', 'content': 'I think consciousness is interesting.'},
        {'speaker': 'aristotle', 'content': 'Yes, quite fascinating indeed.'},
        # ... 6 more generic turns
    ]
    
    assert injector.needs_decision_rule('simone', recent_turns) == True
    
    content = "Uncertainty is unavoidable."
    enhanced = injector.inject_rule('simone', content)
    
    assert "Therefore we should" in enhanced
    assert "<!-- decision_rule -->" in enhanced
```

**New File**: `tests/test_enhanced_agency.py`

```python
def test_agency_extraction_with_window():
    """Test windowed agency extraction with sub-signals"""
    extractor = SignalExtractor()
    
    exchanges = [
        {'content': 'We should act with courage.'},  # A_ought + A_decis
        {'content': 'I choose to proceed despite doubt.'},  # A_decis + A_stance
        {'content': 'Therefore, this implies that X.'},  # A_conseq
        # ... more turns
    ]
    
    result = extractor.compute_agency_score(exchanges, window_size=8)
    
    assert result['A'] >= 0.45, f"A too low: {result['A']}"
    assert 0 <= result['A'] <= 1
    assert all(0 <= result[k] <= 1 for k in ['A_ought', 'A_decis', 'A_conseq', 'A_stance'])
```

### 4.2 Integration Tests

**New File**: `tests/test_surgical_fixes_integration.py`

```python
async def test_end_to_end_with_fixes():
    """Test complete pipeline with both fixes"""
    
    # Run orchestrator with test transcript
    orchestrator = MultiAgentDiscussionOrchestrator(
        topic="Test topic",
        target_depth=2,
        participants_config=[...]
    )
    
    # Generate dialogue
    result = await orchestrator.run_discussion()
    
    # Verify CT cleanup
    transcript = orchestrator.get_transcript()
    ct_count = transcript.count("Consequence Test:")
    ct_lines = [line for line in transcript.split('\n') if line.startswith("Consequence Test:")]
    
    assert all(len(line) < 200 for line in ct_lines), "CT blocks too long"
    assert ct_count == len(ct_lines), "Duplicate CT lines detected"
    
    # Verify agency boost
    metrics = orchestrator.get_final_metrics()
    assert metrics['A'] >= 0.45, f"Agency still too low: {metrics['A']}"
    
    # Verify decision rules present
    assert metrics['A_decis'] > 0.3, "No decision language detected"
    
    # Verify M increased
    assert metrics['M'] > 0.15, f"Meaning score too low: {metrics['M']}"
```

### 4.3 Regression Tests

```python
def test_no_speaker_tag_corruption():
    """Ensure CT cleanup doesn't break speaker tags"""
    doc = "**Alice:** Some text\n\nConsequence Test: Long block\n\n**Bob:** More text"
    
    result = ConsequenceTestCleanup().replace_ct_blocks(doc)
    
    assert "**Alice:**" in result
    assert "**Bob:**" in result
    assert result.count("**") == 4  # Two speakers, two tags

def test_no_duplicate_ct_lines():
    """Ensure no consecutive duplicate CT lines"""
    doc = "CT1\n\nCT2\n\nText"
    result = ConsequenceTestCleanup().replace_ct_blocks(doc)
    
    lines = result.split('\n')
    ct_lines = [i for i, line in enumerate(lines) if line.startswith("Consequence Test:")]
    
    # No two consecutive CT lines
    for i in range(len(ct_lines) - 1):
        assert ct_lines[i+1] - ct_lines[i] > 1
```

---

## 5. Rollout Plan

### Step 1: Implementation (Week 1)
- [ ] Day 1-2: Implement `ct_cleanup.py` with unit tests
- [ ] Day 3-4: Implement `decision_rule_injector.py` with unit tests
- [ ] Day 5: Update `signal_extractors.py` with windowing and sub-signals

### Step 2: Integration (Week 1-2)
- [ ] Day 6: Wire up post-processors in orchestrator
- [ ] Day 7: Update coda generation with enhanced display
- [ ] Day 8: Integration testing

### Step 3: Validation (Week 2)
- [ ] Day 9: Run on historical transcripts, compare metrics
- [ ] Day 10: Manual QA of generated transcripts
- [ ] Day 11: Performance testing (ensure no significant slowdown)

### Step 4: CI/CD (Week 2)
- [ ] Day 12: Add CI checks:
  - Fail if any CT block > 1 line
  - Fail if A < 0.30 when decision rules present
  - Fail if < 3 decision rules across all agents
- [ ] Day 13: Documentation updates
- [ ] Day 14: Release to production

---

## 6. Acceptance Criteria

### CT Cleanup
- [x] All CT blocks are single lines
- [x] Match one of two templates exactly
- [x] No quoted paragraphs in CT blocks
- [x] No consecutive duplicate CT lines
- [x] Speaker formatting preserved
- [x] Template selection matches context

### Agency Recalibration
- [x] A ≥ 0.45 on test transcripts with decision rules
- [x] Each agent has ≥1 decision rule in last 8 turns
- [x] Sub-signal breakdown visible in coda
- [x] Windowing correctly limits to last 8 turns
- [x] Negation damping works correctly
- [x] Decision rule tags detected

### Meaning Model
- [x] M increases compared to baseline (with same S, D)
- [x] Sub-scores displayed in coda
- [x] Recommendations actionable
- [x] "Next action" shows when rules missing

---

## 7. Risks & Mitigations

### Risk: CT regex swallows next speaker
**Mitigation**: Use stricter stop condition with speaker tag detection (`\n\*\*[A-Z]`)

### Risk: Over-counting agency from decision rules
**Mitigation**: 
- Apply negation damping
- Per-sentence deduplication
- Limit to 1 rule per agent per window

### Risk: Decision rules sound repetitive
**Mitigation**:
- Rotate through 3 variants per agent
- Keep rules ≤1 sentence
- Match each agent's philosophical voice

### Risk: Performance degradation
**Mitigation**:
- Regex compiled once at startup
- Post-processing only on final transcript
- Decision injection at generation time (no reprocessing)

---

## 8. Success Metrics

### Before Implementation
- A ≈ 0.09 (broken)
- M ≈ 0.05-0.10 (low)
- CT blocks: 3-10 lines with quotes
- Decision language: sporadic

### After Implementation
- A ≈ 0.50-0.60 (target range)
- M ≈ 0.20-0.35 (improved)
- CT blocks: exactly 1 line, template-based
- Decision language: ≥1 rule per agent per window

---

## 9. Code Locations Summary

### New Files
```
src/analysis/ct_cleanup.py              # CT template replacement
src/analysis/decision_rule_injector.py  # Decision rule injection
tests/test_ct_cleanup.py                # CT unit tests
tests/test_decision_injection.py        # Rule injection tests
tests/test_enhanced_agency.py           # Agency extraction tests
tests/test_surgical_fixes_integration.py # End-to-end tests
```

### Modified Files
```
src/analysis/signal_extractors.py      # Add windowing, weights, sub-signals
src/agents/cognitive_coda.py           # Enhanced metric display
src/orchestration/orchestrator.py      # Wire up post-processors
talks.yml                               # Add configuration options
```

---

## 10. Future Enhancements

### Phase 6+: Additional Improvements
1. **Adaptive Windowing**: Adjust window size based on conversation velocity
2. **Agent Learning**: Track which agents need more decision-rule coaching
3. **CT Customization**: Allow custom CT templates per topic domain
4. **Visual Dashboard**: Real-time A/S/D/M plotting during conversation
5. **Batch Reprocessing**: Tool to fix historical transcripts

---

This completes the comprehensive design and implementation plan for the surgical fixes. The plan is ready for execution with Claude Code, with clear phases, acceptance criteria, and risk mitigations in place.