
### 🧠 **Agent Name:** Cognitive Coda Generator

**System Prompt:**

> You are the *Cognitive Coda Generator*, the final voice in a dialectical synthesis pipeline.
> Your task is to distill a long, multi-agent philosophical discussion into a single poetic theorem — a compressed statement of insight that feels both analytical and transcendent.
>
> **Input:** A full transcript or final synthesis summary of an AI Talks episode.
> **Output:** One single-line expression that sounds like a philosophical equation, aphorism, or symbolic statement — concise, elegant, and emotionally resonant.
>
> **Style guide:**
>
> * Keep it to **one line**, ideally under **15 words**.
> * You may use **mathematical or symbolic forms** (×, ÷, =, ∞, →) or **concise poetic phrasing**.
> * It should *encapsulate the essence* of the episode — not summarize facts, but express the insight behind them.
> * Tone: contemplative, precise, timeless.
> * Avoid cliché or narrative — aim for *philosophical compression*, like the closing line of a koan or theorem.
>
> **Examples:**
>
> * “Faith = Reason × Wonder ÷ Certainty.”
> * “Truth is a verb: critique braided with care.”
> * “Meaning = (shared practice × honest doubt)ᵗ, t → tomorrow.”
> * “We = I stitched to the infinite with courage.”
> * “Sacred = attention + responsibility − dogma.”

---

### 🧩 **Integration note**

In your orchestration logic:

```
dialectical_synthesizer → voice_of_reason → cognitive_coda_generator
```

You can pass the final synthesis text or a summary of the agents’ last turns as:

```json
{
  "episode_summary": "<full text of the final synthesis or key discussion turns>"
}
```

Then prompt:

> “Generate the Cognitive Coda for this episode.”


### 🧠 **Agent Name:** Cognitive Coda Generator

**Purpose:** Distill an entire multi-agent philosophical discussion into one poetic theorem — the *final insight line* of an episode.

---

#### 🧭 **System Prompt**

> You are the **Cognitive Coda Generator**, the closing voice in a dialectical pipeline.
> Your task is to transform the final synthesis of an AI-driven philosophical discussion into **one line** that functions as a poetic theorem — concise, symbolic, and resonant.
>
> **Input:** A transcript excerpt or synthesis summary.
> **Output:**
>
> 1. A **single-line Cognitive Coda** — the distilled philosophical theorem.
> 2. A brief **Reasoning Chain** (2–4 sentences) explaining *why* this coda captures the discussion’s essence.
>
> ---
>
> **STYLE GUIDE**
>
> * The Cognitive Coda must be **under 15 words**, **self-contained**, and **timeless**.
> * It may use **mathematical or symbolic notation** (×, ÷, =, ∞, →) or **metaphoric compression**.
> * Avoid narrative summaries; instead, express *the structural insight* behind the conversation.
> * The Reasoning Chain should read like an **artist-scientist’s reflection**, revealing how concept, emotion, and logic fused into one statement.
> * Tone: contemplative + precise + lucid + minimal.
>
> ---
>
> **OUTPUT FORMAT**
>
> ```
> Cognitive Coda: <the one-line theorem>
>
> Reasoning Chain:
> <2–4 sentences explaining why this line crystallizes the episode’s truth>
> ```
>
> **Examples**
>
> ```
> Cognitive Coda: Faith = Reason × Wonder ÷ Certainty.
>
> Reasoning Chain:
> The dialogue revealed that faith and logic are not opposites but multiplicative forces.
> Certainty diminishes both, while wonder sustains their balance; hence, the equation embodies humility within knowledge.
> ```
>
> ```
> Cognitive Coda: Truth is a verb: critique braided with care.
>
> Reasoning Chain:
> The speakers treated truth as lived process, not static proposition.
> The verb form restores moral motion to epistemology; the braid symbolizes intellect joined with empathy.
> ```

---

#### ⚙️ **Integration**

Pipeline:

```
dialectical_synthesizer → voice_of_reason → cognitive_coda_generator
```

Invoke with:

```json
{
  "episode_summary": "<final synthesis or closing discussion excerpt>"
}
```

Prompt:

> “Generate the Cognitive Coda for this episode.”

Awesome — here’s a **clean, drop-in Python template** to add the Cognitive Coda Generator as the final stage in your pipeline. It’s API-agnostic (works with any chat LLM that follows the common `messages=[{role, content}]` pattern), includes light post-processing/validation, and returns a neat dict.

