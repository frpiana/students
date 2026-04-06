# students — CSV to PDF feedback reports

Converts Moodle survey CSV files into individual PDF feedback reports for each discussion leader.

## Target of the program

The program is designed for CSV files exported from the Moodle learning management system as survey results ("Discussion Leading Feedback"). The CSV files are expected to be in Czech-locale format.

The program automatically identifies the required columns by matching patterns in the header names, making it compatible with different Moodle export variants. The following columns are **required** (the header must contain the keyword):

| Keyword             | Description                          |
|---------------------|--------------------------------------|
| `Leader name`       | Name of the discussion leader        |
| `Preparation`       | Score: leader was well-prepared      |
| `Introduction`      | Score: clear topic introduction      |
| `Inclusion`         | Score: everyone participated         |
| `Fav question`      | Open: most interesting question      |
| `What learned`      | Open: one thing learned              |
| `Negative feedback` | Open: what could be improved         |
| `ID`                | Student identifier (for dedup)       |

The following columns are **optional** and will be recognized if present: `Group`, `Positive feedback`.

Other Moodle metadata columns (Odpověď, Odesláno, Instituce, etc.) are recognized and ignored.

## How to install

### Option 1: Windows executable

Download _students.exe_ from the [release page](https://github.com/frpiana/students/releases/) and place it in a folder without spaces in the path, for example: `C:\Users\user_name\Documents\executables`.

Add the folder to your `PATH` environment variable: search for "Edit the system environment variables for your account", select the `Path` variable, click _Edit_, then _New_, and paste the folder path.

### Option 2: Run from source

Requires Python 3.9 or later. Install the dependencies:

```bash
pip install -r requirements.txt
```

## How to use

Navigate to the folder containing the CSV file and run:

```bash
students
```

or, when running from source:

```bash
python src/students/main.py
```

The program will:

1. Ask for the CSV file name.
2. Perform a structural analysis of the file (encoding, delimiter, column validation) and report any issues.
3. Clean and normalize the leader names to avoid duplicate PDFs caused by inconsistent data entry (e.g. surname-only vs. full name, reversed name order, typos).
4. Generate one PDF per leader in a `pdf/` subfolder.

### File analysis

Before importing data, the program checks the CSV for:

- Encoding (UTF-8 with/without BOM, Windows-1250, Latin-1 — auto-detected)
- Delimiter (comma, semicolon, tab — auto-detected)
- Missing or duplicate columns
- Non-numeric values in score columns (expected: 1–5)
- Empty or malformed rows

Issues are classified as ERROR (blocks execution), WARNING (may cause imprecise results), or INFO (informational).

### Name cleaning

The program applies three layers of normalization to the leader name column:

1. **Strip**: removes whitespace and normalizes Unicode.
2. **Structural**: merges surname-only entries with full names and unifies reversed name order.
3. **Fuzzy**: catches typos and accent variants using Levenshtein distance.

All corrections are logged to the terminal.

## Testing

A test runner is included. From the project root:

```bash
# Run all tests (generates PDFs in test/output/)
bash test/run_tests.sh

# Clean test output
bash test/run_tests.sh clean
```

The test runner executes the program on each CSV in the `data/` folder and saves the generated PDFs in separate subfolders under `test/output/` for manual inspection.

## Project structure

```
students/
├── src/
│   ├── fonts/              # Garamond font files
│   └── students/
│       ├── main.py             # Entry point
│       ├── file_analysis.py    # CSV structural validation
│       ├── data_import.py      # Column mapping and import
│       ├── data_cleaning.py    # Leader name normalization
│       ├── pdfgen.py           # PDF generation
│       ├── styles.py           # Garamond paragraph styles
│       ├── file_request.py     # Input file validation
│       └── notifications.py    # Terminal messages
├── data/                   # Test CSV files
├── test/
│   ├── run_tests.sh        # Automated test runner
│   └── output/             # Generated test PDFs
├── dist/                   # Compiled executable
├── CHANGELOG.md
├── README.md
├── requirements.txt
├── build.bat
└── students.spec
```

## License

MIT — see [LICENCE](LICENCE).
