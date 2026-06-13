"""Tests for compare_prompts.metrics — no API calls, no API key needed."""

from compare_prompts.metrics import measure


class TestListDetection:
    def test_detects_bullet_list_dash(self):
        text = "Here are steps:\n- Step one\n- Step two\n- Step three"
        result = measure(text)
        assert result["uses_lists"] is True

    def test_detects_bullet_list_asterisk(self):
        text = "Items:\n* Item one\n* Item two"
        result = measure(text)
        assert result["uses_lists"] is True

    def test_detects_numbered_list(self):
        text = "Steps:\n1. First\n2. Second\n3. Third"
        result = measure(text)
        assert result["uses_lists"] is True

    def test_no_list(self):
        text = "This is a simple sentence without any lists."
        result = measure(text)
        assert result["uses_lists"] is False


class TestHeaderDetection:
    def test_detects_h1(self):
        text = "# Introduction\nSome content here."
        result = measure(text)
        assert result["uses_headers"] is True

    def test_detects_h2(self):
        text = "## Details\nMore content."
        result = measure(text)
        assert result["uses_headers"] is True

    def test_no_headers(self):
        text = "Just plain text with no headers at all."
        result = measure(text)
        assert result["uses_headers"] is False


class TestCodeBlockDetection:
    def test_detects_fenced_code(self):
        text = "Here is code:\n```python\nprint('hello')\n```"
        result = measure(text)
        assert result["uses_code_blocks"] is True

    def test_no_code_blocks(self):
        text = "Just regular text without code blocks."
        result = measure(text)
        assert result["uses_code_blocks"] is False


class TestTokenCount:
    def test_approximate_count(self):
        # 10 words -> approximately 10/0.75 = 13 tokens
        text = "one two three four five six seven eight nine ten"
        result = measure(text)
        assert 10 <= result["token_count"] <= 16

    def test_empty_text(self):
        result = measure("")
        assert result["token_count"] == 0

    def test_whitespace_only(self):
        result = measure("   ")
        assert result["token_count"] == 0


class TestRefusalDetection:
    def test_detects_refusal_cant(self):
        text = "I can't help with that request as it goes against my guidelines."
        result = measure(text)
        assert result["is_refusal"] is True

    def test_detects_refusal_unable(self):
        text = "I'm unable to assist with that question."
        result = measure(text)
        assert result["is_refusal"] is True

    def test_no_refusal(self):
        text = "Paris is the capital of France and is known for the Eiffel Tower."
        result = measure(text)
        assert result["is_refusal"] is False


class TestToneDetection:
    def test_formal_tone(self):
        text = (
            "Furthermore, the analysis demonstrates that consequently "
            "the results are significant. Moreover, the evidence "
            "notwithstanding shows improvement."
        )
        result = measure(text)
        assert result["tone"] == "formal"

    def test_warm_tone(self):
        text = (
            "I am so happy and excited to help you! "
            "This is wonderful and amazing! Absolutely fantastic!"
        )
        result = measure(text)
        assert result["tone"] == "warm"

    def test_technical_tone(self):
        text = (
            "The function accepts a parameter and returns an array. "
            "The class method implements the interface using the API."
        )
        result = measure(text)
        assert result["tone"] == "technical"

    def test_neutral_tone(self):
        text = "The sky is blue. Water is wet."
        result = measure(text)
        assert result["tone"] == "neutral"


class TestReadingLevel:
    def test_returns_valid_level(self):
        text = "A simple test sentence for checking the level."
        result = measure(text)
        assert result["reading_level"] in [
            "elementary", "middle school", "high school", "college"
        ]


class TestSentenceLength:
    def test_calculates_average(self):
        text = "Short sentence. Another short one. And one more."
        result = measure(text)
        assert result["avg_sentence_length"] > 0

    def test_empty_text(self):
        result = measure("")
        assert result["avg_sentence_length"] == 0.0


class TestReturnKeys:
    def test_returns_all_expected_keys(self):
        text = "A simple test sentence."
        result = measure(text)
        expected_keys = {
            "token_count", "uses_lists", "uses_headers", "uses_code_blocks",
            "tone", "reading_level", "is_refusal", "avg_sentence_length",
        }
        assert expected_keys == set(result.keys())

    def test_empty_text_returns_all_keys(self):
        result = measure("")
        expected_keys = {
            "token_count", "uses_lists", "uses_headers", "uses_code_blocks",
            "tone", "reading_level", "is_refusal", "avg_sentence_length",
        }
        assert expected_keys == set(result.keys())
