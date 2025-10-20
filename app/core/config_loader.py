from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import Any, Dict, Optional

import yaml  # type: ignore


@dataclass
class ChannelConfig:
    entity: str
    full_scale: float
    meter_type: str
    ema_alpha: float
    gain: float = 1.0
    offset: float = 0.0
    clamp_min: Optional[float] = None


@dataclass
class HardwareConfig:
    i2c_bus: int = 1
    mcp4725_address: int = 0x62
    vref_volts: float = 5.0


def load_yaml(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_channel_configs(path: pathlib.Path) -> Dict[str, ChannelConfig]:
    raw = load_yaml(path)
    result: Dict[str, ChannelConfig] = {}
    for key, cfg in (raw.get("channels") or {}).items():
        result[key] = ChannelConfig(
            entity=str(cfg.get("entity", key)),
            full_scale=float(cfg.get("full_scale", 1.0)),
            meter_type=str(cfg.get("meter_type", "voltage_0_5v")),
            ema_alpha=float(cfg.get("ema_alpha", 0.2)),
            gain=float(cfg.get("gain", 1.0)),
            offset=float(cfg.get("offset", 0.0)),
            clamp_min=float(cfg["clamp_min"]) if "clamp_min" in cfg else None,
        )
    return result


def load_hardware_config(path: pathlib.Path) -> HardwareConfig:
    raw = load_yaml(path)
    hw = raw.get("hardware") or {}
    return HardwareConfig(
        i2c_bus=int(hw.get("i2c_bus", 1)),
        mcp4725_address=int(hw.get("mcp4725_address", 0x62)),
        vref_volts=5.0,
    )






