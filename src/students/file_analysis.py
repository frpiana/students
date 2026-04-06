"""
Modulo di analisi strutturale dei file CSV in ingresso.

Esegue una batteria di controlli prima dell'importazione dati e restituisce
un report con tre livelli di severità:
  - ERROR   : il file non può essere processato senza intervento
  - WARNING : anomalia che potrebbe causare risultati imprecisi
  - INFO    : osservazione utile, nessun impatto sul funzionamento

Il modulo tenta anche di auto-rilevare encoding e delimitatore per rendere
l'importazione il più robusta possibile.
"""

from __future__ import annotations
import csv
import os
from dataclasses import dataclass, field
from enum import Enum
from io import StringIO


# ---------------------------------------------------------------------------
# Tipi
# ---------------------------------------------------------------------------

class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class Issue:
    severity: Severity
    category: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.value:7s}] {self.category}: {self.message}"


@dataclass
class AnalysisReport:
    """Risultato dell'analisi strutturale."""
    file_path: str
    encoding: str = "utf-8"
    delimiter: str = ","
    quotechar: str = '"'
    has_bom: bool = False
    line_ending: str = "LF"
    num_rows: int = 0
    num_columns: int = 0
    headers: list[str] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def is_valid(self) -> bool:
        """True se non ci sono errori bloccanti."""
        return len(self.errors) == 0

    def print_report(self) -> None:
        """Stampa il report a schermo."""
        print(f"\n{'='*50}")
        print(f" Analisi strutturale: {os.path.basename(self.file_path)}")
        print(f"{'='*50}")
        print(f"  Encoding    : {self.encoding} (BOM: {'sì' if self.has_bom else 'no'})")
        print(f"  Delimitatore: {repr(self.delimiter)}")
        print(f"  Fine riga   : {self.line_ending}")
        print(f"  Colonne     : {self.num_columns}")
        print(f"  Righe dati  : {self.num_rows}")

        if not self.issues:
            print(f"\n  ✓ Nessun problema rilevato.")
        else:
            for sev in (Severity.ERROR, Severity.WARNING, Severity.INFO):
                group = [i for i in self.issues if i.severity == sev]
                if group:
                    print()
                    for issue in group:
                        print(f"  {issue}")

        status = "VALIDO" if self.is_valid else "NON VALIDO — correggere gli errori"
        print(f"\n  Stato: {status}")
        print(f"{'='*50}\n")


# ---------------------------------------------------------------------------
# Pattern delle colonne attese (riutilizzati da data_import)
# ---------------------------------------------------------------------------

# Le colonne "essenziali" che il programma deve trovare per poter generare i PDF
REQUIRED_PATTERNS: dict[str, list[str]] = {
    "ID":                  ["ID uživatele", "ID"],
    "Leader_name":         ["Leader name", "Leader"],
    "Preparation":         ["Preparation"],
    "Introduction":        ["Introduction"],
    "Inclusion":           ["Inclusion"],
    "Fav_question":        ["Fav question"],
    "What_learned":        ["What learned"],
    "Negative_feedback":   ["Negative feedback"],
}

# Colonne facoltative (presenti solo in alcune varianti del sondaggio)
OPTIONAL_PATTERNS: dict[str, list[str]] = {
    "Group":               ["Group"],
    "Positive_feedback":   ["Positive feedback"],
}


def _match_column(header: str, patterns: list[str]) -> bool:
    h = header.lower()
    return any(p.lower() in h for p in patterns)


# ---------------------------------------------------------------------------
# Rilevamento encoding
# ---------------------------------------------------------------------------

