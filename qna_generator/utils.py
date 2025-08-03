import math


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
