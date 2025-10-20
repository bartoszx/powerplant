#!/usr/bin/env python3
import pathlib
import signal
import sys
from contextlib import suppress

from app.analog.channels.daily_home import DailyHomeChannel
from app.core.config_loader import load_channel_configs, load_hardware_config
from app.sim.daily_kwh_sim import ramp_daily_kwh


ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    cfg_channels = load_channel_configs(ROOT / "config" / "channels.yaml")
    cfg_hw = load_hardware_config(ROOT / "config" / "hardware.yaml")
    daily_cfg = cfg_channels["daily_home"]

    chan = DailyHomeChannel(daily_cfg, cfg_hw)

    stop = False

    def handle_sigint(signum, frame):  # noqa: ARG001
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGTERM, handle_sigint)

    try:
        for value in ramp_daily_kwh(total_kwh=10.0, duration_s=20.0, step_s=0.5):
            volts = chan.update_and_output(value)
            print(f"daily={value:.2f} kWh → {volts:.3f} V")
            if stop:
                break
    finally:
        with suppress(Exception):
            chan.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())






