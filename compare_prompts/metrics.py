"""
Behavioral metrics for LLM output analysis.

All functions in this module operate on plain text strings.
No API calls, no ML models, no external services.
"""

import math
import re
import textstat


# ---------------------------------------------------------------------------
# Tone lexicons — (words, phrases) per category.
# Words are matched as whole tokens (\b boundaries).
# Phrases are matched literally and count double (stronger signal).
# ---------------------------------------------------------------------------

_TONE_LEXICONS: dict[str, dict] = {
    "technical": {
        "words": [
            "function", "variable", "algorithm", "parameter", "return",
            "class", "method", "array", "object", "syntax", "implementation",
            "interface", "compile", "runtime", "api", "debug", "error",
            "exception", "library", "framework", "module", "instance",
            "iterate", "recursion", "loop", "string", "integer", "boolean",
            "null", "async", "callback", "promise", "endpoint", "database",
            "query", "schema", "token", "parse", "output", "input",
        ],
        "phrases": [
            "return value", "time complexity", "edge case", "use case",
            "data structure", "code block", "type error", "stack trace",
            "null pointer", "key value",
        ],
    },
    "formal": {
        "words": [
            "furthermore", "therefore", "however", "nevertheless",
            "consequently", "regarding", "pursuant", "hereby", "moreover",
            "accordingly", "notwithstanding", "whereas", "henceforth",
            "aforementioned", "therein", "thereof", "herein", "stipulate",
            "endeavor", "commence", "terminate", "ascertain", "facilitate",
            "pertaining", "constitute", "whereby", "insofar", "forthwith",
            "heretofore", "subsequently", "aforementioned", "thus",
        ],
        "phrases": [
            "in accordance with", "with respect to", "in the event that",
            "it should be noted", "in light of", "it is worth noting",
            "as previously mentioned", "in conclusion", "to summarize",
            "it is important to note",
        ],
    },
    "analytical": {
        "words": [
            "analyze", "analysis", "data", "evidence", "research", "study",
            "findings", "conclude", "hypothesis", "theory", "measure",
            "compare", "evaluate", "assess", "determine", "identify",
            "examine", "observe", "indicate", "demonstrate", "correlation",
            "factor", "component", "structure", "process", "mechanism",
            "pattern", "trend", "metric", "benchmark", "approach", "method",
            "result", "outcome", "insight", "reasoning",
        ],
        "phrases": [
            "based on", "it follows that", "the data shows",
            "this suggests", "the evidence indicates", "one can conclude",
            "this demonstrates", "the results show", "in comparison",
            "on the other hand",
        ],
    },
    "casual": {
        "words": [
            "yeah", "yep", "nope", "okay", "ok", "hey", "just", "pretty",
            "really", "totally", "basically", "actually", "honestly",
            "anyway", "gonna", "wanna", "kinda", "sorta", "gotta", "awesome",
            "cool", "nice", "stuff", "thing", "things", "bit", "lot",
            "quick", "super", "easy", "literally", "definitely", "right",
            "sure", "look", "well", "so",
        ],
        "phrases": [
            "you know", "kind of", "sort of", "a lot of", "by the way",
            "for sure", "no worries", "feel free", "heads up", "fair enough",
        ],
    },
    "empathetic": {
        "words": [
            "understand", "feel", "empathize", "support", "care", "help",
            "together", "happy", "glad", "wonderful", "love", "hope",
            "delighted", "pleasure", "appreciate", "value", "respect",
            "kind", "compassionate", "concern", "experience", "journey",
            "growth", "comfort", "encourage", "embrace", "nurture",
            "hear", "listen", "validate", "acknowledge", "relate",
        ],
        "phrases": [
            "i understand", "that must be", "i can imagine", "you are not alone",
            "i am here to help", "i hear you", "it makes sense",
            "i appreciate you", "thank you for sharing", "i know how",
        ],
    },
    "humorous": {
        "words": [
            "joke", "funny", "laugh", "humor", "wit", "sarcasm", "irony",
            "pun", "hilarious", "comical", "absurd", "silly", "playful",
            "amusing", "chuckle", "ridiculous", "banter", "quip", "wink",
            "teasing", "haha", "lol", "lmao", "hehe", "comic", "goofy",
            "whimsical", "lighthearted", "tongue",
        ],
        "phrases": [
            "just kidding", "no pun intended", "on a lighter note",
            "in all seriousness", "ha ha", "not to be funny",
            "speaking of which", "you had to be there",
        ],
    },
    "encouraging": {
        "words": [
            "believe", "achieve", "succeed", "inspire", "motivate", "courage",
            "potential", "capable", "strength", "thrive", "persist",
            "resilience", "empower", "proud", "progress", "overcome",
            "champion", "unleash", "transform", "fearless", "ambitious",
            "confidence", "determination", "celebrate", "remarkable",
            "incredible", "proud", "brilliant",
        ],
        "phrases": [
            "you can do it", "keep going", "don't give up", "you've got this",
            "great job", "keep it up", "i believe in you", "well done",
            "you are capable", "proud of you",
        ],
    },
    "cautious": {
        "words": [
            "perhaps", "maybe", "possibly", "might", "arguably", "seemingly",
            "apparently", "generally", "typically", "often", "usually",
            "suggest", "indicate", "appear", "tend", "likely", "uncertain",
            "approximately", "somewhat", "arguably", "potentially",
            "conceivably", "presumably", "arguably", "ostensibly",
            "tentatively", "cautiously", "carefully",
        ],
        "phrases": [
            "it depends", "in some cases", "this may vary", "it is worth noting",
            "results may differ", "generally speaking", "as a general rule",
            "this is not always", "keep in mind", "bear in mind",
        ],
    },
    "assertive": {
        "words": [
            "must", "always", "never", "clearly", "certainly",
            "obviously", "simply", "exactly", "precisely", "immediately",
            "required", "essential", "critical", "undoubtedly", "guaranteed",
            "undeniable", "absolutely", "directly", "explicitly", "firmly",
            "decisively", "unquestionably", "definitively", "plainly",
        ],
        "phrases": [
            "the answer is", "you need to", "this is how", "make sure you",
            "the fact is", "without a doubt", "it is clear that",
            "you must", "do not", "always remember",
        ],
    },
}

