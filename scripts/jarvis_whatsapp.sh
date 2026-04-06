#!/bin/bash
# JARVIS WhatsApp Sender v8 — triple-click na pole wiadomości po wejściu w czat
# Użycie: ./jarvis_whatsapp.sh "Kontakt" "Wiadomość"

CONTACT="$1"
MESSAGE="$2"

if [ -z "$CONTACT" ] || [ -z "$MESSAGE" ]; then
    echo "BLAD: Podaj kontakt i wiadomość."
    echo "Użycie: $0 \"kontakt\" \"wiadomość\""
    exit 1
fi

SAFE_CONTACT=$(echo "$CONTACT" | sed "s/\"/\\\\\"/g")
SAFE_MESSAGE=$(echo "$MESSAGE" | sed "s/\"/\\\\\"/g")

echo "[*] JARVIS WhatsApp v7 — kontakt: $CONTACT"

TMPSCRIPT=$(mktemp /tmp/jarvis_wa_XXXX.scpt)
RESULT_FILE="/tmp/jarvis_wa_result_$$.txt"
rm -f "$RESULT_FILE"

cat > "$TMPSCRIPT" <<APSCRIPT
-- Krok 1: Otwórz WhatsApp i poczekaj
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
                do shell script "echo 'BLAD: WhatsApp timeout' > $RESULT_FILE"
                return
            end if
        end repeat

        set frontmost to true
        delay 1

        -- Krok 2: Cmd+F = otwórz wyszukiwarkę
        keystroke "f" using {command down}
        delay 2.5

        -- Wyczyść pole i wpisz kontakt
        keystroke "a" using {command down}
        delay 0.3
        keystroke "$SAFE_CONTACT"
        delay 3

        -- Strzałka w dół 1x (do pierwszego wyniku kontaktu — pomijamy nagłówek)
        key code 125
        delay 0.8
        key code 125
        delay 0.8

        -- Enter = otwórz czat
        keystroke return
        delay 2.5

        -- Krok 3: Triple-click w dolną część okna = focus na polu wiadomości
        -- Pobierz pozycję i rozmiar okna, kliknij 3x w dolną część (obszar input)
        set winPos to position of front window
        set winSize to size of front window
        set clickX to (item 1 of winPos) + (item 1 of winSize) / 2
        set clickY to (item 2 of winPos) + (item 2 of winSize) - 50

        click at {clickX, clickY}
        delay 0.3
        click at {clickX, clickY}
        delay 0.3
        click at {clickX, clickY}
        delay 0.5

        -- Krok 4: Wpisz wiadomość i wyślij
        keystroke "$SAFE_MESSAGE"
        delay 1
        keystroke return
        delay 0.8

    end tell
end tell

do shell script "echo 'OK' > $RESULT_FILE"
APSCRIPT

# Uruchom przez Terminal.app (ma Accessibility)
osascript 2>/dev/null <<LAUNCHER
tell application "Terminal"
    activate
    do script "osascript $(printf '%q' "$TMPSCRIPT"); sleep 2; exit"
end tell
LAUNCHER

echo "[*] Czekam na wykonanie WhatsApp (max 40s)..."
for i in $(seq 1 40); do
    sleep 1
    if [ -f "$RESULT_FILE" ]; then
        RESULT=$(cat "$RESULT_FILE")
        rm -f "$RESULT_FILE" "$TMPSCRIPT"
        if [ "$RESULT" = "OK" ]; then
            echo "OK: Wiadomosc \"$MESSAGE\" wyslana do \"$CONTACT\" przez WhatsApp!"
            exit 0
        else
            echo "BLAD: $RESULT"
            exit 1
        fi
    fi
    if [ $((i % 10)) -eq 0 ]; then
        echo "    ... czekam jeszcze ($i/40s)"
    fi
done

rm -f "$RESULT_FILE" "$TMPSCRIPT"
echo "TIMEOUT: Skrypt trwal za dlugo. Sprawdz WhatsApp."
exit 1
