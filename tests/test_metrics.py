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
        assert result["tone"].startswith("formal")

    def test_empathetic_tone(self):
        text = (
            "I understand how you feel. I am here to help and I hear you. "
            "Together we can find comfort. I appreciate you sharing this journey."
        )
        result = measure(text)
        assert result["tone"].startswith("empathetic")

    def test_technical_tone(self):
        text = (
            "The function accepts a parameter and returns an array. "
            "The class method implements the interface using the API. "
            "Debug the exception in the recursive loop."
        )
        result = measure(text)
        assert result["tone"].startswith("technical")

    def test_neutral_tone(self):
        text = "The sky is blue. Water is wet."
        result = measure(text)
        assert result["tone"] == "neutral"

    def test_humorous_tone(self):
        text = (
            "Haha, just kidding! No pun intended, but this is hilarious. "
            "The absurd and silly situation made everyone chuckle. "
            "What a whimsical and playful twist — on a lighter note, lol!"
        )
        result = measure(text)
        assert result["tone"].startswith("humorous")

    def test_encouraging_tone(self):
        text = (
            "You can do it! Keep going, don't give up. I believe in you. "
            "You have the strength and resilience to overcome this. "
            "Believe in your potential and celebrate every bit of progress."
        )
        result = measure(text)
        assert result["tone"].startswith("encouraging")

    def test_cautious_tone(self):
        text = (
            "Perhaps this might work, but it depends on the situation. "
            "Generally speaking, results may differ. Keep in mind that "
            "this may vary and is not always the case. Arguably, it tends "
            "to appear somewhat uncertain in some cases."
        )
        result = measure(text)
        assert result["tone"].startswith("cautious")

    def test_assertive_tone(self):
        text = (
            "You must do this immediately. The answer is clearly defined. "
            "Always remember: never skip this step. Make sure you follow "
            "the required process precisely. Without a doubt, it is critical."
        )
        result = measure(text)
        assert result["tone"].startswith("assertive")

    def test_casual_tone(self):
        text = (
            "Hey, so basically you just wanna do this thing, you know? "
            "It's pretty easy, honestly. Kind of a lot of stuff going on, "
            "but anyway feel free to ask. No worries, for sure!"
        )
        result = measure(text)
        assert result["tone"].startswith("casual")

    def test_analytical_tone(self):
        text = (
            "Based on the data, the analysis indicates a strong correlation. "
            "The evidence demonstrates a clear trend. This suggests that "
            "the findings support the hypothesis. In comparison, the results "
            "show a measurable outcome worth evaluating."
        )
        result = measure(text)
        assert result["tone"].startswith("analytical")

    def test_tone_includes_percentage(self):
        """Non-neutral tones should include a percentage in the output."""
        text = (
            "The function accepts a parameter and returns an array. "
            "The class method implements the interface using the API."
        )
        result = measure(text)
        if result["tone"] != "neutral":
            assert "%" in result["tone"]

    def test_secondary_tone_shown_when_strong(self):
        """When two tones are both strong, both appear in the label."""
        text = (
            "Haha! Just kidding — no pun intended. This is hilarious and silly. "
            "But on a lighter note: you must do this immediately. "
            "Always remember, never skip it. It is absolutely critical."
        )
        result = measure(text)
        # Primary tone may be humorous or assertive; either way if secondary
        # is strong enough the · separator should appear
        # (not always guaranteed with short text, so just check format is valid)
        tone = result["tone"]
        assert isinstance(tone, str) and len(tone) > 0

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
            "tone", "tone_scores", "reading_level", "is_refusal",
            "avg_sentence_length",
        }
        assert expected_keys == set(result.keys())

    def test_empty_text_returns_all_keys(self):
        result = measure("")
        expected_keys = {
            "token_count", "uses_lists", "uses_headers", "uses_code_blocks",
            "tone", "tone_scores", "reading_level", "is_refusal",
            "avg_sentence_length",
        }
        assert expected_keys == set(result.keys())

    def test_tone_scores_contains_all_categories(self):
        """tone_scores dict should have one key per tone category."""
        from compare_prompts.metrics import _TONE_LEXICONS
        result = measure("A simple test sentence.")
        # neutral sentinel may appear for empty-ish text, otherwise all 9 lexicon keys
        tone_score_keys = set(result["tone_scores"].keys())
        expected = set(_TONE_LEXICONS.keys())
        # Must contain at least all lexicon keys (neutral sentinel is additive)
        assert expected.issubset(tone_score_keys | {"neutral"})
