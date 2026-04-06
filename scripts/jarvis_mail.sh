#!/bin/bash
# JARVIS Mail Sender — wysyła maile z załącznikami przez Mail.app
# Użycie: ./jarvis_mail.sh "odbiorca@email.com" "Temat" "Treść" ["/sciezka/do/pliku.pdf"]
#
# Argumenty:
#   $1 — adres email odbiorcy
#   $2 — temat
#   $3 — treść wiadomości
#   $4 — (opcjonalny) pełna ścieżka do załącznika

RECIPIENT="$1"
SUBJECT="$2"
BODY="$3"
ATTACHMENT="$4"

if [ -z "$RECIPIENT" ] || [ -z "$SUBJECT" ] || [ -z "$BODY" ]; then
    echo "BLAD: Podaj odbiorcę, temat i treść."
    echo "Użycie: $0 \"email\" \"Temat\" \"Treść\" [\"/sciezka/pliku\"]"
    exit 1
fi

# Oblicz delay na podstawie rozmiaru pliku (minimum 5s, max 15s)
DELAY=5
if [ -n "$ATTACHMENT" ] && [ -f "$ATTACHMENT" ]; then
    FILE_SIZE=$(stat -f%z "$ATTACHMENT" 2>/dev/null || echo 0)
    if [ "$FILE_SIZE" -gt 5000000 ]; then
        DELAY=15
    elif [ "$FILE_SIZE" -gt 1000000 ]; then
        DELAY=10
    else
        DELAY=5
    fi
fi

if [ -n "$ATTACHMENT" ] && [ ! -f "$ATTACHMENT" ]; then
    echo "BLAD: Plik nie istnieje: $ATTACHMENT"
    exit 1
fi

if [ -n "$ATTACHMENT" ]; then
    # Mail z załącznikiem
    osascript <<APPLESCRIPT
set theFile to POSIX file "$ATTACHMENT"
tell application "Mail"
    set newMsg to make new outgoing message with properties {subject:"$SUBJECT", content:"$BODY", visible:false}
    tell newMsg
        make new to recipient at end of to recipients with properties {address:"$RECIPIENT"}
        make new attachment with properties {file name:theFile} at after last paragraph of content
    end tell
    delay $DELAY
    send newMsg
end tell
APPLESCRIPT
else
    # Mail bez załącznika
    osascript <<APPLESCRIPT
tell application "Mail"
    set newMsg to make new outgoing message with properties {subject:"$SUBJECT", content:"$BODY", visible:false}
    tell newMsg
        make new to recipient at end of to recipients with properties {address:"$RECIPIENT"}
    end tell
    send newMsg
end tell
APPLESCRIPT
fi

if [ $? -eq 0 ]; then
    echo "OK: Mail wysłany do $RECIPIENT | Temat: $SUBJECT | Załącznik: ${ATTACHMENT:-brak} | Delay: ${DELAY}s"
else
    echo "BLAD: Wysyłanie nieudane."
    exit 1
fi