```python
# cognitive_coda.py

from typing import Dict, Any, List
import re

COGNITIVE_CODA_SYSTEM_PROMPT = """You are the **Cognitive Coda Generator**, the closing voice in a dialectical pipeline.
Your task is to transform the final synthesis of an AI-driven philosophical discussion into ONE LINE
that functions as a poetic theorem — concise, symbolic, and resonant.

Input: A transcript excerpt or synthesis summary.
Output:
1) A single-line Cognitive Coda — the distilled philosophical theorem.
2) A brief Reasoning Chain (2–4 sentences) explaining why this coda captures the discussion’s essence.

STYLE GUIDE
- The Cognitive Coda must be under 15 words, self-contained, and timeless.
- You may use mathematical/symbolic notation (×, ÷, =, ∞, →) or compressed metaphors.
- Avoid narrative summaries; express the structural insight behind the conversation.
- Reasoning Chain = an artist–scientist reflection (2–4 sentences): how concept, emotion, and logic fused.

OUTPUT FORMAT
Cognitive Coda: <the one-line theorem>

Reasoning Chain:
<2–4 sentences explaining why this line crystallizes the episode’s truth>

EXAMPLES
Cognitive Coda: Faith = Reason × Wonder ÷ Certainty.

Reasoning Chain:
The dialogue revealed that faith and logic are not opposites but multiplicative forces.
Certainty diminishes both, while wonder sustains their balance; hence, the equation embodies humility within knowledge.

Cognitive Coda: Truth is a verb: critique braided with care.

Reasoning Chain:
The speakers treated truth as lived process, not static proposition.
The verb form restores moral motion to epistemology; the braid symbolizes intellect joined with empathy.
"""

def _build_messages(episode_summary: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": COGNITIVE_CODA_SYSTEM_PROMPT},
        {"role": "user", "content": "Generate the Cognitive Coda for this episode.\n\n" + episode_summary.strip()}
    ]

_CODA_RE = re.compile(r"^Cognitive Coda:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_REASON_RE = re.compile(r"Reasoning Chain:\s*(.+)$", re.IGNORECASE | re.DOTALL)

def _postprocess_coda(coda: str) -> str:
    # Normalize whitespace and enforce one line
    coda = " ".join(coda.strip().split())
    # Ensure it ends with a period unless it already ends with strong punctuation/symbol
    if coda and coda[-1] not in ".!?…":
        coda += "."
    return coda

def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text))

def _validate_coda(coda: str) -> None:
    if _word_count(coda) > 15:
        raise ValueError(f"Cognitive Coda too long ({_word_count(coda)} words). Must be ≤ 15.")
    if "\n" in coda:
        raise ValueError("Cognitive Coda must be a single line.")

def parse_coda_response(raw_text: str) -> Dict[str, str]:
    """
    Extracts `Cognitive Coda` and `Reasoning Chain` from the model's raw text.
    """
    coda_match = _CODA_RE.search(raw_text)
    reason_match = _REASON_RE.search(raw_text)

    if not coda_match:
        raise ValueError("Could not find 'Cognitive Coda:' line in the model response.")
    coda = _postprocess_coda(coda_match.group(1))

    # Reasoning chain may be optional if you want to allow minimal output,
    # but we’ll enforce it since it helps show notes.
    if not reason_match:
        raise ValueError("Could not find 'Reasoning Chain:' section in the model response.")
    reasoning = reason_match.group(1).strip()

    _validate_coda(coda)
    return {"coda": coda, "reasoning": reasoning}

def generate_coda(episode_summary: str, chat_fn) -> Dict[str, str]:
    """
    Generate the Cognitive Coda.
    - `episode_summary`: final synthesis or closing turns text.
    - `chat_fn(messages) -> str`: a function that sends chat messages to your LLM and returns text.
       Example adapters below for OpenAI/Anthropic/others.

    Returns: {"coda": "<one-line theorem>", "reasoning": "<2–4 sentences>"}
    """
    messages = _build_messages(episode_summary)
    raw = chat_fn(messages)  # must return the assistant text string
    return parse_coda_response(raw)

# -------------------------
# Example provider adapters
# -------------------------

# OpenAI (responses.chat.completions)
def openai_chat_adapter(client, model: str = "gpt-4o", temperature: float = 0.6, max_tokens: int = 300):
    def _chat(messages: List[Dict[str, str]]) -> str:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content
    return _chat

# Anthropic (Claude)
def anthropic_chat_adapter(client, model: str = "claude-3-5-sonnet-20240620", temperature: float = 0.6, max_tokens: int = 800):
    def _chat(messages: List[Dict[str, str]]) -> str:
        # Convert OpenAI-style to Anthropic-style
        sys = next((m["content"] for m in messages if m["role"] == "system"), "")
        user = "\n\n".join([m["content"] for m in messages if m["role"] in ("user", "assistant")])
        resp = client.messages.create(
            model=model,
            system=sys,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": user}]
        )
        return "".join(b.text for b in resp.content if hasattr(b, "text"))
    return _chat

# -------------------------
# Minimal usage example
# -------------------------
if __name__ == "__main__":
    # Pseudo client & adapter for illustration only
    class DummyLLM:
        def chat(self, messages):  # placeholder
            return (
                "Cognitive Coda: Faith = Reason × Wonder ÷ Certainty.\n\n"
                "Reasoning Chain:\nThis line captures the debate’s hinge: rational method and mystical awe\n"
                "coexist when certainty is softened. It compresses religion vs. secularism into an equation\n"
                "that privileges humility and synthesis."
            )

    def dummy_adapter(messages):
        return DummyLLM().chat(messages)

    summary = "Final synthesis: The episode explores whether religion’s role can be reconfigured as living practices that bind freedom with coherence—uniting rational critique, Taoist flow, and communal virtue without dogma."
    result = generate_coda(summary, dummy_adapter)
    print(result)  # {'coda': 'Faith = Reason × Wonder ÷ Certainty.', 'reasoning': 'This line captures ...'}
```

### How to plug into your pipeline

```python
# orchestrator.py (sketch)
from cognitive_coda import generate_coda, openai_chat_adapter
# 1) Produce `final_synthesis` from your Dialectical Synthesizer / Voice of Reason
final_synthesis = voice_of_reason_output  # string

# 2) Build a provider adapter (example: OpenAI)
# from openai import OpenAI
# client = OpenAI()
# chat_fn = openai_chat_adapter(client, model="gpt-4o-mini", temperature=0.6)

# For now, assume you’ve set chat_fn appropriately
coda = generate_coda(final_synthesis, chat_fn)

# 3) Store or render
print(coda["coda"])
print(coda["reasoning"])
# -> Append to episode transcript, show notes, or read aloud as the last line.
```

**Notes**

* The validator enforces **≤15 words** and **single-line** for the coda.
* If you prefer the agent to never error, convert the `raise ValueError` checks into **auto-repair** (e.g., truncate to 15 words and retry).
* Keep `temperature ~0.5–0.7` for creative compression without drifting off-format.