def _detect_encoding(raw_bytes: bytes) -> tuple[str, bool]:
    """Rileva encoding e presenza del BOM. Restituisce (encoding, has_bom)."""
    # BOM UTF-8
    if raw_bytes[:3] == b'\xef\xbb\xbf':
        return "utf-8-sig", True

    # BOM UTF-16
    if raw_bytes[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return "utf-16", True

    # Prova UTF-8 diretto
    try:
        raw_bytes.decode("utf-8")
        return "utf-8", False
    except UnicodeDecodeError:
        pass

    # Prova Windows-1250 (comune per testi cechi)
    try:
        raw_bytes.decode("windows-1250")
        return "windows-1250", False
    except UnicodeDecodeError:
        pass

    # Prova Latin-1 (accetta tutto, fallback)
    return "latin-1", False


# ---------------------------------------------------------------------------
# Rilevamento delimitatore
# ---------------------------------------------------------------------------

def _detect_delimiter(text: str) -> str:
    """Rileva il delimitatore analizzando la prima riga."""
    first_line = text.split("\n", 1)[0]

    # Conta le occorrenze dei candidati
    candidates = {
        ",":  first_line.count(","),
        ";":  first_line.count(";"),
        "\t": first_line.count("\t"),
    }

    # Anche csv.Sniffer come conferma
    try:
        dialect = csv.Sniffer().sniff(first_line, delimiters=",;\t")
        sniffed = dialect.delimiter
    except csv.Error:
        sniffed = None

    # Il delimitatore è quello con più occorrenze, con conferma dallo sniffer
    best = max(candidates, key=candidates.get)

    if candidates[best] == 0:
        # Nessun delimitatore trovato
        return ","

    if sniffed and sniffed == best:
        return best

    # Se sniffer e conteggio discordano, fidarsi del conteggio
    return best


# ---------------------------------------------------------------------------
# Rilevamento fine riga
# ---------------------------------------------------------------------------

def _detect_line_ending(raw_bytes: bytes) -> str:
    if b'\r\n' in raw_bytes:
        # Controlla se ci sono anche \n puri (mixed)
        stripped = raw_bytes.replace(b'\r\n', b'')
        if b'\n' in stripped:
            return "MIXED"
        return "CRLF"
    elif b'\r' in raw_bytes:
        return "CR"
    return "LF"


# ---------------------------------------------------------------------------
# Controlli strutturali
# ---------------------------------------------------------------------------

def _check_headers(headers: list[str], issues: list[Issue]) -> None:
    """Verifica la struttura delle colonne nell'header."""

    # Colonne duplicate
    seen: dict[str, int] = {}
    for h in headers:
        h_clean = h.strip().lower()
        seen[h_clean] = seen.get(h_clean, 0) + 1
    duplicates = {k: v for k, v in seen.items() if v > 1}
    if duplicates:
        issues.append(Issue(
            Severity.ERROR, "Header",
            f"Colonne duplicate: {duplicates}"
        ))

    # Spazi trailing/leading nei nomi colonna
    messy = [h for h in headers if h != h.strip()]
    if messy:
        issues.append(Issue(
            Severity.INFO, "Header",
            f"{len(messy)} intestazione/i con spazi leading/trailing: "
            f"{[repr(h) for h in messy[:3]]}"
        ))

    # Colonne richieste mancanti
    for internal_name, patterns in REQUIRED_PATTERNS.items():
        matches = [h for h in headers if _match_column(h, patterns)]
        if not matches:
            issues.append(Issue(
                Severity.ERROR, "Colonne",
                f"Colonna richiesta non trovata: '{internal_name}' "
                f"(pattern cercati: {patterns})"
            ))
        elif len(matches) > 1:
            issues.append(Issue(
                Severity.WARNING, "Colonne",
                f"Più colonne corrispondono a '{internal_name}': {matches}"
            ))

    # Colonne opzionali (solo informativo)
    for internal_name, patterns in OPTIONAL_PATTERNS.items():
        matches = [h for h in headers if _match_column(h, patterns)]
        if matches:
            issues.append(Issue(
                Severity.INFO, "Colonne",
                f"Colonna opzionale presente: '{internal_name}' → {matches[0]}"
            ))

    # Colonne non riconosciute (potenziale errore di formato)
    all_patterns = {**REQUIRED_PATTERNS, **OPTIONAL_PATTERNS}
    known_meta = ["odpověď", "odesláno", "instituce", "oddělení",
                   "kurz", "skupina", "celý", "uživatelské"]
    unrecognized = []
    for h in headers:
        h_lower = h.strip().lower()
        is_known = any(
            _match_column(h, pats) for pats in all_patterns.values()
        )
        is_meta = any(m in h_lower for m in known_meta)
        if not is_known and not is_meta:
            unrecognized.append(h)
    if unrecognized:
        issues.append(Issue(
            Severity.WARNING, "Colonne",
            f"{len(unrecognized)} colonna/e non riconosciuta/e: "
            f"{[h.strip() for h in unrecognized[:5]]}"
        ))


def _check_rows(text: str, delimiter: str, quotechar: str,
                 num_header_cols: int, issues: list[Issue]) -> int:
    """Controlli riga per riga. Restituisce il numero di righe dati."""
    reader = csv.reader(StringIO(text), delimiter=delimiter, quotechar=quotechar)
    rows = list(reader)

    if len(rows) < 2:
        issues.append(Issue(
            Severity.ERROR, "Dati",
            "Il file non contiene righe dati (solo header o vuoto)."
        ))
        return 0

    data_rows = rows[1:]
    num_data = len(data_rows)

    # Righe vuote
    empty_indices = [i + 2 for i, row in enumerate(data_rows)
                     if all(cell.strip() == "" for cell in row)]
    if empty_indices:
        issues.append(Issue(
            Severity.WARNING, "Dati",
            f"{len(empty_indices)} riga/righe completamente vuota/e: "
            f"righe {empty_indices[:5]}"
        ))

    # Righe con numero di colonne diverso dall'header
    short_rows = []
    long_rows = []
    for i, row in enumerate(data_rows, start=2):
        if len(row) < num_header_cols:
            short_rows.append(i)
        elif len(row) > num_header_cols:
            # Tolleranza: se l'unica colonna in più è vuota → trailing delimiter
            extra = row[num_header_cols:]
            if all(c.strip() == "" for c in extra):
                pass  # trailing delimiter, harmless
            else:
                long_rows.append(i)

    if short_rows:
        issues.append(Issue(
            Severity.ERROR, "Dati",
            f"{len(short_rows)} riga/righe con meno colonne del previsto "
            f"({num_header_cols}): righe {short_rows[:10]}"
        ))
    if long_rows:
        issues.append(Issue(
            Severity.WARNING, "Dati",
            f"{len(long_rows)} riga/righe con colonne extra "
            f"non vuote: righe {long_rows[:10]}"
        ))

    # Virgolette non bilanciate (a livello di testo grezzo)
    lines = text.splitlines()
    unbalanced = [i + 1 for i, line in enumerate(lines)
                  if line.count('"') % 2 != 0]
    if unbalanced:
        # Potrebbe essere legittimo in CSV multilinea, segnalo solo come info
        issues.append(Issue(
            Severity.INFO, "Quote",
            f"Righe con numero dispari di virgolette: {unbalanced[:5]} "
            f"(potrebbe essere CSV multilinea)"
        ))

    return num_data


def _check_data_types(text: str, headers: list[str],
                      delimiter: str, quotechar: str,
                      issues: list[Issue]) -> None:
    """Verifica che le colonne numeriche contengano valori validi."""
    reader = csv.DictReader(
        StringIO(text), delimiter=delimiter, quotechar=quotechar
    )

    # Identifica le colonne numeriche (Preparation, Introduction, Inclusion)
    numeric_patterns = ["Preparation", "Introduction", "Inclusion"]
    numeric_cols = []
    for h in headers:
        for pat in numeric_patterns:
            if pat.lower() in h.lower():
                numeric_cols.append(h)
                break

    if not numeric_cols:
        return

    bad_values: dict[str, list[tuple[int, str]]] = {c: [] for c in numeric_cols}

    for row_idx, row in enumerate(reader, start=2):
        for col in numeric_cols:
            val = row.get(col) or ""
            val = val.strip()
            if val == "" or val.lower() == "nan":
                continue
            try:
                num = float(val)
                if num < 1 or num > 5:
                    bad_values[col].append((row_idx, f"{val} (fuori scala 1-5)"))
            except ValueError:
                bad_values[col].append((row_idx, f"{repr(val)} (non numerico)"))

    for col, bads in bad_values.items():
        if bads:
            col_short = col.split("_")[0] if "_" in col else col[:30]
            non_numeric = [b for b in bads if "non numerico" in b[1]]
            out_of_range = [b for b in bads if "fuori scala" in b[1]]

            if non_numeric:
                issues.append(Issue(
                    Severity.ERROR, "Tipi",
                    f"Colonna '{col_short}': {len(non_numeric)} valore/i "
                    f"non numerico/i — riga {non_numeric[0][0]}: "
                    f"{non_numeric[0][1]}"
                ))
            if out_of_range:
                issues.append(Issue(
                    Severity.WARNING, "Tipi",
                    f"Colonna '{col_short}': {len(out_of_range)} valore/i "
                    f"fuori dalla scala 1-5 — riga {out_of_range[0][0]}: "
                    f"{out_of_range[0][1]}"
                ))


# ---------------------------------------------------------------------------
# Funzione principale
# ---------------------------------------------------------------------------

def analyze_file(file_path: str) -> AnalysisReport:
    """
    Esegue l'analisi strutturale completa di un file CSV.

    Restituisce un AnalysisReport con le caratteristiche rilevate,
    la lista dei problemi trovati e i parametri auto-rilevati
    (encoding, delimiter) da usare per l'importazione.
    """
    report = AnalysisReport(file_path=file_path)

    # --- Esistenza e dimensione ---
    if not os.path.isfile(file_path):
        report.issues.append(Issue(
            Severity.ERROR, "File",
            f"Il file '{file_path}' non esiste."
        ))
        return report

    file_size = os.path.getsize(file_path)
    if file_size == 0:
        report.issues.append(Issue(
            Severity.ERROR, "File",
            "Il file è vuoto (0 byte)."
        ))
        return report

    # --- Lettura raw ---
    raw_bytes = open(file_path, "rb").read()

    # Controlla se è un file binario (non testuale)
    # Euristica: se più del 10% dei byte non sono printable ASCII/UTF-8
    non_text = sum(1 for b in raw_bytes[:1024]
                   if b < 9 or (b > 13 and b < 32))
    if non_text / min(len(raw_bytes), 1024) > 0.10:
        report.issues.append(Issue(
            Severity.ERROR, "File",
            "Il file sembra essere binario, non un CSV testuale."
        ))
        return report

    # --- Encoding ---
    encoding, has_bom = _detect_encoding(raw_bytes)
    report.encoding = encoding
    report.has_bom = has_bom

    try:
        text = raw_bytes.decode(encoding)
    except (UnicodeDecodeError, LookupError) as e:
        report.issues.append(Issue(
            Severity.ERROR, "Encoding",
            f"Impossibile decodificare il file con encoding '{encoding}': {e}"
        ))
        return report

    # Rimuovi BOM dal testo se presente
    if text and text[0] == '\ufeff':
        text = text[1:]

    # --- Fine riga ---
    report.line_ending = _detect_line_ending(raw_bytes)
    if report.line_ending == "MIXED":
        report.issues.append(Issue(
            Severity.WARNING, "File",
            "Terminazioni di riga miste (CRLF e LF). "
            "Il file potrebbe essere stato modificato su sistemi diversi."
        ))
    elif report.line_ending == "CR":
        report.issues.append(Issue(
            Severity.WARNING, "File",
            "Terminazioni di riga CR (vecchio Mac). Potrebbe causare "
            "problemi con alcuni parser."
        ))

    # --- Delimitatore ---
    delimiter = _detect_delimiter(text)
    report.delimiter = delimiter

    if delimiter == ";":
        report.issues.append(Issue(
            Severity.INFO, "Formato",
            "Delimitatore rilevato: punto e virgola (locale europeo)."
        ))
    elif delimiter == "\t":
        report.issues.append(Issue(
            Severity.INFO, "Formato",
            "Delimitatore rilevato: tabulazione (TSV)."
        ))

    # --- Parsing header ---
    try:
        reader = csv.reader(StringIO(text), delimiter=delimiter, quotechar='"')
        headers = next(reader)
    except StopIteration:
        report.issues.append(Issue(
            Severity.ERROR, "Dati",
            "Il file non contiene nessuna riga (nemmeno l'header)."
        ))
        return report

    report.headers = headers
    report.num_columns = len(headers)

    if report.num_columns < 10:
        report.issues.append(Issue(
            Severity.WARNING, "Formato",
            f"Solo {report.num_columns} colonne rilevate. "
            f"Se il file usa un delimitatore diverso da '{repr(delimiter)}', "
            f"il parsing potrebbe essere errato."
        ))

    # --- Controlli header ---
    _check_headers(headers, report.issues)

    # --- Controlli righe ---
    report.num_rows = _check_rows(text, delimiter, '"',
                                   report.num_columns, report.issues)

    if report.num_rows < 3:
        report.issues.append(Issue(
            Severity.WARNING, "Dati",
            f"Solo {report.num_rows} righe dati. Medie e statistiche "
            f"potrebbero non essere significative."
        ))

    # --- Controlli tipi nelle colonne numeriche ---
    _check_data_types(text, headers, delimiter, '"', report.issues)

    return report
