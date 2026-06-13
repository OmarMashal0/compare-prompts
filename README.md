# compare-prompts

[![PyPI version](https://badge.fury.io/py/compare-prompts.svg)](https://pypi.org/project/compare-prompts/)
[![CI](https://github.com/OmarMashal0/compare-prompts/actions/workflows/ci.yml/badge.svg)](https://github.com/OmarMashal0/compare-prompts/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Compare LLM prompts side by side. No config files. No dashboards. No signup.**

```bash
pip install compare-prompts
```

---

## The problem

You have two (or more) prompts. You changed one word. Did it actually change anything? Right now:
- Running them manually and eyeballing outputs takes 30 minutes
- Setting up promptfoo requires YAML config and predefined "correct" answers
- Platforms like Braintrust/LangSmith require signup and send data to a dashboard

**compare-prompts is the missing middle ground** — run it in your script, get a table in your terminal.

---

## Quickstart

### Step 1 — Install

```bash
pip install compare-prompts
```

### Step 2 — Generate a starter file (optional)

```bash
compare-prompts init
```

This creates a `test_prompts.py` file you can edit immediately.

### Step 3 — Or write your own comparison

```python
from compare_prompts import compare

compare(
    prompts={
        "original": "You are a helpful assistant.",
        "concise":  "You are a concise helpful assistant.",
    },
    inputs=[
        "Explain what a database is.",
        "What is recursion?",
        "Write a short poem about coding.",
    ],
    model="gpt-4o-mini"
)
```

### Step 4 — Run it

```bash
python test_prompts.py
```

### Step 5 — See results

```
Running 2 prompts x 3 inputs = 6 calls...  done

                   Prompt Comparison Results
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  avg length (tokens)    187                  61  (-67%)
  tone                   warm                 neutral
  uses lists             67%                  33%
  uses headers           33%                  0%
  avg cost (USD)*        $0.0021              $0.0009
  refusal rate           0%                   0%
  reading level          high school          middle school
```

---

## Where to put this in your project

```
your-project/                <- your existing project
├── main.py                  <- don't touch this
├── prompts.py               <- don't touch this
├── .env                     <- don't touch this (already has your API key)
└── test_prompts.py          <- create this one new file
```

Import your prompts directly from your existing code:

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

## Setup your API key

Create a `.env` file in your project root (or use an existing one):

```bash
# Only one key is needed — whichever provider you use
OPENAI_API_KEY=sk-...
```

compare-prompts automatically reads `.env` files. No extra configuration.

### Get an API key

| Provider | Link | Env variable | Free tier? |
|---|---|---|---|
| OpenAI | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | `OPENAI_API_KEY` | No |
| Anthropic | [console.anthropic.com](https://console.anthropic.com/settings/keys) | `ANTHROPIC_API_KEY` | No |
| Google Gemini | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | `GEMINI_API_KEY` | Yes |
| Groq | [console.groq.com/keys](https://console.groq.com/keys) | `GROQ_API_KEY` | Yes |
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com/) | `DEEPSEEK_API_KEY` | No |
| Ollama | [ollama.com](https://ollama.com) | None needed | Yes (local) |

---

## Supported models

`compare-prompts` is extremely lightweight and natively supports the top 6 major AI providers with **zero external dependencies**:

```python
compare(..., model="gpt-4o-mini")                      # OpenAI
compare(..., model="gpt-4o")                            # OpenAI
compare(..., model="anthropic/claude-3-5-haiku-20241022") # Anthropic
compare(..., model="anthropic/claude-3-5-sonnet-20241022")# Anthropic
compare(..., model="gemini/gemini-2.0-flash")           # Google Gemini
compare(..., model="groq/llama-3.3-70b-versatile")      # Groq (free)
compare(..., model="ollama/llama3")                     # Ollama (local, free)
compare(..., model="deepseek/deepseek-chat")            # DeepSeek
```

**Need an enterprise model?**
We also optionally support 2,600+ additional models (Azure, AWS Bedrock, Vertex AI, OpenRouter, etc.) via LiteLLM as a fallback. To unlock them, just install the full package:
```bash
pip install "compare-prompts[all]"
```
Full list of all 2,600+ advanced models: [models.litellm.ai](https://models.litellm.ai)

---

## Compare more than 2 prompts

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

Each prompt becomes a column. Same table, more columns.

---

## See raw outputs

```python
compare(
    prompts={...},
    inputs=[...],
    show_outputs=True
)
```

Prints each raw LLM response below the table, grouped by input.

---

## Faster execution with async

For many prompt+input combinations, run calls concurrently:

```python
compare(
    prompts={...},
    inputs=[...],
    use_async=True
)
```

---

## What it measures

| Metric | Description |
|---|---|
| avg length (tokens) | Average response length in tokens |
| tone | Detected tone: neutral, formal, warm, or technical |
| uses lists | % of responses using bullet points or numbered lists |
| uses headers | % of responses using markdown headers |
| uses code blocks | % of responses using fenced code blocks |
| avg cost (USD)* | Estimated cost per response based on token usage |
| refusal rate | % of responses that refused to answer |
| reading level | elementary / middle school / high school / college |
| avg sentence length | Average number of words per sentence |

*(Note: Calculating API costs requires installing the full version: `pip install "compare-prompts[all]"`)*

---

## Why not promptfoo?

promptfoo is excellent. Use it if you need CI/CD integration, red-teaming,
or assertion-based testing with expected outputs.

**compare-prompts is for when you just want to run prompts right now** and see how they
behave differently — no YAML, no config, no web server, no predefined "correct"
answers. Just a table in your terminal.

---

## Future Work & Contributions

Here are some major features I plan to build into `compare-prompts` in the future:

- **Interactive Wizard Mode:** A `compare-prompts wizard` CLI command that interactively asks for prompts and inputs in the terminal, eliminating the need to create a Python file.
- **Export to CSV / JSON:** Allowing `export="results.csv"` to save the terminal table data to a file.
- **Custom Python Metrics:** Permitting developers to inject arbitrary scoring functions (e.g., `custom_metrics=[my_cohesion_scorer]`).
- **Live Streaming Output:** Streaming LLM responses live to the terminal while waiting for the final aggregate table.
- **Local Caching:** Adding a local cache so re-running the exact same prompt doesn't hit the API twice.
- **CLI Safety Guards:** Adding a `.gitignore` generator to the `init` command so beginners don't leak their `.env` files.

While I plan to implement these, **all contributions are wildly welcomed and appreciated!** If you want to tackle any of these items, or if you have a totally different idea for a metric, a new AI provider, or a UI tweak, PRs are always welcome. If you have your own idea that isn't on this list, that is also good and all good! Build it and open a PR.

⭐ **If you find this tool useful or like the idea, please don't forget to star the repository!** ⭐

---

## License

MIT
