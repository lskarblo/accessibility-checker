# PowerPoint & PDF Accessibility Checker

En webbaserad applikation för automatisk tillgänglighetsanpassning av PowerPoint-presentationer (PPTX) och PDF-dokument enligt WCAG 2.1 AA, Microsoft Accessibility Guidelines och PDF/UA (ISO 14289).

## Funktioner

- **11 tillgänglighetsregler**:
  1. Struktur och läsordning
  2. Alt-texter (AI-genererade med Claude)
  3. Färg och kontrast (WCAG 4.5:1)
  4. Typsnitt och textformat
  5. Layouter och mallar
  6. Tabeller och diagram
  7. Multimedia
  8. Hyperlänkar
  9. Animationer och rörelser
  10. Rapportering
  11. Tekniska krav

- **Stöd för både PPTX och PDF**
- **AI-driven alt-text-generering** med Claude API
- **Human-in-the-loop** - användaren godkänner ändringar
- **Omfattande rapporter** i HTML/PDF format
- **OCR-support** för scanned PDFs

## Installation

### Förutsättningar

- Python 3.13+
- UV package manager
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (för scanned PDFs)

### Setup

1. Klona repository
2. Installera dependencies:
   ```bash
   uv sync
   ```

3. Skapa `.env` fil:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   STORAGE_ROOT=./storage
   HOST=localhost
   PORT=8000
   ```

4. Starta server:
   ```bash
   uv run uvicorn src.pptx_accessibility.api.app:app --reload
   ```

5. Öppna `http://localhost:8000` i webbläsaren

## Användning

1. Ladda upp en PPTX eller PDF-fil
2. Välj vilka regler som ska köras
3. Klicka "Start Analysis"
4. Granska fynden och godkänn/avvisa förändringar
5. Applicera godkända ändringar
6. Ladda ner förbättrad fil och rapport

## Teknisk stack

- **Backend**: Python 3.13, FastAPI
- **PPTX**: python-pptx
- **PDF**: pikepdf, pypdfium2, pytesseract
- **AI**: Anthropic Claude API
- **Frontend**: Vanilla HTML/CSS/JavaScript

## Utveckling

Kör tester:
```bash
uv run pytest
```

Formatera kod:
```bash
uv run black src/ tests/
uv run ruff check src/ tests/
```

## Licens

Copyright 2025 Capio Sankt Görans Sjukhus AB

