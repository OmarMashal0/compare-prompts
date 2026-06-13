# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
