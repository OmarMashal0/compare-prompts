# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2026-06-14

### Changed
- Massive README rewrite to improve the onboarding flow for new users, moving API key instructions earlier and highlighting free tier options like Groq.
- Unified the `init` command flow so users are directly guided to generate and edit a comparison file rather than having disjointed options.
- Added explicit trailing commas to code examples to make copy-pasting easier and prevent syntax errors.
- **UI:** Added helpful interactive tips directly to the terminal output guiding users to use `use_async=True` (if running many prompts) and `show_outputs=True` (to see raw LLM text).
- **Metadata:** Fixed incorrect author email address in package setup.

## [0.3.0] - 2026-06-14

### Changed
- **Overhauled tone detection** — replaced the 3-word-list heuristic with a proper 9-category system: `technical`, `formal`, `analytical`, `casual`, `empathetic`, `humorous`, `encouraging`, `cautious`, `assertive`.
- Tone scoring now uses whole-word regex matching (`\b` boundaries) instead of substring search, eliminating false positives (e.g. `class` no longer matches `classical`).
- Tone scoring now counts per-occurrence frequency rather than just checking keyword presence.
- All tone scores are length-normalized (hits per 100 words) so short and long responses are treated fairly.
- Scores are converted to a softmax probability distribution for principled multi-category classification.
- **New display format:** tone row now shows `"technical (71%)"` (primary + confidence) or `"technical (52%) · cautious"` (when secondary tone exceeds 33% share), instead of a single flat label.
- Aggregation across multiple inputs now averages softmax probability vectors rather than picking the modal string — much more accurate for mixed-tone prompt comparisons.
- Added `tone_scores` key to `measure()` return dict (dict of softmax probabilities per category, used internally for aggregation).
- Expanded test suite: 12 tone tests (up from 4), covering all 9 categories plus format validation.

## [0.2.4] - 2026-06-13

### Fixed
- Fixed HTTP 403 Forbidden errors when using the Groq API due to Cloudflare blocking native urllib requests without a User-Agent header.

## [0.2.3] - 2026-06-13

### Added
- Added `__main__.py` to support executing the CLI directly via `python -m compare_prompts`.

## [0.2.2] - 2026-06-13

### Changed
- Fixed a bug in the GitHub Actions pipeline that prevented PyPI uploads (`contents: read` permissions).
- Added dynamic API cost calculation using `litellm` fallback if installed.
- Fixed documentation around supported models to clarify native vs fallback logic.
- Added DeepSeek to the API keys documentation.

## [0.2.0] - 2026-06-13

### Changed
- Massive size reduction: stripped `litellm` from default install, reducing package size from 192MB to ~30MB.
- Rewrote the core routing engine to use pure Python `urllib` for OpenAI, Groq, DeepSeek, Ollama, Anthropic, and Gemini natively.
- Made `litellm` an optional dependency (`pip install "compare-prompts[all]"`) to handle obscure enterprise models as a smart fallback.

## [0.1.4] - 2026-06-13

### Changed
- Complete rename and refactor to `compare-prompts` across all namespaces.
- Fixed Python 3.9 type-hinting compatibility for GitHub Actions CI.

## [0.1.0] - 2026-06-13

### Added
- `compare()` function with support for 2+ prompts
- Support for dict and list prompt input formats
- Metrics: token count, tone, lists, headers, code blocks, cost, refusal rate, reading level, sentence length
- LiteLLM integration (2,600+ models supported)
- `show_outputs` parameter for viewing raw responses
- `use_async` parameter for concurrent execution
- `compare-prompts init` CLI command for scaffolding test files
- Progress indicator during API calls
- Clear error messages for missing API keys, invalid model names, and rate limits
- Comprehensive test suite (no API keys needed to run tests)