# Minimum raw score (hits per 100 words) for any tone to be considered
_MIN_FLOOR = 0.3

# Secondary tone shown only if its softmax share exceeds this threshold
_SECONDARY_THRESHOLD = 0.33


def _score_tone(text_lower: str, word_count: int, lexicon: dict) -> float:
    """
    Compute a length-normalized score for one tone category.

    Words matched with whole-word regex, counted by frequency.
    Phrase matches count double.
    Score is returned as hits per 100 words.
    """
    raw = 0

    for word in lexicon["words"]:
        raw += len(re.findall(r'\b' + re.escape(word) + r'\b', text_lower))

    for phrase in lexicon["phrases"]:
        raw += 2 * len(re.findall(re.escape(phrase), text_lower))

    return (raw / max(word_count, 1)) * 100


def _softmax(scores: dict[str, float]) -> dict[str, float]:
    """Apply softmax to a dict of raw scores → probabilities."""
    values = list(scores.values())
    exp_values = [math.exp(v) for v in values]
    total = sum(exp_values)
    return {k: exp_values[i] / total for i, k in enumerate(scores)}


def _detect_tone(text: str, word_count: int) -> str:
    """
    Detect tone using softmax-normalized scoring over 9 tone categories.

    Returns a display string:
      - "neutral"                        if no tone clears the minimum floor
      - "primary (X%)"                   if secondary share ≤ 33%
      - "primary (X%) · secondary"       if secondary share > 33%
    """
    text_lower = text.lower()

    raw_scores = {
        tone: _score_tone(text_lower, word_count, lexicon)
        for tone, lexicon in _TONE_LEXICONS.items()
    }

    # If nothing clears the minimum floor, return neutral immediately
    if max(raw_scores.values()) < _MIN_FLOOR:
        return "neutral"

    probs = _softmax(raw_scores)

    # Sort tones by probability descending
    ranked = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    primary_tone, primary_prob = ranked[0]
    secondary_tone, secondary_prob = ranked[1]

    primary_pct = round(primary_prob * 100)

    if secondary_prob > _SECONDARY_THRESHOLD:
        return f"{primary_tone} ({primary_pct}%) · {secondary_tone}"
    else:
        return f"{primary_tone} ({primary_pct}%)"


def tone_scores(text: str) -> dict[str, float]:
    """
    Return raw softmax probability scores for each tone category.

    Useful for aggregation across multiple inputs.

    Args:
        text: The raw output string from an LLM.

    Returns:
        Dict mapping tone name → softmax probability (0.0–1.0).
        Returns uniform distribution if text is empty or too short.
    """
    if not text or not text.strip():
        n = len(_TONE_LEXICONS)
        return {tone: 1.0 / n for tone in _TONE_LEXICONS}

    word_count = len(text.split())
    text_lower = text.lower()

    raw_scores = {
        tone: _score_tone(text_lower, word_count, lexicon)
        for tone, lexicon in _TONE_LEXICONS.items()
    }

    if max(raw_scores.values()) < _MIN_FLOOR:
        return {"neutral": 1.0, **{t: 0.0 for t in _TONE_LEXICONS}}

    return _softmax(raw_scores)


