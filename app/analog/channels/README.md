Channels

Each channel implements a uniform interface:
- init(config)
- update(value)  # clamp, EMA, gain/offset
- output()       # pushes to DAC/driver

Examples: PV, Daily Home, Battery SoC, House Load, Grid Buy.






