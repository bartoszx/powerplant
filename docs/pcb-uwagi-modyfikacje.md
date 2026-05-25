# Uwagi i planowane modyfikacje PCB (BLK_METER_LED, złącza)

Plik zbiera wymagania i uwagi do kolejnej rewizji płytki / zmian w okablowaniu.

---

## 1. MCP23017 – adresy I²C i sterowanie 5 miernikami

**Problem:** Rozszerzacze I/O (MCP23017) mają ten sam adres I²C, przez co nie da się niezależnie sterować wszystkimi 5 miernikami.

**Wymaganie:** Zmienić podejście do MCP tak, aby:
- każdy miernik (MTR1..MTR5) mógł być sterowany osobno,
- na I²C były unikalne adresy (np. różne A0/A1/A2 lub osobne układy z różnymi adresami).

**Uwagi do projektu:** Sprawdzić schemat BLK_METER_LED – które MCP sterują OUT_Mx_BL / OUT_Mx_URAL; zaproponować nowy podział adresów (np. 0x20, 0x21, …) i ewentualnie dodatkowe piny adresowe na PCB.

---

## 2. Jedno złącze na obsługę wszystkich mierników (wskaźówka + LED)

**Problem:** Obecnie sygnały są rozbite na wiele złączy – wskaźówka (DAC/cewka) w jednym, dane LED (MTRx_DATA) w innym, podświetlenie (J5 spare) osobno itd.

**Wymaganie:** Jedno gniazdo (lub jeden zestaw złączy) do obsługi wszystkich mierników:
- wskaźówka (analog / DAC),
- LED (łuk / pasek WS2812),
- podświetlenie (WS2812),

tak aby jeden kabel / jedna wtyczka obsługiwała cały miernik (albo wszystkie mierniki z jednego, czytelnego złącza).

**Uwagi do projektu:** Zdefiniować pinout tego złącza (zasilanie, GND, DATA_WS2812, DAC/cewka, ewent. wspólne linie) i przenieść go na PCB zamiast rozproszonych J5/MTRx_DATA itd.

---

## 3. Podświetlenie miernika – z LED na programowalne (WS2812)

**Stan:** Podświetlenie miernika zostało zmienione ze zwykłego LED na taśmę/pasek programowalny (WS2812).

**Konsekwencje:**
- Sterowanie jest przez linię danych (np. Pico GPIO11..15 → J5 spare), nie przez proste ON/OFF z MCP (OUT_Mx_BL).
- W firmware (Pico `main.py`): BACKLIGHT_PINS = [11, 12, 13, 14, 15], BACKLIGHT_LED_COUNTS (np. 2, 2, 40, 40, 40).
- Na PCB: sygnały podświetlenia to MTRx_DATA (lub odpowiedniki na J5), buforowane 3.3 V → 5 V (74AHCT125), z rezystorami szeregowymi (np. 68 Ω).

**Uwagi do projektu:** W następnej wersji PCB:
- potwierdzić, że podświetlenie jest wyłącznie WS2812 (bez równoległego sterowania przez MCP OUT_Mx_BL, chyba że celowo zostawione jako enable),
- ewentualnie uprościć opis w schemacie („podświetlenie = WS2812”) i dopasować nazewnictwo netów/złączy.

---

## Podsumowanie

| # | Temat | Cel |
|---|--------|-----|
| 1 | MCP23017 | Unikalne adresy I²C, sterowanie 5 miernikami |
| 2 | Złącza | Jedno gniazdo na miernik (wskaźówka + LED + podświetlenie) |
| 3 | Podświetlenie | Ujęcie w dokumentacji przejścia z LED na WS2812 |

---

*Ostatnia aktualizacja: na podstawie uwag użytkownika.*
