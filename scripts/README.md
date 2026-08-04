# SBI TT BUY rate extraction

Builds a single wide CSV (`data/sbi_tt_buy_rates.csv`) — one row per date, one
column per currency — from the SBI forex rate card PDFs published daily at
[sahilgupta/sbi-fx-ratekeeper](https://github.com/sahilgupta/sbi-fx-ratekeeper).

```bash
pip install -r requirements.txt

# One-off backfill from a local clone of sbi-fx-ratekeeper
python extract_sbi_rates.py scan --pdf-dir /path/to/sbi-fx-ratekeeper/pdf_files

# Fetch a specific day (or today, if --date is omitted) directly from GitHub
python extract_sbi_rates.py download [--date YYYY-MM-DD]
```

Only dates missing from the output CSV are (re)processed by default; pass
`--full` to reprocess dates that are already present.

The `daily-sbi-rates` GitHub Action runs `download` daily and commits the
updated CSV back to this repo.
