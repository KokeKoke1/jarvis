#!/bin/bash
# JARVIS — Ask GPT for code/solution and optionally apply it
# Użycie: ./jarvis_ask_gpt.sh "zapytanie" [--apply skrypt_do_podmiany]
# Przykład: ./jarvis_ask_gpt.sh "napisz AppleScript który wysyła plik przez WhatsApp" --apply jarvis_whatsapp_file.sh

QUERY="$1"
APPLY_TARGET="$2"
APPLY_FILE="$3"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CHATGPT_SCRIPT="$SCRIPT_DIR/jarvis_chatgpt.sh"
OUTPUT_FILE="/tmp/jarvis_gpt_code.txt"
WAIT=45  # więcej czasu dla długich odpowiedzi z kodem

if [ -z "$QUERY" ]; then
    echo "BLAD: Podaj pytanie"
    echo "Uzycie: $0 \"pytanie\" [--apply nazwa_skryptu]"
    exit 1
fi

echo "[JARVIS] Pytam ChatGPT o: $QUERY"
echo ""

# Zbuduj prompt techniczny — prosi o kod bash/applescript
FULL_PROMPT="Napisz kod bash/AppleScript rozwiązujący ten problem na macOS: $QUERY. Zwróć TYLKO gotowy kod, bez wyjaśnień. Kod ma być w bloku \`\`\`bash lub \`\`\`applescript."

# Wywołaj ChatGPT
"$CHATGPT_SCRIPT" "$FULL_PROMPT"
GPT_STATUS=$?

if [ $GPT_STATUS -ne 0 ]; then
    echo "[JARVIS] ChatGPT nie odpowiedział. Sprawdź Chrome."
    exit 1
fi

# Pobierz odpowiedź z pliku
GPT_RESPONSE=$(cat /tmp/jarvis_chatgpt_response.txt 2>/dev/null)

if [ -z "$GPT_RESPONSE" ]; then
    echo "[JARVIS] Brak odpowiedzi od ChatGPT."
    exit 1
fi

# Wyodrębnij sam kod z bloków ``` ```
EXTRACTED_CODE=$(echo "$GPT_RESPONSE" | awk '/^```/{flag=!flag; next} flag{print}')

if [ -z "$EXTRACTED_CODE" ]; then
    # Fallback — użyj całej odpowiedzi jeśli nie ma bloków kodu
    EXTRACTED_CODE="$GPT_RESPONSE"
fi

echo "$EXTRACTED_CODE" > "$OUTPUT_FILE"
echo ""
echo "[JARVIS] Kod od ChatGPT zapisany do: $OUTPUT_FILE"

# Jeśli --apply podano — podmień skrypt docelowy
if [ "$APPLY_TARGET" = "--apply" ] && [ -n "$APPLY_FILE" ]; then
    TARGET_PATH="$SCRIPT_DIR/$APPLY_FILE"

    echo ""
    echo "[JARVIS] Chcesz zastąpić $APPLY_FILE kodem od GPT? [t/n]"
    read -r CONFIRM

    if [ "$CONFIRM" = "t" ] || [ "$CONFIRM" = "T" ]; then
        # Backup oryginału
        cp "$TARGET_PATH" "${TARGET_PATH}.backup_$(date +%Y%m%d_%H%M%S)" 2>/dev/null

        # Wklej nowy kod
        echo "#!/bin/bash" > "$TARGET_PATH"
        echo "# Wygenerowane przez ChatGPT via JARVIS — $(date)" >> "$TARGET_PATH"
        echo "" >> "$TARGET_PATH"
        echo "$EXTRACTED_CODE" >> "$TARGET_PATH"
        chmod +x "$TARGET_PATH"

        echo "[JARVIS] ✅ $APPLY_FILE zaktualizowany. Backup zapisany."
    else
        echo "[JARVIS] Anulowano. Kod dostępny w: $OUTPUT_FILE"
    fi
fi
