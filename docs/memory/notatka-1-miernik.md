# 📝 MCP4728 + analogowe mierniki  
**Projekt:** POWERPLANT / smartgun  
**Data:** 2026-02-08  

---

## 1. Konfiguracja sprzętowa
- DAC: **MCP4728**
- Adres I²C: **stały 0x60**
- Brak pinów adresowych (A0/A1) → brak możliwości zmiany adresu
- Zasilanie DAC: **~5 V**
- Wyjścia:
  - **VOUTA–D → LM358 → IRLZ44N → cewka miernika → Rsense → GND**
- Liczba mierników: **5**
  - 4 obsługiwane przez MCP4728
  - 5-ty wymaga osobnego rozwiązania

---

## 2. Kluczowe ustalenia
### ❌ Zmiana adresu MCP4728
- Nie da się zmienić adresu:
  - software’owo
  - przez EEPROM
  - przez LDAC / General Call
- Adres **0x60 jest zaszyty w krzemie**
- Wariant użyty na PCB **nie posiada pinów A0/A1**

➡️ **Dwa MCP4728 na jednej magistrali I²C bez muxa są niemożliwe**

---

## 3. Problemy początkowe i ich przyczyna
### 3.1 Zapis do DAC
- Biblioteka `adafruit_mcp4728` działała poprawnie
- Własny skrypt nie działał, ponieważ:
  - używał `SMBus.write_i2c_block_data()`
  - MCP4728 **nie obsługuje SMBus block write**
- Układ wymaga **RAW I²C (`i2c_rdwr`)**

➡️ Rozwiązanie: użycie **surowego zapisu I²C**

---

### 3.2 Ograniczenie napięcia do ~2 V
- MCP4728 miał zapisane w EEPROM:
  - **VREF = internal 2.048 V**
  - **GAIN = x1**
- Tryb Fast Write **nie zmienia VREF/GAIN**

➡️ Rozwiązanie:
- użycie **Multi-Write Input Register (0x40)**
- ustawienie:
  - `VREF = internal`
  - `GAIN = x2`

➡️ Efekt:
- **pełna skala ~4.9 V na VOUT**

---

## 4. Finalna konfiguracja DAC (działająca)
- Skala: **0–4095**
- Konfiguracja:
  - `VREF = internal`
  - `GAIN = x2`
- Efektywne napięcie wyjściowe: **~0–5 V**
- Uznana jako konfiguracja docelowa

---

## 5. Diagnostyka toru miernika
### Punkty pomiarowe
- **VOUTA MCP4728**  
  - stabilne napięcie DC  
  - poprawna praca DAC
- **Wyjście do miernika (IDC-10)**  
  - skoki napięcia  
  - overshooty  
  - wartości > VREF

➡️ Jest to **normalne**, ponieważ:
- miernik = indukcyjność
- pętla: LM358 + MOSFET + cewka
- brak tłumienia powoduje oscylacje
- multimetr pokazuje wartości uśrednione

---

## 6. Wnioski sprzętowe
- DAC działa poprawnie
- Oprogramowanie działa poprawnie
- MOSFET (IRLZ44N) działa poprawnie
- Miernik reaguje

❗ Główny problem: **niestabilna pętla prądowa**

---

## 7. Zalecane poprawki hardware
1. **Dioda flyback** równolegle do cewki miernika  
   (np. 1N4148 / dioda Schottky)
2. **Kondensator filtrujący na SENSE_A → GND**
   - start: **100 nF**
   - w razie potrzeby: 220–470 nF
3. Opcjonalnie:
   - RC na Gate MOSFETa (np. 10–47 nF)

---

## 8. Zalecenia software
- Nie używać pełnej skali 0–4095
  - typowo: **0–600 / 0–1200**
- Wolne rampy:
  - `step = 5–10`
  - `delay = 20–30 ms`
- Miernik analogowy ma wolną mechanikę

---

## 9. Problem 5. miernika – decyzje architektoniczne
Ponieważ:
- MCP4728 ma **tylko jeden adres (0x60)**
- liczba mierników > liczba kanałów DAC

### Realne opcje:
1. ✅ **I²C multiplexer TCA9548A**
2. ✅ **PWM + filtr RC** dla 5-tego miernika
3. ❌ Zmiana adresu MCP4728 (niemożliwe)

---

## 10. Stan końcowy
- Układ działa poprawnie
- Skala DAC opanowana
- Przyczyna problemów zidentyfikowana
- Projekt gotowy do dalszej rozbudowy