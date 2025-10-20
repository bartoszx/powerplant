from __future__ import annotations

from dataclasses import dataclass


try:
    import smbus2  # type: ignore
except Exception as exc:  # pragma: no cover - helpful message on non-RPi
    raise RuntimeError(
        "smbus2 is required on RPi. Install with: pip install smbus2"
    ) from exc


@dataclass
class Mcp4725Config:
    i2c_bus: int = 1
    i2c_address: int = 0x62  # default ADR for many MCP4725 boards
    vref_volts: float = 5.0   # powered from 5 V rail


class Mcp4725:
    """Minimal MCP4725 driver using FAST MODE write (12-bit DAC).

    Note: FAST MODE write is two bytes [D11..D4, D3..D0<<4].
    """

    def __init__(self, config: Mcp4725Config) -> None:
        self._cfg = config
        self._bus = smbus2.SMBus(config.i2c_bus)

    def close(self) -> None:
        try:
            self._bus.close()
        except Exception:
            pass

    def set_voltage(self, volts: float) -> None:
        """Set output voltage 0..Vref using 12-bit resolution.

        Clamps volts to [0, vref].
        """
        v = max(0.0, min(self._cfg.vref_volts, volts))
        dac_max = 4095
        code = int(round((v / self._cfg.vref_volts) * dac_max))
        # FAST MODE payload (2 bytes): MSB = D11..D4, LSB = D3..D0<<4
        msb = (code >> 4) & 0xFF
        lsb = (code & 0x0F) << 4
        self._bus.write_i2c_block_data(self._cfg.i2c_address, msb, [lsb])






