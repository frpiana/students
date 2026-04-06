from __future__ import annotations
from pandas import read_csv, DataFrame

# Mapping: substring da cercare nell'header originale → nome colonna interno
# L'ordine non conta: il match avviene per contenuto, non per posizione.
COLUMN_PATTERNS = {
    "ID":                  ["ID uživatele", "ID"],
    "Q02_Leader_name":     ["Leader name", "Leader"],
    "Q03_Preparation":     ["Preparation"],
    "Q04_Introduction":    ["Introduction"],
    "Q05_Inclusion":       ["Inclusion"],
    "Q06_Fav_question":    ["Fav question"],
    "Q07_What_learned":    ["What learned"],
    "Q08_Negative_feedback": ["Negative feedback"],
}

# Colonne richieste dal generatore PDF (senza le quali il programma non può funzionare)
REQUIRED_COLUMNS = [
    "ID",
    "Q02_Leader_name",
    "Q03_Preparation",
    "Q04_Introduction",
    "Q05_Inclusion",
    "Q06_Fav_question",
    "Q07_What_learned",
    "Q08_Negative_feedback",
]


def _match_column(original_header: str, patterns: list[str]) -> bool:
    """Ritorna True se l'header originale contiene almeno uno dei pattern."""
    header_lower = original_header.lower()
    return any(p.lower() in header_lower for p in patterns)


def _build_column_map(original_columns: list[str]) -> dict[str, str]:
    """Costruisce la mappa {nome_interno: nome_originale} cercando i pattern."""
    col_map = {}
    for internal_name, patterns in COLUMN_PATTERNS.items():
        matches = [col for col in original_columns if _match_column(col, patterns)]
        if len(matches) == 1:
            col_map[internal_name] = matches[0]
        elif len(matches) > 1:
            # Se ci sono più match, prendi quello più specifico (più corto)
            col_map[internal_name] = min(matches, key=len)
        # Se nessun match, la colonna manca — verrà segnalato dopo
    return col_map


def data_import(file_name: str,
                encoding: str = "utf-8-sig",
                delimiter: str = ",") -> DataFrame:
    # Encoding e delimiter possono essere forniti dal modulo file_analysis
    data_frame = read_csv(file_name, encoding=encoding, sep=delimiter)

    # Costruisci la mappa tra nomi interni e header originali
    col_map = _build_column_map(list(data_frame.columns))

    # Verifica che tutte le colonne richieste siano state trovate
    missing = [name for name in REQUIRED_COLUMNS if name not in col_map]
    if missing:
        raise ValueError(
            f"Colonne mancanti nel file '{file_name}': {', '.join(missing)}.\n"
            f"Header trovati: {list(data_frame.columns)}"
        )

    # Rinomina: seleziona le colonne originali e assegna i nomi interni
    rename_map = {original: internal for internal, original in col_map.items()}
    data_frame = data_frame[[col_map[name] for name in REQUIRED_COLUMNS]]
    data_frame = data_frame.rename(columns=rename_map)

    return data_frame
