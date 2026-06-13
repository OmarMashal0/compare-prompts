"""Tests for promptdiff.runner — uses mocked LiteLLM calls, no API key needed."""

from unittest.mock import MagicMock, patch
from promptdiff.runner import run_prompt, run_all


def make_mock_response(text="Hello world", prompt_tokens=50, completion_tokens=100):
    """Helper to create a fake LiteLLM response object."""
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = text
    response.usage = MagicMock()
    response.usage.prompt_tokens = prompt_tokens
    response.usage.completion_tokens = completion_tokens
    return response


class TestRunPrompt:
    @patch("promptdiff.runner.litellm.completion")
    @patch("promptdiff.runner.litellm.completion_cost", return_value=0.001)
    def test_returns_text(self, mock_cost, mock_completion):
        mock_completion.return_value = make_mock_response("Hello world")
        result = run_prompt("You are helpful.", "Say hello.", "gpt-4o-mini")
        assert result["text"] == "Hello world"

    @patch("promptdiff.runner.litellm.completion")
    @patch("promptdiff.runner.litellm.completion_cost", return_value=0.001)
    def test_returns_cost(self, mock_cost, mock_completion):
        mock_completion.return_value = make_mock_response("Response text")
        result = run_prompt("System prompt.", "User input.", "gpt-4o-mini")
        assert result["cost"] == 0.001

    @patch("promptdiff.runner.litellm.completion")
    @patch("promptdiff.runner.litellm.completion_cost", return_value=0.001)
    def test_returns_token_counts(self, mock_cost, mock_completion):
        mock_completion.return_value = make_mock_response(
            "Some output", prompt_tokens=30, completion_tokens=80
        )
        result = run_prompt("System.", "User.", "gpt-4o-mini")
        assert result["prompt_tokens"] == 30
        assert result["completion_tokens"] == 80

    @patch("promptdiff.runner.litellm.completion")
    @patch(
        "promptdiff.runner.litellm.completion_cost",
        side_effect=Exception("no pricing"),
    )
    def test_cost_fallback_to_zero(self, mock_cost, mock_completion):
        mock_completion.return_value = make_mock_response("Output")
        result = run_prompt("System.", "User.", "some-model")
        assert result["cost"] == 0.0


class TestRunAll:
    @patch("promptdiff.runner.litellm.completion")
    @patch("promptdiff.runner.litellm.completion_cost", return_value=0.001)
    def test_returns_results_for_each_label(self, mock_cost, mock_completion):
        mock_completion.return_value = make_mock_response("Some output")

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

    @patch("promptdiff.runner.litellm.completion")
    @patch("promptdiff.runner.litellm.completion_cost", return_value=0.001)
    def test_correct_number_of_api_calls(self, mock_cost, mock_completion):
        mock_completion.return_value = make_mock_response("Output")

        prompts = {"a": "Prompt A", "b": "Prompt B", "c": "Prompt C"}
        inputs = ["Q1", "Q2"]

        run_all(prompts, inputs, "gpt-4o-mini")

        # 3 prompts x 2 inputs = 6 calls
        assert mock_completion.call_count == 6
