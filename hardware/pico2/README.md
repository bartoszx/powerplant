# Pico 2 – sterowanie MTR1_DATA z głównego RPi

Pico 2 odbiera komendy po UART od RPi i steruje linią **MTR1_DATA** (WS2812, 34 LEDy) na **GPIO6** oraz podświetleniem na GPIO11..15.

## Połączenia

| RPi (BCM) | Kierunek | Pico 2  | Opis        |
|-----------|----------|---------|-------------|
| BCM 14    | TXD →    | GPIO 1  | RX (we)     |
| BCM 15    | RXD ←    | GPIO 0  | TX (wy)     |
| GND       |          | GND     | wspólna masa|
| (opcjonalnie 3V3/5V) |   | VSYS / VBUS | zasilanie Pico |

**Pico GPIO 6** → **MTR1_DATA** (wejście danych taśmy WS2812 przy mierniku 1).  
**Pico GPIO 11..15** → podświetlenie mierników 1..5 (J5 spare).

## 1. Wgranie MicroPython na Pico 2

1. Pobierz firmware MicroPython dla RP2040:  
   https://micropython.org/download/RPI_PICO2/
2. Przytrzymaj BOOTSEL na Pico, podłącz USB, puść BOOTSEL – pojawi się dysk **RPI-RP2**.
3. Skopiuj na ten dysk plik **`.uf2`** z archiwum – Pico zrestartuje się z MicroPythonem.

## 2. Wgranie programu (main.py)

- Przez **Thonny** (lub inny REPL / mpremote): połącz się z Pico 2 przez USB i wgraj plik **`main.py`** do katalogu głównego (root) urządzenia.
- Albo przez **mpremote** (po `pip install mpremote`):
  ```bash
  mpremote connect /dev/ttyACM0 cp hardware/pico2/main.py :main.py
  mpremote connect /dev/ttyACM0 reset
  ```
- Po wgraniu **main.py** Pico przy starcie uruchomi nasłuch UART i sterowanie LEDami.

## 3. Podłączenie do RPi (bez USB)

- Odłącz Pico od USB.
- Zasil Pico z RPi (3V3 lub 5V – według Twojej konfiguracji) i połącz:
  - RPi **BCM14 (TXD)** → Pico **GPIO1 (RX)**
  - RPi **BCM15 (RXD)** ← Pico **GPIO0 (TX)**
  - **GND** – wspólna masa.
- Włącz RPi; Pico startuje z **main.py** i czeka na dane UART.

## 4. Test z RPi

Na głównym RPi (w katalogu projektu):

```bash
pip install pyserial pyyaml
python3 scripts/test_mtr1_via_pico.py --ping    # test łączności
python3 scripts/test_mtr1_via_pico.py          # miganie 34 LEDów
python3 scripts/test_mtr1_via_pico.py --fill 255 0 0   # cały pasek na czerwono
```

Port UART w configu: **config/hardware.yaml** → **pico2.serial.port** (domyślnie `/dev/serial0`). Na RPi 5 często to `/dev/ttyAMA0` lub symlink `/dev/serial0`.

## Protokół UART (RPi → Pico)

- **0xFF** – ping; Pico odpowiada jednym bajtem **0xFF**.
- **0x01** + **102 bajty** (34 × RGB) – ustawienie kolorów 34 LEDów (łuk) i odświeżenie (show).
- **0x02** + **1 B maska** + **3 B R,G,B** – podświetlenie: maska bit0..4 = MTR1..5 (1=on), kolor z R,G,B. Np. `0x02 0x01 100 180 255` = MTR1, niebiski.
- **0x03** – wszystkie podświetlenia OFF.
- **0x04** + **2 B długość (big-endian)** + **body** – OTA: zapis body do `main.py` na Pico i `soft_reset()` (max 16 KB).

Baud: **115200**, 8N1.

## Kolory (RGB vs GRB)

Większość taśm WS2812 ma **kolejność GRB** na drucie. W **main.py**:
- **Backlight** (GPIO11..15) – zawsze zapis (G,R,B), żeby (255,0,0) z hosta dawało czerwony.
- **Strip łuk** (GPIO6) – stała **MTR1_STRIP_GRB** (domyślnie `True`): host wysyła (R,G,B), Pico zapisuje (G,R,B) do NeoPixel.

Jeśli kolory na łuku się nie zgadzają z tym, co wysyła host (np. czerwony świeci na zielono, lub różne płytki 4-LED zachowują się inaczej), sprawdź:
1. **MTR1_STRIP_GRB** w main.py – ustaw `False`, wgraj OTA i przetestuj. Część taśm to RGB.
2. Jedna fizyczna taśma na wszystkich miernikach – wtedy kolejność jest taka sama; jeśli łączysz różne moduły (np. inne wersje WS2812/SK6812), mogą mieć różny order (RGB/GRB/BGR) i wtedy trzeba osobnej konfiguracji per-pin albo ujednolicić hardware.

## 5. OTA – aktualizacja main.py przez UART (bez USB)

Po **jednorazowym** wgraniu `main.py` przez USB (p. 2) możesz później aktualizować firmware **przez UART** z RPi:

```bash
python3 scripts/ota_pico_main.py
```

Skrypt wysyła zawartość `hardware/pico2/main.py` komendą 0x04. Pico zapisuje ją do `main.py` i restartuje się. Port z configu: **config/hardware.yaml** → **pico2.serial.port**.

**Uwaga:** Pierwsze wgranie `main.py` musi być przez USB (Thonny lub `mpremote cp ... :main.py`), żeby na Pico był kod z obsługą OTA. Potem aktualizacje możesz robić tylko przez UART.
