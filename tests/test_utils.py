import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))
from qna_generator.utils import (
    calculate_temperature_step,
    increment_temperature,
    split_text_into_chunks,
)


def test_calculate_temperature_step_basic():
    assert calculate_temperature_step(0) == 1
    assert calculate_temperature_step(4) == 1
    assert calculate_temperature_step(8) == 1
    assert calculate_temperature_step(16) == 2


def test_increment_temperature_capped():
    assert increment_temperature(0.0) == 0.1
    assert increment_temperature(0.75) == 0.8
    assert increment_temperature(0.8) == 0.8


def test_split_text_into_chunks_respects_token_limit():
    text = "token " * 50
    chunks = split_text_into_chunks(text, max_tokens=10)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.split()) <= 10
