# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
