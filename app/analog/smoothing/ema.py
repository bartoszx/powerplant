from __future__ import annotations


def ema_update(previous: float, value: float, alpha: float) -> float:
    if alpha <= 0.0:
        return value
    if alpha >= 1.0:
        return value
    return alpha * value + (1.0 - alpha) * previous






