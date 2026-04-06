#!/bin/bash
# ==============================================================
# Test runner per students
# Esegue il programma su ciascun CSV nella cartella data/
# e salva i PDF in cartelle separate per ispezione manuale.
#
# Uso:
#   bash test/run_tests.sh          — esegue tutti i test
#   bash test/run_tests.sh clean    — cancella le cartelle di output
# ==============================================================

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="$REPO_ROOT/src/students"
FONT_DIR="$REPO_ROOT/src/fonts"
DATA_DIR="$REPO_ROOT/data"
OUTPUT_ROOT="$REPO_ROOT/test/output"

# Colori per output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ---- Comando "clean" ----
if [ "${1}" = "clean" ]; then
    echo -e "${CYAN}Pulizia cartelle di output...${NC}"
    rm -rf "$OUTPUT_ROOT"
    echo -e "${GREEN}Done.${NC} Cartella $OUTPUT_ROOT rimossa."
    exit 0
fi

echo "========================================"
echo " students — test runner"
echo "========================================"
echo ""
echo "Repo root   : $REPO_ROOT"
echo "Source dir   : $SRC_DIR"
echo "Data dir    : $DATA_DIR"
echo "Output root : $OUTPUT_ROOT"
echo ""

# Pulisci le cartelle di output precedenti
rm -rf "$OUTPUT_ROOT"
mkdir -p "$OUTPUT_ROOT"

# Contatori
PASS=0
FAIL=0
TOTAL=0

# Itera su tutti i CSV nella cartella data/
for csv_file in "$DATA_DIR"/*.csv; do
    csv_name="$(basename "$csv_file")"
    # Nome della cartella di output (senza estensione)
    test_label="${csv_name%.csv}"
    test_dir="$OUTPUT_ROOT/$test_label"
    pdf_dir="$test_dir/pdf"

    TOTAL=$((TOTAL + 1))

    echo "----------------------------------------"
    echo -e "${YELLOW}TEST $TOTAL: $csv_name${NC}"
    echo "----------------------------------------"

    # Prepara la workdir per questo test
    mkdir -p "$test_dir"

    # Copia font nella workdir (il programma li cerca nel cwd)
    cp "$FONT_DIR"/* "$test_dir"/

    # Copia il CSV nella workdir
    cp "$csv_file" "$test_dir"/

    # Esegui il programma dalla workdir, passando:
    #   --output-dir pdf   → i PDF vanno in test_dir/pdf/
    #   il nome del CSV via stdin
    cd "$test_dir"
    OUTPUT=$(echo "$csv_name" | python3 -u "$SRC_DIR/main.py" --output-dir "$pdf_dir" 2>&1)
    EXIT_CODE=$?
    cd "$REPO_ROOT"

    echo "$OUTPUT"
    echo ""

    if [ $EXIT_CODE -eq 0 ]; then
        # Controlla che siano stati generati PDF
        PDF_COUNT=$(find "$pdf_dir" -name "*.pdf" 2>/dev/null | wc -l)
        if [ "$PDF_COUNT" -gt 0 ]; then
            echo -e "${GREEN}✓ PASS${NC} — Exit code: $EXIT_CODE, PDF generati: $PDF_COUNT"
            ls "$pdf_dir/"
            PASS=$((PASS + 1))
        else
            echo -e "${RED}✗ FAIL${NC} — Exit code: 0 ma nessun PDF generato"
            FAIL=$((FAIL + 1))
        fi
    else
        echo -e "${RED}✗ FAIL${NC} — Exit code: $EXIT_CODE"
        FAIL=$((FAIL + 1))
    fi

    # Rimuovi i font copiati (lascio solo CSV e pdf/)
    rm -f "$test_dir"/GARA*.TTF "$test_dir"/GARA*.ttf

    echo ""
done

# Riepilogo
echo "========================================"
echo " RIEPILOGO"
echo "========================================"
echo -e " Totale : $TOTAL"
echo -e " ${GREEN}Pass${NC}   : $PASS"
echo -e " ${RED}Fail${NC}   : $FAIL"
echo ""
echo -e " I PDF sono in: ${CYAN}$OUTPUT_ROOT/${NC}"
echo "========================================"

# Exit code globale
if [ $FAIL -gt 0 ]; then
    exit 1
else
    exit 0
fi
