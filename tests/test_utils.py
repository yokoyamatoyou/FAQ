import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))
from qna_generator.utils import calculate_temperature_step, increment_temperature


def test_calculate_temperature_step_basic():
    assert calculate_temperature_step(0) == 1
    assert calculate_temperature_step(4) == 1
    assert calculate_temperature_step(8) == 1
    assert calculate_temperature_step(16) == 2


def test_increment_temperature_capped():
    assert increment_temperature(0.0) == 0.1
    assert increment_temperature(0.75) == 0.8
    assert increment_temperature(0.8) == 0.8
