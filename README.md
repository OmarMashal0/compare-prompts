# compare-prompts

[![PyPI version](https://badge.fury.io/py/compare-prompts.svg)](https://pypi.org/project/compare-prompts/)
[![CI](https://github.com/OmarMashal0/compare-prompts/actions/workflows/ci.yml/badge.svg)](https://github.com/OmarMashal0/compare-prompts/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Compare LLM prompts side by side. No config files. No dashboards. No signup.**

📦 **[View on PyPI](https://pypi.org/project/compare-prompts/)** | 🐙 **[View on GitHub](https://github.com/OmarMashal0/compare-prompts)**

```bash
pip install compare-prompts
```

---

## What is this?

You have two prompts. You changed one word. Did it actually change anything?

- Running them manually takes 30 minutes of eyeballing
- Setting up promptfoo requires YAML config and predefined "correct" answers
- Platforms like Braintrust/LangSmith require signup and send data to a dashboard

**compare-prompts is the missing middle ground** — run it in your script, get a table in your terminal in seconds:

```
                   Prompt Comparison Results
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        original             concise
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  avg length (tokens)   187                  61  (-67%)
  tone                  empathetic (61%)     analytical (54%) · cautious
  uses lists            67%                  33%
  uses headers          33%                  0%
  avg cost (USD)        $0.0021              $0.0009
  refusal rate          0%                   0%
  reading level         high school          middle school
  avg sentence length   18.3 words           9.1 words  (-50%)
```

Each column is a prompt. Each row is a measured behavioral difference. No guessing.

---

## Quickstart

### Step 1 — Install

```bash
pip install compare-prompts
```

---

### Step 2 — Get an API key

> **Already have a `.env` file with an API key?** Skip this step entirely — compare-prompts will pick it up automatically.

You need an API key for whichever provider you want to use. Create a `.env` file in your project root:

```bash
OPENAI_API_KEY=sk-...
```

compare-prompts reads `.env` files automatically. No extra setup.

| Provider | Where to get a key | Env variable | Free? |
|---|---|---|---|
| OpenAI | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | `OPENAI_API_KEY` | No |
| Anthropic | [console.anthropic.com](https://console.anthropic.com/settings/keys) | `ANTHROPIC_API_KEY` | No |
| Google Gemini | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | `GEMINI_API_KEY` | Yes |
| Groq | [console.groq.com/keys](https://console.groq.com/keys) | `GROQ_API_KEY` | Yes |
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com/) | `DEEPSEEK_API_KEY` | No |
| Ollama | [ollama.com](https://ollama.com) | None needed | Yes (local) |

> **New here?** Groq and Google Gemini both have free tiers — great for trying this out without spending anything.

---

### Step 3 — Create your comparison file

Generate a starter file by running:

```bash
python -m compare_prompts init
```

This creates a `test_prompts.py` file in your directory. Open it up, and you'll see a template that looks like this:

```python
from compare_prompts import compare

compare(
    prompts={
        # Each key is a label shown in the table column.
        # Each value is the system prompt you want to test.
        "original": "You are a helpful assistant.",
        "concise":  "You are a concise helpful assistant.",
    },
    inputs=[
        # These are the user messages sent to each prompt.
        # Use real questions your users actually ask for the most useful results.
        "Explain what a database is.",
        "What is recursion?",
        "Write a short poem about coding.",
    ],
    model="gpt-4o-mini"  # ← change this to match your provider
)
```

**How to edit this file:**
- **prompts:** Swap the example text with the actual prompts you want to compare.
- **inputs:** Add the test questions you want to evaluate those prompts against.
- **model:** Change the model string to match your provider. See the [Supported models](#supported-models) section below for the exact strings to use for OpenAI, Groq, Gemini, etc.

*(Note: If you don't want to use the `init` command, you can also just create `test_prompts.py` manually and paste the code above into it.)*

---

### Step 4 — Run it

```bash
python test_prompts.py
```

> **Too slow?** If you have many prompts or inputs, add `use_async=True` to run all API calls in parallel. See [Faster execution with async](#faster-execution-with-async) below.

> **Want to see the actual responses?** Add `show_outputs=True` to print the raw LLM output below the table. See [See raw outputs](#see-raw-outputs) below.

---

### Step 5 — Read the table

```
  Running 2 prompts x 3 inputs = 6 calls...

                   Prompt Comparison Results
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  avg length (tokens)   187                  61  (-67%)
  tone                  empathetic (61%)     analytical (54%) · cautious
  uses lists            67%                  33%
  uses headers          33%                  0%
  avg cost (USD)        $0.0021              $0.0009  (-57%)
  refusal rate          0%                   0%
  reading level         high school          middle school
  avg sentence length   18.3 words           9.1 words  (-50%)
```

Numbers in parentheses are diffs from the first (baseline) prompt.

The **tone** column shows the dominant tone and its confidence. When a second tone is also strong, it appears after `·` — e.g. `analytical (54%) · cautious` means primarily analytical with a notable cautious undertone.

---

## What it measures

| Metric | What it tells you |
|---|---|
| avg length (tokens) | How verbose each prompt makes the model |
| tone | Dominant writing style. 9 categories: `technical`, `formal`, `analytical`, `casual`, `empathetic`, `humorous`, `encouraging`, `cautious`, `assertive` |
| uses lists | % of responses that used bullet points or numbered lists |
| uses headers | % of responses that used markdown headers |
| uses code blocks | % of responses that used fenced code blocks |
| avg cost (USD)* | Estimated cost per API call based on token usage |
| refusal rate | % of responses that refused to answer |
| reading level | elementary / middle school / high school / college |
| avg sentence length | Average words per sentence |

*Cost calculation requires the full install: `pip install "compare-prompts[all]"`*

---

## Supported models

compare-prompts natively supports the top providers with no extra dependencies:

```python
compare(..., model="gpt-4o-mini")                        # OpenAI
compare(..., model="gpt-4o")                             # OpenAI
compare(..., model="anthropic/claude-3-5-haiku-20241022") # Anthropic
compare(..., model="anthropic/claude-3-5-sonnet-20241022")# Anthropic
compare(..., model="gemini/gemini-2.0-flash")            # Google Gemini (free tier)
compare(..., model="groq/llama-3.3-70b-versatile")       # Groq (free tier)
compare(..., model="ollama/llama3")                      # Ollama (local, free)
compare(..., model="deepseek/deepseek-chat")             # DeepSeek
```

**Need an enterprise model?**
Install the full package to unlock 2,600+ additional models (Azure, AWS Bedrock, Vertex AI, OpenRouter, etc.) via LiteLLM:

```bash
pip install "compare-prompts[all]"
```

Full list: [models.litellm.ai](https://models.litellm.ai)

---

## More options

### Compare more than 2 prompts

Every prompt gets its own column. Numbers show the diff from the first (baseline) prompt:

```python
compare(
    prompts={
        "baseline": "You are a helpful assistant.",
        "concise":  "You are a concise helpful assistant.",
        "formal":   "You are a professional formal assistant.",
        "friendly": "You are a warm friendly assistant.",
    },
    inputs=["your test questions"]
)
```

### See raw outputs

Print each LLM response below the table, grouped by input:

```python
compare(
    prompts={...},
    inputs=[...],
    show_outputs=True
)
```

### Faster execution with async

Run all API calls concurrently — useful when you have many prompt × input combinations:

```python
compare(
    prompts={...},
    inputs=[...],
    use_async=True
)
```

---

## Using it in an existing project

If you already have prompts defined in your code, just import them directly. No need to copy-paste:

```
your-project/
├── main.py           ← don't touch this
├── prompts.py        ← don't touch this
├── .env              ← don't touch this (already has your API key)
└── test_prompts.py   ← create this one new file
```

```python
from compare_prompts import compare
from prompts import PROMPT_V1, PROMPT_V2

compare(
    prompts={"v1": PROMPT_V1, "v2": PROMPT_V2},
    inputs=["your test questions here"],
    model="gpt-4o-mini"
)
```

---

## Why not promptfoo?

promptfoo is excellent. Use it if you need CI/CD integration, red-teaming, or assertion-based testing with predefined "correct" answers.

**compare-prompts is for when you just want to run prompts right now** and see how they behave differently — no YAML, no config, no web server. Just a table in your terminal.

---

## Contributing & Future Plans

Features planned for future versions:

- **Interactive Wizard Mode:** `python -m compare_prompts wizard` — set up a comparison interactively in the terminal, no Python file needed
- **Export to CSV / JSON:** Save results with `export="results.csv"`
- **Custom Metrics:** Inject your own scoring functions via `custom_metrics=[my_scorer]`
- **Live Streaming:** See LLM responses stream in while waiting for the final table
- **Local Caching:** Skip the API call if you've already run the exact same prompt
- **`.gitignore` generator:** Auto-add `.env` to `.gitignore` on `init` so you don't accidentally leak your keys

All contributions are welcome — whether it's one of the above or your own idea. Open a PR.

⭐ **If you find this useful, a star on GitHub goes a long way!** ⭐

---

## License

MIT
