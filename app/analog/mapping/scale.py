from __future__ import annotations

from typing import Optional


def clamp_ratio(value: float, full_scale: float, clamp_min: Optional[float] = None) -> float:
    if clamp_min is not None and value < clamp_min:
        value = clamp_min
    if full_scale <= 0:
        return 0.0
    ratio = value / full_scale
    if ratio < 0.0:
        return 0.0
    if ratio > 1.0:
        return 1.0
    return ratio


def ratio_to_voltage(ratio: float, vref_volts: float = 5.0) -> float:
    if ratio < 0.0:
        ratio = 0.0
    if ratio > 1.0:
        ratio = 1.0
    return ratio * vref_volts






