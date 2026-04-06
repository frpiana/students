"""
Modulo di pulizia e normalizzazione dei nomi dei leader (Q02_Leader_name).

Applica tre strati di correzione in ordine crescente di aggressività:
  1. Strip e normalizzazione spazi
  2. Unificazione cognome↔nome completo e ordine invertito dei token
  3. Fuzzy matching per typo e varianti ortografiche (con warning)
"""

from __future__ import annotations
from pandas import DataFrame, Series
from unicodedata import normalize, combining, category


# ---------------------------------------------------------------------------
# Utilità
# ---------------------------------------------------------------------------

def _normalize_unicode(s: str) -> str:
    """Normalizzazione NFC per confronti coerenti di caratteri accentati."""
    return normalize("NFC", s)


def _strip_accents(s: str) -> str:
    """Rimuove gli accenti per il confronto fuzzy (NFD → rimuovi combining)."""
    return "".join(c for c in normalize("NFD", s) if not combining(c))


def _tokenize(name: str) -> set[str]:
    """Restituisce il set di token in minuscolo di un nome."""
    return set(name.lower().split())


def _surname(name: str) -> str:
    """Restituisce l'ultimo token (cognome convenzionale) in minuscolo."""
    tokens = name.split()
    return tokens[-1].lower() if tokens else ""


def _levenshtein(a: str, b: str) -> int:
    """Distanza di Levenshtein tra due stringhe."""
    if len(a) < len(b):
        return _levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]


# ---------------------------------------------------------------------------
# Strato 1 — Strip e normalizzazione spazi
# ---------------------------------------------------------------------------

def _layer_strip(names: Series) -> Series:
    """Rimuove spazi leading/trailing e normalizza Unicode NFC."""
    return names.map(lambda x: _normalize_unicode(x.strip()) if isinstance(x, str) else x)


# ---------------------------------------------------------------------------
# Strato 2 — Cognome ↔ nome completo + ordine invertito
# ---------------------------------------------------------------------------

def _build_merge_map_structural(unique_names: list[str]) -> dict[str, str]:
    """
    Costruisce una mappa {nome_originale: nome_canonico} per:
      - Cognome solo → nome completo (es. "Radová" → "Hana Radová")
      - Ordine invertito (es. "Anderle Vojtěch" → "Vojtěch Anderle")
    Il nome canonico scelto è quello con più token; a parità, il primo
    in ordine alfabetico (per determinismo).
    """
    merge: dict[str, str] = {}

    # Separa nomi a singolo token (solo cognome) da quelli multi-token
    singles: list[str] = []
    multis: list[str] = []
    for n in unique_names:
        (singles if len(n.split()) == 1 else multis).append(n)

    # 2a — Cognome solo → nome completo
    for single in singles:
        candidates = [m for m in multis if _surname(m) == single.lower()]
        if len(candidates) == 1:
            merge[single] = candidates[0]
        elif len(candidates) > 1:
            # Più candidati: prendi il più frequente (gestito dopo) o il primo
            merge[single] = sorted(candidates)[0]

    # 2b — Ordine invertito tra nomi multi-token
    processed: set[str] = set()
    for i, a in enumerate(multis):
        if a in processed:
            continue
        ta = _tokenize(a)
        for b in multis[i + 1:]:
            if b in processed:
                continue
            tb = _tokenize(b)
            if len(ta) > 1 and ta == tb and a != b:
                # Stesso set di token, ordine diverso → unifica
                # Preferisci l'ordine Nome Cognome (prima lettera maiuscola
                # del primo token più corto = probabilmente il nome)
                canonical = sorted([a, b])[0]
                other = b if canonical == a else a
                merge[other] = canonical
                processed.add(other)

    return merge


# ---------------------------------------------------------------------------
# Strato 3 — Fuzzy matching
# ---------------------------------------------------------------------------

