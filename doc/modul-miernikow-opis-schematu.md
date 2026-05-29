# Moduł sterowania miernikami — opis schematu

**Projekt KiCad:** `modul-miernikow.kicad_pro`  
**Pliki KiCad:** `~/Dropbox/kicad/powerplant/`  
**Dokumentacja (git):** `powerplant/doc/` (ten katalog)  
**Skrót do schematu:** [modul-miernikow-wklejka-schemat.txt](modul-miernikow-wklejka-schemat.txt)

---

## Weryfikacja MCP (KiCAD MCP Server)

Ten dokument opisuje **aktualny schemat**, nie historyczny blok tekstu (MCP4728 / 2N2222 / URAL).

| Pole | Wartość |
|------|---------|
| Metoda | Model Context Protocol — KiCAD MCP Server + `kicad-cli` |
| Źródło prawdy | `modul-miernikow.kicad_sch`, netlista, ERC/DRC |
| Zakres | Połączenia J18, J1, U16, LM358, AO3400, 74AHCT125; mapa DAC; brak zwarcia nazw sieci krytycznych |
| Ostatnia weryfikacja | 2026-05-25 |
| DRC | 0 naruszeń (`modul-miernikow.kicad_pcb`) |
| ERC | 12 ostrzeżeń (biblioteka LM358, etykiety ML vs `J_METER_PLUS_MINUS+`, global/local labels) — **0 błędów** |
| Potwierdzenie toru A | Wizualnie w KiCad zgodne z opisem poniżej (użytkownik) |

**Przy zmianie schematu:** ponów eksport netlisty, ERC/DRC przez MCP lub `kicad-cli`, zaktualizuj tabelę powyżej i [modul-miernikow-wklejka-schemat.txt](modul-miernikow-wklejka-schemat.txt).

---

## 1. Rola modułu

Moduł **nie** jest pojedynczym miernikiem. To **jedna płyta** obsługująca **wszystkie 5 mierników** oraz komunikująca się z **płytą główną** (RPi5, Pico, przetwornica buck).

Na każdy miernik wychodzi osobny przewód (GX8 → terminal → moduł miernika), agregowany na płytce modułu w złączu **IDC-34 (J1)**.

Każdy miernik ma:

- sterowanie wskazówką (cewka),
- zasilanie i sterowanie LEDów sekcji: **DATA_LIGHT**, **DATA_SCALE**, **DATA_MODE** (w schemacie sieci `MTR_KWH_*` / `GPIO_KWH_*`).

---

## 2. Architektura połączeń

```text
Płyta główna (RPi5, Pico, buck)
        │
        ├── J18 EDGE 2×12 ── +5V, +12V, GND, I2C_SDA/SCL, GPIO_LIGHT/SCALE/KWH
        │                      │
        │                      ▼
        │              [ moduł mierników ]
        │                 U16 DAC7578
        │                 U2,U3,U10 LM358 + Q7..Q12 AO3400
        │                 U1,U4..U7 74AHCT125
        │
        └── (masa wspólna z modułem)

        J1 IDC-34 ──► mierniki 1..5 (cewka + LED DATA + +5V/GND)
```

**Założenie dokumentacyjne:** wszystko, co jest na **J18**, ma kontynuację na płycie głównej (zasilanie, I²C, GPIO).

**J1** to wyłącznie **wyjście na wiązki mierników** w terenie.

---

## 3. Złącza

### J18 — `EDGE` (2×12, do płyty głównej)

| Pin J18 | Sieć | Funkcja |
|---------|------|---------|
| 1, 2 | +5V | Zasilanie logiki |
| 3, 4, 6, 24 | GND | Masa |
| 5 | +12V | Zasilanie toru analogowego (cewki) |
| 7 | I2C_SDA | → U16 DAC7578 |
| 8 | I2C_SCL | → U16 DAC7578 |
| 9 | GPIO_LIGHT_1 | → U1 (74AHCT) |
| 10 | GPIO_SCALE_1 | → U1 |
| 11 | GPIO_KWH_1 | → U1 |
| 12–23 | GPIO_* 2..5 | → U4, U5, U6, U7 |

### J1 — `IDC-34_METER_SIG_OUT` (2×17, do mierników)

Patrz sekcja 7 i plik [modul-miernikow-wklejka-schemat.txt](modul-miernikow-wklejka-schemat.txt).

**+12 V nie występuje na J1** — cewki zasilane z modułu przez rezystory limitujące od szyny +12 V (wejście +12 V z J18).

---

## 4. Układy scalone

