"""
Behavioral metrics for LLM output analysis.

All functions in this module operate on plain text strings.
No API calls, no ML models, no external services.
"""

import re
import textstat


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
        - tone: "warm", "formal", "neutral", or "technical"
        - reading_level: "elementary", "middle school", "high school", or "college"
        - is_refusal: True if response appears to be a refusal
        - avg_sentence_length: average number of words per sentence
    """

    if not text or not text.strip():
        return {
            "token_count": 0,
            "uses_lists": False,
            "uses_headers": False,
            "uses_code_blocks": False,
            "tone": "neutral",
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

    # Tone detection via keyword heuristics
    formal_words = [
        'furthermore', 'therefore', 'however', 'nevertheless',
        'consequently', 'regarding', 'pursuant', 'hereby',
        'moreover', 'accordingly', 'notwithstanding', 'whereas',
    ]
    warm_words = [
        'happy', 'great', 'wonderful', 'love', 'feel', 'hope',
        'glad', 'excited', 'amazing', 'fantastic', 'sure', 'awesome',
        'absolutely', 'delighted', 'pleasure',
    ]
    technical_words = [
        'function', 'variable', 'algorithm', 'parameter',
        'return', 'class', 'method', 'array', 'object', 'syntax',
        'implementation', 'interface', 'compile', 'runtime', 'api',
    ]

    text_lower = text.lower()
    formal_score = sum(1 for w in formal_words if w in text_lower)
    warm_score = sum(1 for w in warm_words if w in text_lower)
    technical_score = sum(1 for w in technical_words if w in text_lower)

    max_score = max(formal_score, warm_score, technical_score)
    if max_score == 0:
        tone = "neutral"
    elif formal_score == max_score:
        tone = "formal"
    elif warm_score == max_score:
        tone = "warm"
    else:
        tone = "technical"

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
    is_refusal = any(phrase in text_lower for phrase in refusal_phrases)

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
        "reading_level": reading_level,
        "is_refusal": is_refusal,
        "avg_sentence_length": avg_sentence_length,
    }
