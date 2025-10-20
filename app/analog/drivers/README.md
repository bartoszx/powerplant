Drivers

Isolate hardware access:
- MCP4728 (4ch 0–5 V) and MCP4725 (1ch 0–5 V) via I²C
- Current drivers (LM358) for 0–1 mA meters
- No business logic here; expose simple set_output(channel, volts|milliamps)






