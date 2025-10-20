from __future__ import annotations

from dataclasses import dataclass

from app.analog.drivers.mcp4725 import Mcp4725, Mcp4725Config
from app.analog.mapping.scale import clamp_ratio, ratio_to_voltage
from app.analog.smoothing.ema import ema_update
from app.core.config_loader import ChannelConfig, HardwareConfig


@dataclass
class DailyHomeChannel:
    chan_cfg: ChannelConfig
    hw_cfg: HardwareConfig
    _ema_value: float = 0.0

    def __post_init__(self) -> None:
        self._dac = Mcp4725(Mcp4725Config(
            i2c_bus=self.hw_cfg.i2c_bus,
            i2c_address=self.hw_cfg.mcp4725_address,
            vref_volts=5.0,
        ))
        # start at 0V
        self._dac.set_voltage(0.0)

    def close(self) -> None:
        self._dac.set_voltage(0.0)
        self._dac.close()

    def update_and_output(self, value_kwh: float) -> float:
        # Smooth value
        self._ema_value = ema_update(self._ema_value, value_kwh, self.chan_cfg.ema_alpha)
        # Apply clamp, ratio and calibration
        ratio = clamp_ratio(self._ema_value, self.chan_cfg.full_scale, self.chan_cfg.clamp_min)
        ratio = max(0.0, min(1.0, ratio * self.chan_cfg.gain + self.chan_cfg.offset))
        volts = ratio_to_voltage(ratio, vref_volts=5.0)
        self._dac.set_voltage(volts)
        return volts






