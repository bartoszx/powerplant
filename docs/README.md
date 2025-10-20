Docs

Include wiring diagrams, parts lists, calibration procedure, and screenshots of the retro console.






# 🧩 POWERPLANT – Struktura schematów KiCad (stan bieżący)

## 🟢 Główny arkusz
**Zawiera:**
- Raspberry Pi HAT (GPIO 40-pin)
- Magistrala **I²C** (SDA, SCL, +3V3, GND)
- Linie zasilania: **+3V3**, **+5V**, **+12V**, **GND**, **GNDPWR**
- Złącza / arkusze hierarchiczne:
  - `BLK_METER_LED`
  - `BLK_BUTTONS`
  - `BLK_SWITCH_MODES`
  - `BLK_SWITCH_DISPLAY`

---

## ⚙️ BLK_METER_LED
Obsługuje **5 mierników analogowych** + ich LED wskaźniki.

### Układy
- **U6, U7:** 74AHCT125 (4× buffer, 3.3V→5V poziomy logiczne)
- **U8:** ULN2803A (8× tranzystor NPN do LED 12V)
- **U9:** MCP23017 @0x20 (I/O expander 3.3V, I²C)
- **Złącze:** `J7 IDC-34 (METER_LED_BUS)`

### Połączenia
| Funkcja | Złącze IDC-34 | Układ | Opis |
|----------|---------------|--------|------|
| MTRx_DATA | 3/5/7/9/11 | U6/U7 | dane do LED-ringów (z 74AHCT125) |
| OUT_Mx_BL | 15/17/19/21/23 | ULN2803A | LED-backlight mierników |
| OUT_Mx_URAL | 25/27/29/31/33 | ULN2803A | lampki URAL 12V |
| BTN_*_SIG | 16/18/20/22 | MCP23017 | sygnały z przycisków (GATE/GARAGE/FENCE/DOOR) |
| OUT_*_LED | 24/26/28/30 | ULN2803A | LED przycisków (12V) |
| +12V | 13 | Zasilanie sekcji mocy |
| +5V | 1 | Zasilanie logiki LED |
| GND | 2/4/6/8/10/12/32 | Masa logiczna |
| GNDPWR | 34 | Masa mocy |

### Filtracja zasilania
- +5V: C21 = 100 µF (elektrolit), C22 = 0.1 µF (ceramiczny)
- +12V: C23 = 0.1 µF (ceramiczny), C24 = 100 µF (elektrolit)

---

## 🟡 BLK_BUTTONS
Obsługuje **4 przyciski** (GATE, GARAGE, FENCE, DOOR).

### Układy
- Współdzieli MCP23017 @0x20 (z BLK_METER_LED)
- LED 12V sterowane z ULN2803A (OUT3..OUT6)

### Połączenia
| Przycisk | Wejście (MCP) | LED (ULN IN) | LED (ULN OUT) |
|-----------|----------------|---------------|---------------|
| GATE | GPB2 | IN3 | OUT13 |
| GARAGE | GPB3 | IN4 | OUT14 |
| FENCE | GPB4 | IN5 | OUT15 |
| DOOR | GPB5 | IN6 | OUT16 |

Każdy przycisk:
- `BTN_*_SIG` → MCP23017 (z pull-up R=10k do 3.3V, C=100nF do GND)
- `OUT_*_LED` → ULN2803A → LED → +12V
- Zasilanie LED wspólne 12V

---

## 🟠 BLK_SWITCH_MODES
Obsługuje przełączniki krzywkowe i łopatkowe (tryby i strefy).

### Układ
- **U11:** MCP23017 @0x21 (3.3V, I²C)
- Wspólna filtracja: C28 = 0.1 µF (VDD↔GND)

### Mapowanie pinów
| MCP pin | Funkcja |
|----------|----------|
| GPA0–GPA4 | SW_MODE_P1–P5 (OFF, ANTI_GRID, BAT_SAVE, BLACKOUT, NORMAL) |
| GPA5–GPA7 | SW_RANGE_P1–P3 (LIVE, 1DAY, 7DAY) |
| GPB0–GPB3 | SW_RANGE_P4–P7 (14DAY, CUR_MONTH, M6, M12) |
| GPB4–GPB7 | ZONE1–ZONE4 (komendy strefowe) |

Każda linia:
- R=10k do +3V3
- C=100nF do GND
- Przełącznik zwiera sygnał do GND

Adres: A0=+3V3, A1=GND, A2=GND → I²C addr 0x21

---

## 🔵 BLK_SWITCH_DISPLAY
Obsługuje suwakowy 6-pozycyjny przełącznik wyboru temperatury.

### Układ
- **U12:** MCP23017 @0x22 (3.3V, I²C)
- GPA0–GPA5: `SW_TEMP_P1..P6`
  - OUTDOOR, SALON, GAB, MIB, HEL, OLA

Każda linia:
- R=10k do +3V3
- C=100nF do GND
- Styk wspólny przełącznika do GND

Adres: A0=GND, A1=GND, A2=+3V3 → I²C addr 0x22

---

## 🧲 Zasilanie i magistrale
| Sygnał | Opis |
|---------|------|
| +3V3 | z Raspberry Pi, zasilanie logiki i MCP |
| +5V | z Raspberry Pi, LED logiczne |
| +12V | z zasilacza, LED mocy i URAL |
| GND | masa logiczna |
| GNDPWR | masa mocy |
| SDA, SCL | magistrala I²C (3.3V), wspólna dla U9, U11, U12 |

---

## 🧩 Stan projektu
✅ Gotowe:
- BLK_METER_LED (mierniki + LEDy)
- BLK_BUTTONS (przyciski + podświetlenie)
- BLK_SWITCH_MODES (krzywkowe + łopatkowe)
- BLK_SWITCH_DISPLAY (suwakowy)

⏳ Kolejne bloki (do dodania później):
- BLK_NIXIE (wyświetlacz)
- BLK_CONSOLE (LCD, enkodery, mikrofon, czujnik światła)
- BLK_SPARE (rezerwa GPIO)
