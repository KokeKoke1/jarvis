#!/bin/bash
# JARVIS ZIP Builder — tworzy archiwum ZIP z plików/folderów
# Użycie:
#   ./jarvis_zip.sh output.zip plik1 plik2 folder1 ...
#   ./jarvis_zip.sh --find-photos output.zip    # automatycznie znajdź 5 zdjęć
#   ./jarvis_zip.sh --find-ext jpg,png output.zip  # znajdź po rozszerzeniu

MODE="normal"
OUTPUT=""
FILES=()

# Parsuj argumenty
while [[ $# -gt 0 ]]; do
    case "$1" in
        --find-photos)
            MODE="photos"
            shift
            OUTPUT="$1"
            shift
            ;;
        --find-ext)
            MODE="ext"
            shift
            EXTENSIONS="$1"
            shift
            OUTPUT="$1"
            shift
            ;;
        *)
            if [ -z "$OUTPUT" ]; then
                OUTPUT="$1"
            else
                FILES+=("$1")
            fi
            shift
            ;;
    esac
done

if [ -z "$OUTPUT" ]; then
    echo "BLAD: Podaj nazwę pliku wyjściowego ZIP"
    echo "Użycie:"
    echo "  $0 output.zip plik1 plik2 ..."
    echo "  $0 --find-photos output.zip"
    echo "  $0 --find-ext jpg,png output.zip"
    exit 1
fi

# Dodaj .zip jeśli brak rozszerzenia
[[ "$OUTPUT" != *.zip ]] && OUTPUT="${OUTPUT}.zip"
OUTPUT_PATH="$OUTPUT"

echo "[*] JARVIS ZIP Builder — cel: $OUTPUT_PATH"

if [ "$MODE" = "photos" ]; then
    echo "[*] Szukam zdjęć na laptopie..."
    while IFS= read -r line; do FILES+=("$line"); done < <(
        find ~/Downloads ~/Pictures ~/Desktop ~/Documents -maxdepth 3 \
            \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.heic" \) \
            2>/dev/null | head -10
    )
    if [ ${#FILES[@]} -eq 0 ]; then
        echo "BLAD: Nie znaleziono żadnych zdjęć"
        exit 1
    fi
    echo "[*] Znaleziono ${#FILES[@]} zdjęć, wybieram pierwsze 6..."
    FILES=("${FILES[@]:0:6}")

elif [ "$MODE" = "ext" ]; then
    echo "[*] Szukam plików: $EXTENSIONS ..."
    IFS=',' read -ra EXTS <<< "$EXTENSIONS"
    FIND_ARGS=()
    for ext in "${EXTS[@]}"; do
        FIND_ARGS+=(-o -name "*.${ext}")
    done
    # usuń pierwsze -o
    FIND_ARGS=("${FIND_ARGS[@]:1}")
    while IFS= read -r line; do FILES+=("$line"); done < <(
        find ~/Downloads ~/Desktop ~/Documents -maxdepth 3 \
            \( "${FIND_ARGS[@]}" \) 2>/dev/null | head -10
    )
    if [ ${#FILES[@]} -eq 0 ]; then
        echo "BLAD: Nie znaleziono plików ($EXTENSIONS)"
        exit 1
    fi
fi

if [ ${#FILES[@]} -eq 0 ]; then
    echo "BLAD: Brak plików do spakowania"
    exit 1
fi

echo "[*] Pakuję ${#FILES[@]} pliki/ów:"
for f in "${FILES[@]}"; do
    echo "    - $(basename "$f")"
done

# Utwórz ZIP
rm -f "$OUTPUT_PATH"
zip -j "$OUTPUT_PATH" "${FILES[@]}" 2>&1

if [ $? -ne 0 ]; then
    echo "BLAD: Nie udało się stworzyć ZIP"
    exit 1
fi

SIZE=$(du -sh "$OUTPUT_PATH" | cut -f1)
echo "OK: $OUTPUT_PATH ($SIZE) gotowy!"
echo "$OUTPUT_PATH"