def _build_merge_map_fuzzy(unique_names: list[str],
                           threshold: int = 2) -> tuple[dict[str, str], list[str]]:
    """
    Trova coppie di nomi con distanza di Levenshtein ≤ threshold
    (calcolata senza accenti per catturare varianti come á↔a).

    Restituisce:
      - merge_map: {nome_da_sostituire: nome_canonico}
      - warnings: lista di messaggi da stampare a schermo
    """
    merge: dict[str, str] = {}
    warnings: list[str] = []
    processed: set[str] = set()

    for i, a in enumerate(unique_names):
        if a in processed:
            continue
        for b in unique_names[i + 1:]:
            if b in processed:
                continue
            # Confronto senza accenti
            a_norm = _strip_accents(a.lower())
            b_norm = _strip_accents(b.lower())

            if a_norm == b_norm:
                # Identici senza accenti (es. Vedralova ↔ Vedralová)
                dist = 0
            else:
                dist = _levenshtein(a_norm, b_norm)

            # Soglia proporzionale alla lunghezza del nome più corto
            min_len = min(len(a_norm), len(b_norm))
            effective_threshold = threshold if min_len > 6 else 1

            if 0 < dist <= effective_threshold:
                # Scegli il canonico: preferisci quello con più accenti (più corretto)
                accent_a = sum(1 for c in normalize("NFD", a) if combining(c))
                accent_b = sum(1 for c in normalize("NFD", b) if combining(c))
                if accent_a >= accent_b:
                    canonical, other = a, b
                else:
                    canonical, other = b, a

                merge[other] = canonical
                processed.add(other)
                warnings.append(
                    f"  FUZZY: \"{other}\" → \"{canonical}\" "
                    f"(distanza Levenshtein: {dist})"
                )
            elif dist == 0 and a != b:
                # Identici senza accenti
                # Preferisci quello con gli accenti originali cechi
                canonical = max(a, b, key=lambda x: sum(
                    1 for c in normalize("NFD", x) if combining(c)
                ))
                other = b if canonical == a else a
                merge[other] = canonical
                processed.add(other)
                warnings.append(
                    f"  FUZZY (accento): \"{other}\" → \"{canonical}\""
                )

    return merge, warnings


# ---------------------------------------------------------------------------
# Funzione principale
# ---------------------------------------------------------------------------

def clean_leader_names(data_frame: DataFrame) -> DataFrame:
    """
    Pulisce e normalizza la colonna Q02_Leader_name applicando i tre strati.
    Stampa a schermo le correzioni effettuate.
    Ritorna il DataFrame con i nomi corretti.
    """
    col = "Q02_Leader_name"
    corrections_log: list[str] = []

    # Strato 1 — Strip e normalizzazione
    data_frame[col] = _layer_strip(data_frame[col])

    unique_before = data_frame[col].dropna().unique()
    stripped_count = len(set(unique_before))

    # Strato 2 — Unificazione strutturale
    unique_names = sorted(data_frame[col].dropna().unique())
    structural_map = _build_merge_map_structural(unique_names)

    if structural_map:
        corrections_log.append("Correzioni strutturali (cognome/ordine):")
        for old, new in sorted(structural_map.items()):
            corrections_log.append(f"  \"{old}\" → \"{new}\"")
        data_frame[col] = data_frame[col].map(
            lambda x: structural_map.get(x, x) if isinstance(x, str) else x
        )

    # Strato 3 — Fuzzy matching (sui nomi già normalizzati)
    unique_names = sorted(data_frame[col].dropna().unique())
    fuzzy_map, fuzzy_warnings = _build_merge_map_fuzzy(unique_names)

    if fuzzy_map:
        corrections_log.append("Correzioni fuzzy (varianti ortografiche):")
        corrections_log.extend(fuzzy_warnings)
        data_frame[col] = data_frame[col].map(
            lambda x: fuzzy_map.get(x, x) if isinstance(x, str) else x
        )

    # Report finale
    unique_after = data_frame[col].dropna().nunique()
    total_merged = stripped_count - unique_after

    if corrections_log:
        print("\n--- Data cleaning: Q02_Leader_name ---")
        for line in corrections_log:
            print(line)
        print(f"Nomi unici: {stripped_count} → {unique_after} "
              f"({total_merged} unificati)")
        print("--------------------------------------\n")

    return data_frame
