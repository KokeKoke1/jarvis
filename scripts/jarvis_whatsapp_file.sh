#!/bin/bash
# JARVIS WhatsApp File Sender — metoda CV (clipboard + Cmd+V)
# Użycie: ./jarvis_whatsapp_file.sh "Kontakt" "/ścieżka/do/pliku"

CONTACT="$1"
FILEPATH="$2"

if [ -z "$CONTACT" ] || [ -z "$FILEPATH" ]; then
    echo "BLAD: Użycie: $0 \"Kontakt\" \"/ścieżka/do/pliku\""
    exit 1
fi

if [ ! -f "$FILEPATH" ]; then
    echo "BLAD: Plik nie istnieje: $FILEPATH"
    exit 1
fi

SAFE_CONTACT=$(echo "$CONTACT" | sed 's/"/\\"/g')
SAFE_FILEPATH=$(echo "$FILEPATH" | sed 's/"/\\"/g')
FILENAME=$(basename "$FILEPATH")

echo "[*] JARVIS WhatsApp File — wysyłam '$FILENAME' do '$CONTACT'"

# Krok 1: Skopiuj plik do schowka (poza Terminal)
osascript -e "set the clipboard to (POSIX file \"$SAFE_FILEPATH\")" 2>/dev/null
sleep 1
echo "[*] Plik skopiowany do schowka."

TMPSCRIPT=$(mktemp /tmp/jarvis_wf_XXXX.scpt)
RESULT_FILE="/tmp/jarvis_wf_result_$$.txt"
rm -f "$RESULT_FILE"

cat > "$TMPSCRIPT" <<APSCRIPT
-- ===== JARVIS WhatsApp File Sender — metoda clipboard =====

tell application "WhatsApp"
    activate
end tell
delay 3

tell application "System Events"
    tell process "WhatsApp"
        -- Czekaj na okno
        set maxWait to 20
        set waited to 0
        repeat
            if (count of windows) > 0 then exit repeat
            delay 1
            set waited to waited + 1
            if waited >= maxWait then
                do shell script "echo 'BLAD: WhatsApp nie otworzyl okna' > $RESULT_FILE"
                return
            end if
        end repeat

        set frontmost to true
        delay 1

        -- === KROK 1: Szukaj kontaktu ===
        keystroke "f" using {command down}
        delay 2.5

        keystroke "a" using {command down}
        delay 0.3
        keystroke "$SAFE_CONTACT"
        delay 3

        -- === KROK: Wybierz pierwszy wynik (Down x1 + Enter) ===
        -- Down raz = pierwszy wynik listy (wpisaliśmy dokładną nazwę więc to nasz kontakt)
        key code 125
        delay 0.8
        key code 36
        delay 1

        delay 2.5

        -- === WERYFIKACJA: Czy jesteśmy w czacie z właściwym kontaktem? ===
        -- Szukamy imienia kontaktu w elementach UI (WhatsApp nie zmienia tytułu okna)
        set chatVerified to false
        set contactLower to do shell script "echo " & quoted form of "$SAFE_CONTACT" & " | tr '[:upper:]' '[:lower:]'"

        try
            -- Szukaj w przyciskach i nagłówku czatu (header WhatsApp ma button z imieniem)
            set allButtons to every button of front window
            repeat with btn in allButtons
                try
                    set btnName to do shell script "echo " & quoted form of (name of btn as string) & " | tr '[:upper:]' '[:lower:]'"
                    if btnName contains contactLower then
                        set chatVerified to true
                        exit repeat
                    end if
                end try
            end repeat
        end try

        -- Fallback: szukaj w static text na górze okna
        if not chatVerified then
            try
                set allTexts to every static text of front window
                repeat with txt in allTexts
                    try
                        set txtVal to do shell script "echo " & quoted form of (value of txt as string) & " | tr '[:upper:]' '[:lower:]'"
                        if txtVal contains contactLower then
                            set chatVerified to true
                            exit repeat
                        end if
                    end try
                end repeat
            end try
        end if

        if not chatVerified then
            -- Dump pierwszych buttonów dla diagnostyki
            set diagInfo to ""
            try
                set btnList to every button of front window
                set btnCount to count of btnList
                set diagInfo to "buttons:" & btnCount
                if btnCount > 0 then
                    set firstBtn to name of item 1 of btnList
                    set diagInfo to diagInfo & " first:" & firstBtn
                end if
            end try
            do shell script "echo 'BLAD: Zly czat! Nie znaleziono kontaktu: $SAFE_CONTACT [" & diagInfo & "]' > $RESULT_FILE"
            return
        end if

        -- === KROK 2: Pobierz rozmiar okna ===
        set winPos to position of front window
        set winSize to size of front window
        set winLeft to item 1 of winPos
        set winTop to item 2 of winPos
        set winW to item 1 of winSize
        set winH to item 2 of winSize

        -- Pole wiadomości = środek X, 50px od dołu
        set msgX to winLeft + (winW / 2)
        set msgY to winTop + winH - 50

        -- === KROK 3: 3x klik w pole wiadomości — upewnij się że jesteś tam ===
        click at {msgX, msgY}
        delay 0.4
        click at {msgX, msgY}
        delay 0.4
        click at {msgX, msgY}
        delay 0.8

        -- === KROK 4: Cmd+V — wklej plik ze schowka ===
        keystroke "v" using {command down}
        delay 3.5

        -- === KROK 5: Enter — wyślij ===
        keystroke return
        delay 2.5

    end tell
end tell

do shell script "echo 'OK' > $RESULT_FILE"
APSCRIPT

# Uruchom przez Terminal.app (ma Accessibility permissions)
osascript 2>/dev/null <<LAUNCHER
tell application "Terminal"
    activate
    do script "osascript $(printf '%q' "$TMPSCRIPT"); sleep 2; exit"
end tell
LAUNCHER

echo "[*] Czekam na wykonanie (max 60s)..."
for i in $(seq 1 60); do
    sleep 1
    if [ -f "$RESULT_FILE" ]; then
        RESULT=$(cat "$RESULT_FILE")
        rm -f "$RESULT_FILE" "$TMPSCRIPT"
        if [ "$RESULT" = "OK" ]; then
            echo "OK: '$FILENAME' wyslany do '$CONTACT' przez WhatsApp!"
            exit 0
        else
            echo "BLAD: $RESULT"
            exit 1
        fi
    fi
    [ $((i % 10)) -eq 0 ] && echo "    ... czekam ($i/60s)"
done

rm -f "$RESULT_FILE" "$TMPSCRIPT"
echo "TIMEOUT: Sprawdz WhatsApp recznie."
exit 1
