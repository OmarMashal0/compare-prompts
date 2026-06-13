"""Tests for compare_prompts.runner — uses mocked HTTP calls, no API key needed."""

from unittest.mock import patch
from compare_prompts.runner import run_prompt, run_all

def mock_native_call(*args, **kwargs):
    return {
        "text": "Hello world",
        "prompt_tokens": 50,
        "completion_tokens": 100,
        "cost": 0.0,
    }

class TestRunPrompt:
    @patch("compare_prompts.runner.os.getenv", return_value="fake_key")
    @patch("compare_prompts.runner._native_openai_call", side_effect=mock_native_call)
    def test_returns_text(self, mock_call, mock_env):
        result = run_prompt("You are helpful.", "Say hello.", "gpt-4o-mini")
        assert result["text"] == "Hello world"

    @patch("compare_prompts.runner.os.getenv", return_value="fake_key")
    @patch("compare_prompts.runner._native_openai_call", side_effect=mock_native_call)
    def test_returns_cost(self, mock_call, mock_env):
        result = run_prompt("System prompt.", "User input.", "gpt-4o-mini")
        assert result["cost"] == 0.0

    @patch("compare_prompts.runner.os.getenv", return_value="fake_key")
    @patch("compare_prompts.runner._native_openai_call")
    def test_returns_token_counts(self, mock_call, mock_env):
        mock_call.return_value = {
            "text": "Some output",
            "prompt_tokens": 30,
            "completion_tokens": 80,
            "cost": 0.0
        }
        result = run_prompt("System.", "User.", "gpt-4o-mini")
        assert result["prompt_tokens"] == 30
        assert result["completion_tokens"] == 80

class TestRunAll:
    @patch("compare_prompts.runner.os.getenv", return_value="fake_key")
    @patch("compare_prompts.runner._native_openai_call", side_effect=mock_native_call)
    def test_returns_results_for_each_label(self, mock_call, mock_env):
        prompts = {
            "prompt_a": "You are helpful.",
            "prompt_b": "You are concise.",
        }
        inputs = ["Question one", "Question two"]

        results = run_all(prompts, inputs, "gpt-4o-mini")

        assert "prompt_a" in results
        assert "prompt_b" in results
        assert len(results["prompt_a"]) == 2  # one result per input
        assert len(results["prompt_b"]) == 2

    @patch("compare_prompts.runner.os.getenv", return_value="fake_key")
    @patch("compare_prompts.runner._native_openai_call", side_effect=mock_native_call)
    def test_correct_number_of_api_calls(self, mock_call, mock_env):
        prompts = {"a": "Prompt A", "b": "Prompt B", "c": "Prompt C"}
        inputs = ["Q1", "Q2"]

        run_all(prompts, inputs, "gpt-4o-mini")

        # 3 prompts x 2 inputs = 6 calls
        assert mock_call.call_count == 6
