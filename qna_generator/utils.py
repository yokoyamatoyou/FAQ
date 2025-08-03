import math
from typing import List


def calculate_temperature_step(question_count: int, *, max_temp: float = 0.8, increment: float = 0.1) -> int:
    """Calculate how many questions should be generated before increasing temperature.

    The step is based on distributing temperature increments (of ``increment``) until
    ``max_temp`` is reached. At least one question is required for a step.
    """
    if question_count <= 0:
        return 1
    total_steps = max_temp / increment
    return max(1, math.ceil(question_count / total_steps))


def increment_temperature(current_temp: float, *, increment: float = 0.1, max_temp: float = 0.8) -> float:
    """Return the next temperature value capped at ``max_temp``."""
    return min(current_temp + increment, max_temp)


def split_text_into_chunks(text: str, max_tokens: int) -> List[str]:
    """Split ``text`` into chunks each within ``max_tokens`` *approximate* tokens.

    This simple implementation treats whitespace-separated words as tokens to
    avoid external dependencies. It ensures that each returned chunk contains at
    most ``max_tokens`` words. If ``max_tokens`` is non-positive, the original
    text is returned as a single chunk.
    """

    if max_tokens <= 0:
        return [text]

    words = text.split()
    if len(words) <= max_tokens:
        return [text]

    chunks: List[str] = []
    for i in range(0, len(words), max_tokens):
        chunk = " ".join(words[i : i + max_tokens])
        chunks.append(chunk)
    return chunks