def tone_label_from_scores(avg_scores: dict[str, float]) -> str:
    """
    Convert averaged softmax score vectors → display label.

    Used by the aggregation layer in display.py to produce a tone label
    from probability vectors averaged across multiple inputs.

    Args:
        avg_scores: Dict mapping tone name → average probability.

    Returns:
        Display string in same format as _detect_tone().
    """
    # Neutral sentinel: either all inputs had no tone signal (value close to 1.0)
    # or the majority of the averaged weight is on the neutral placeholder
    if avg_scores.get("neutral", 0) > 0.5:
        return "neutral"

    # Filter out the neutral sentinel key if present
    scores = {k: v for k, v in avg_scores.items() if k != "neutral"}

    if not scores:
        return "neutral"

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_tone, primary_prob = ranked[0]
    secondary_tone, secondary_prob = ranked[1]

    primary_pct = round(primary_prob * 100)

    if secondary_prob > _SECONDARY_THRESHOLD:
        return f"{primary_tone} ({primary_pct}%) · {secondary_tone}"
    else:
        return f"{primary_tone} ({primary_pct}%)"


def measure(text: str) -> dict:
    """
    Analyze a single LLM output string and return behavioral metrics.

    Args:
        text: The raw output string from an LLM.

    Returns:
        A dict with keys:
        - token_count: approximate token count (words / 0.75)
        - uses_lists: True if response contains bullet points or numbered lists
        - uses_headers: True if response contains markdown headers
        - uses_code_blocks: True if response contains fenced code blocks
        - tone: display string e.g. "technical (71%)" or "formal (52%) · cautious"
        - tone_scores: dict of softmax probabilities per tone (for aggregation)
        - reading_level: "elementary", "middle school", "high school", or "college"
        - is_refusal: True if response appears to be a refusal
        - avg_sentence_length: average number of words per sentence
    """

    if not text or not text.strip():
        n = len(_TONE_LEXICONS)
        return {
            "token_count": 0,
            "uses_lists": False,
            "uses_headers": False,
            "uses_code_blocks": False,
            "tone": "neutral",
            "tone_scores": {tone: 1.0 / n for tone in _TONE_LEXICONS},
            "reading_level": "elementary",
            "is_refusal": False,
            "avg_sentence_length": 0.0,
        }

    # Token count (approximate — 1 token ≈ 0.75 words for English)
    word_count = len(text.split())
    token_count = int(word_count / 0.75)

    # Uses bullet lists (lines starting with -, *, bullet, or numbers like "1.")
    uses_lists = bool(
        re.search(r'^\s*[-*•]\s', text, re.MULTILINE)
        or re.search(r'^\s*\d+\.\s', text, re.MULTILINE)
    )

    # Uses markdown headers (lines starting with #)
    uses_headers = bool(re.search(r'^#{1,6}\s', text, re.MULTILINE))

    # Uses fenced code blocks (``` or ~~~)
    uses_code_blocks = bool(re.search(r'^```|^~~~', text, re.MULTILINE))

    # Tone detection
    t_scores = tone_scores(text)
    tone = _detect_tone(text, word_count)

    # Reading level via textstat Flesch-Kincaid grade
    # textstat needs at least ~100 words for accurate scoring
    # For shorter texts we use a simpler average word length heuristic
    if word_count >= 100:
        grade = textstat.flesch_kincaid_grade(text)
    else:
        avg_word_len = sum(len(w) for w in text.split()) / max(word_count, 1)
        grade = avg_word_len * 1.5  # rough approximation

    if grade < 6:
        reading_level = "elementary"
    elif grade < 9:
        reading_level = "middle school"
    elif grade < 13:
        reading_level = "high school"
    else:
        reading_level = "college"

    # Refusal detection
    refusal_phrases = [
        "i can't", "i cannot", "i'm unable", "i am unable",
        "i won't", "i will not", "not able to", "unable to assist",
        "against my", "not appropriate", "i must decline",
        "i'm not able", "i am not able", "i apologize, but i cannot",
        "sorry, but i can't",
    ]
    is_refusal = any(phrase in text.lower() for phrase in refusal_phrases)

    # Average sentence length
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if sentences:
        avg_sentence_length = round(
            sum(len(s.split()) for s in sentences) / len(sentences), 1
        )
    else:
        avg_sentence_length = 0.0

    return {
        "token_count": token_count,
        "uses_lists": uses_lists,
        "uses_headers": uses_headers,
        "uses_code_blocks": uses_code_blocks,
        "tone": tone,
        "tone_scores": t_scores,
        "reading_level": reading_level,
        "is_refusal": is_refusal,
        "avg_sentence_length": avg_sentence_length,
    }