| Ref | Typ | Ilość | Funkcja |
|-----|-----|-------|---------|
| U16 | DAC7578xPW | 1 | 8-kanałowy DAC, I²C, sterowanie napięciem torów wskazówki |
| U2, U3, U10 | LM358 | 3 | Wzmacniacze — po 2 kanały na układ |
| Q7–Q12 | AO3400A | 6 | N-MOSFET low-side, przełączanie zwrotu cewki |
| U1, U4, U5, U6, U7 | 74AHCT125 | 5 | Bufor 3-state, LED DATA → J1 |

**Nie używane:** MCP4728, tranzystory NPN 2N2222, ULN2803/URAL w tym module.

---

## 5. Tor analogowy — wskazówka

### Wzorzec (kanały A–E2)

```text
DAC7578 VOUTx
    │
    R 10 kΩ
    ├── VIN_FILT_x ──► (+) wejście LM358
    └── 4,7 µF + 100 nF ──► GND

LM358 (−) ◄── SENSE_x ◄── source AO3400
              └── C ~680 pF (między wyjściem opampa a SENSE)
              └── R_SENSE do GND (wartość zależna od kanału)

LM358 wyjście ── R 100 Ω ── bramka AO3400 (Rgate)
                      └── Rpd 100 kΩ do GND

+12 V ── Rlimit ──► J1 "+" (strona cewki w mierniku)
AO3400 drain ──► J1 zwrot ("-" / ML / MR)
```

### Mapowanie DAC → miernik

| Kanał | DAC U16 | Sieć filtra | MOSFET | J1 | Typ miernika |
|-------|---------|-------------|--------|-----|--------------|
| A | VOUTA (4) | VIN_FILT_A | Q7 | 1 (+), 2 (−) | jednostronny, 25 µA |
| B | VOUTB (13) | VIN_FILT_B | Q8 | 3 (+), 4 (−) | jednostronny, 5 mA |
| C | VOUTC (5) | VIN_FILT_C | Q9 | 5 (+), 6 (−) | jednostronny, 1 A |
| D | VOUTD (12) | VIN_FILT_D | Q10 | 7 (+), 8 (−) | jednostronny, TBC |
| E1 (ML) | VOUTE (6) | VIN_FILT_E1 | Q11 | 9 (ML) | ± lewo |
| E2 (MR) | VOUTF (11) | VIN_FILT_E2 | Q12 | 10 (MR) | ± prawo |

- **ML** = Miernik Left  
- **MR** = Miernik Right  
- Na fragmencie schematu może występować też etykieta `J_METER_PLUS_MINUS+` — **ta sama sieć co ML** (ERC: unikać duplikacji nazw).

**Nieużywane wyjścia DAC:** VOUTG, VOUTH (NC).

**LDAC (U16 pin 1) → GND** — aktualizacja wyjść DAC bez osobnego strobe.  
**ADDR0 (U16 pin 2) → GND** — bit adresu I²C (pełny adres w datasheet + kod Pico).

### Rezystory SENSE (kalibracja)

| Kanał | RSENSE (do GND z SENSE) | Uwaga |
|-------|-------------------------|--------|
| A | 200 kΩ | bias / słaba pętla prądowa w klasycznym sensie |
| B | 140 kΩ | jw. |
| C | 500 Ω | |
| D | 200 kΩ | |
| E1, E2 | 820 Ω | sensowniejszy zwrot dla ± |

Kalibracja prądu cewki **per kanał** w firmware i przy bring-up.

### Miernik ± (środek wskazówki)

- **4 mierniki** — wychylenie jednostronne (A–D).  
- **1 miernik** — wychylenie **+ / −** od środka: osobno **ML** i **MR**, dwa kanały DAC i dwa MOSFETy.  
- R29, R30 = **10 Ω** do +12 V (inna skala niż Rlimit 100 kΩ na torach A–D).

---

## 6. Tor LED

```text
Pico GPIO (J18) → wejście 74AHCT125 → wyjście → R 68 Ω → J1 MTR_* → miernik
```

| Miernik | LIGHT | SCALE | MODE (KWH) |
|---------|-------|-------|------------|
| 1 | J1-11 | J1-12 | J1-13 |
| 2 | J1-14 | J1-15 | J1-16 |
| 3 | J1-17 | J1-18 | J1-19 |
| 4 | J1-20 | J1-21 | J1-22 |
| 5 | J1-23 | J1-24 | J1-25 |

Zasilanie LED w miernikach: **+5 V** (J1: 27, 29, 31, 33), **GND** (26, 28, 30, 32, 34).

### 74AHCT125 — OE i kierunek

