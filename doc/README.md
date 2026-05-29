# Dokumentacja modułu mierników

Katalog w repozytorium **powerplant** (`doc/`).

| Plik | Zastosowanie |
|------|----------------|
| [modul-miernikow-opis-schematu.md](modul-miernikow-opis-schematu.md) | Pełna dokumentacja (czytanie, review, git) |
| [modul-miernikow-wklejka-schemat.txt](modul-miernikow-wklejka-schemat.txt) | Skrót do wklejenia jako blok tekstu na schemacie KiCad |

**Pliki KiCad (źródło prawdy obwodu):**  
`~/Dropbox/kicad/powerplant/modul-miernikow.kicad_pro` (+ `.kicad_sch`, `.kicad_pcb`)

## Weryfikacja przez MCP (KiCAD MCP Server)

Opis obwodu w tych plikach jest uzgadniany z **rzeczywistym schematem** przy użyciu **Model Context Protocol** — serwera MCP podłączonego do KiCad (netlista, ERC/DRC, analiza połączeń).

**Protokół potwierdzania:**

1. Otwarcie / eksport netlisty z aktualnego `modul-miernikow.kicad_sch`.
2. Sprawdzenie połączeń sieci (J18, J1, U16, LM358, AO3400, 74AHCT125).
3. Uruchomienie ERC i DRC (`kicad-cli` lub narzędzia MCP).
4. Wynik weryfikacji wpisywany w sekcji *Weryfikacja MCP* w `modul-miernikow-opis-schematu.md`.

Przy kolejnych zmianach schematu — ponowna weryfikacja MCP i aktualizacja daty w opisie.

**Uwaga:** Stary blok tekstu na schemacie (MCP4728, 2N2222, URAL, GNDPWR) jest **nieważny** — zastąpić treścią z `modul-miernikow-wklejka-schemat.txt`.
