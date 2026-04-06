# Changelog

## v2.0.0 — Prague, 06.04.2026

### New features

- **Structural file analysis** (`file_analysis.py`): the program now validates the CSV file before importing data. It auto-detects encoding (UTF-8 with/without BOM, Windows-1250, Latin-1), delimiter (comma, semicolon, tab), and line endings. Issues are reported with three severity levels (ERROR, WARNING, INFO). If critical errors are found, the program stops with a clear diagnostic message instead of crashing with a Python traceback.

- **Leader name cleaning** (`data_cleaning.py`): a three-layer normalization pipeline for the leader name column reduces duplicate PDF generation caused by inconsistent data entry:
  - Layer 1 — Strip: removes leading/trailing whitespace and normalizes Unicode (NFC).
  - Layer 2 — Structural: merges surname-only entries with their full-name counterparts (e.g. "Radová" → "Hana Radová") and unifies reversed name order (e.g. "Anderle Vojtěch" → "Vojtěch Anderle").
  - Layer 3 — Fuzzy: catches typos and accent variants via Levenshtein distance (e.g. "Emma Ritterová" → "Ema Ritterová", "Vedralova" → "Vedralová"). Corrections are logged to the terminal.

- **Test runner** (`test/run_tests.sh`): automated test script that runs the program against every CSV in `data/` and saves the generated PDFs in separate folders under `test/output/` for manual inspection. Usage:
  - `bash test/run_tests.sh` — run all tests
  - `bash test/run_tests.sh clean` — remove all test output

### Breaking changes

- `data_import.py` no longer assigns column names by position. Columns are now identified by pattern matching on the original Moodle headers. This makes the program compatible with CSV files containing 16 or 17 columns (with or without the optional "Positive feedback" and "Group" columns).
- `creapdf()` in `pdfgen.py` now accepts an optional `output_dir` parameter (default: `"pdf"`).
- `data_import()` now accepts optional `encoding` and `delimiter` parameters.
- `main.py` accepts an optional `--output-dir` command-line argument.

### Bug fixes

- Fixed crash when the CSV contains rows with a missing leader name (`NaN`). These rows are now silently skipped.
- Fixed crash on leader names that are not strings (e.g. numeric values due to column misalignment) by adding explicit `str()` casts in `pdfgen.py`.
- Fixed encoding issues with UTF-8 BOM (`\xef\xbb\xbf`) by switching from `encoding='utf-8'` to `encoding='utf-8-sig'` as the default.
- Added `from __future__ import annotations` to all modules using modern type hints, ensuring compatibility with Python 3.9+.

## v1.0.0 — Prague, 03.04.2024

Initial release. Reads Moodle survey CSV files and generates one PDF feedback report per discussion leader, with Garamond typography.