- **VCC = 5 V**  
- Kierunek: **host → bufor → J1** (Pico na płycie głównej steruje wejściami A)  
- **OE aktywne LOW:** kanał 1 OE (pin 1) → +5 V (**wyłączony**); OE kanałów 2–4 → GND (**włączone**)  
- Nieużywane piny 2–3 (1A, 1Y) — `no_connect`

---

## 7. Pełna mapa J1 (IDC-34)

| Pin | Sieć | Opis |
|-----|------|------|
| 1 | J_METER_25uA+ | + cewka, kanał A |
| 2 | METER- | zwrot Q7 |
| 3 | J_METER_5mA+ | + cewka, kanał B |
| 4 | (zwrot Q8) | − cewka B |
| 5 | J_METER_1A+ | + cewka, kanał C |
| 6 | (zwrot Q9) | − cewka C |
| 7 | J_METER_TBC+ | + cewka, kanał D |
| 8 | (zwrot Q10) | − cewka D |
| 9 | ML / J_METER_PLUS_MINUS+ | + strona ± |
| 10 | MR | − strona ± (Q12) |
| 11–25 | MTR_LIGHT/SCALE/KWH 1..5 | LED po buforze |
| 26–34 | GND / +5V | zasilanie szynowe mierników |

---

## 8. Zasilanie i masa

| Szyna | Źródło | Konsumenci na module |
|-------|--------|----------------------|
| +5V | J18 | DAC, 74AHCT, kondensatory odsprzęgania |
| +12V | J18 pin 5 | Rlimit cewek, LM358 (pin 8), kondensatory C3/C4… |
| GND | J18 + J1 | wspólna masa analog + cyfra |

**GNDPWR** — nie występuje; jedna sieć **GND**.

---

## 9. Odsprzęganie (skrót)

- Każdy kanał DAC: **10 kΩ + 4,7 µF + 100 nF** do GND.  
- +12 V: **100 nF + 10 µF** (C3, C4, …).  
- DAC U16 i 74AHCT: grupa kondensatorów przy **+5 V** (C16, C55, C56, C74–C83).  
- LM358: **~680 pF** między wyjściem a SENSE (stabilizacja pętli).

---

## 10. PCB (stan na dzień weryfikacji MCP)

- Wymiary płyty: ~121 × 68 mm  
- DRC: **0** naruszeń  
- Via: drill 0,3 mm / 0,6 mm — nadaje się do ręcznego przewlekania  
- **Test points:** TP1–TP14 na schemacie (sekcja poniżej); footprint `TestPoint_Pad_D1.0mm` — po **Update PCB** (F8)

### Test points (TP1–TP14)

Panel po lewej stronie schematu (etykieta „TEST POINTS”); footprint: `TestPoint:TestPoint_Pad_D1.0mm`.

| Ref | Sieć | Ref | Sieć |
|-----|------|-----|------|
| TP1 | VIN_FILT_A | TP8 | SENSE_B |
| TP2 | VIN_FILT_B | TP9 | SENSE_C |
| TP3 | VIN_FILT_C | TP10 | SENSE_D |
| TP4 | VIN_FILT_D | TP11 | SENSE_E1 |
| TP5 | VIN_FILT_E1 | TP12 | SENSE_E2 |
| TP6 | VIN_FILT_E2 | TP13 | +5V |
| TP7 | SENSE_A | TP14 | +12V |

---

## 11. Bring-up (po wytrawieniu płytki)

Kolejność pierwszego uruchomienia na stole:

1. Zasilanie J18 (+5 V, +12 V, GND) — bez zwarcia.  
2. I²C — wykrycie DAC7578, odczyt rejestru.  
3. Kanał A — mały kod DAC, pomiar `VIN_FILT_A`, opcjonalnie cewka / obciążenie zamiast miernika.  
4. Kanały B, C, D po kolei.  
5. ± ML / MR — osobno E1 i E2.  
6. Jedna linia LED (np. `MTR_LIGHT_1`).  
7. Podłączenie J1 → 5 mierników.

---

## 12. Historia zmian dokumentacji

| Data | Zmiana |
|------|--------|
| 2026-05-25 | Utworzenie w `powerplant/doc/`; weryfikacja MCP; zastąpienie opisu MCP4728/URAL/NPN |
| 2026-05-25 | TP1–TP14 na schemacie (VIN_FILT, SENSE, +5V, +12V) |

---

## Powiązane pliki

- [README.md](README.md) — ten katalog  
- [modul-miernikow-wklejka-schemat.txt](modul-miernikow-wklejka-schemat.txt) — wklejka na schemat KiCad
