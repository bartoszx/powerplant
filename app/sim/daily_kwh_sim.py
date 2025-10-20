#!/usr/bin/env python3
import time
from typing import Iterator


def ramp_daily_kwh(total_kwh: float, duration_s: float, step_s: float = 0.5) -> Iterator[float]:
    """Yield values from 0 → total_kwh over duration_s seconds."""
    steps = max(1, int(duration_s / step_s))
    for i in range(steps + 1):
        yield total_kwh * (i / steps)
        time.sleep(step_s)


def demo() -> None:
    fs_kwh = 18.0
    for v in ramp_daily_kwh(total_kwh=10.0, duration_s=20.0, step_s=0.5):
        ratio = min(1.0, max(0.0, v / fs_kwh))
        print(f"sim daily_kwh={v:.2f} → ratio={ratio:.3f}")


if __name__ == "__main__":
    demo()






