#!/bin/bash
# JARVIS — ChatGPT Browser Automation (v2 — pure JS, no keystroke)
# Użycie: ./jarvis_chatgpt.sh "Twój prompt tutaj"
# Wynik: kopiuje odpowiedź ChatGPT do schowka + zapisuje do pliku

PROMPT="$1"
OUTPUT_FILE="/tmp/jarvis_chatgpt_response.txt"
WAIT=30  # sekundy oczekiwania na odpowiedź ChatGPT

if [ -z "$PROMPT" ]; then
    echo "BLAD: Podaj prompt jako argument"
    echo "Uzycie: $0 \"Twoj prompt\""
    exit 1
fi

echo "[JARVIS] Wysylam do ChatGPT: $PROMPT"

# Krok 1: Otwórz zakładkę ChatGPT
osascript << APPLESCRIPT
tell application "Google Chrome"
    activate
    set chatgptTab to null
    set chatgptWindow to null

    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "chatgpt.com" or URL of t contains "chat.openai.com" then
                set chatgptTab to t
                set chatgptWindow to w
                exit repeat
            end if
        end repeat
        if chatgptTab is not null then exit repeat
    end repeat

    if chatgptTab is null then
        make new tab at end of tabs of window 1 with properties {URL:"https://chatgpt.com/"}
        delay 4
    else
        set active tab index of chatgptWindow to tab index of chatgptTab
        set index of chatgptWindow to 1
        delay 1
    end if

    delay 2
end tell
APPLESCRIPT

# Krok 2: Wklej prompt i kliknij Send przez JavaScript
ESCAPED_PROMPT=$(echo "$PROMPT" | sed "s/'/\\\\'/g" | sed 's/"/\\"/g')

osascript << APPLESCRIPT2
tell application "Google Chrome"
    activate
    tell active tab of window 1
        execute javascript "
            (function() {
                var ta = document.querySelector('#prompt-textarea');
                if (!ta) ta = document.querySelector('div[contenteditable]');
                if (!ta) return 'BRAK_TEXTAREA';
                ta.focus();
                document.execCommand('insertText', false, '$ESCAPED_PROMPT');
                return 'WKLEJONO';
            })();
        "
    end tell
end tell
APPLESCRIPT2

sleep 1

# Krok 3: Kliknij przycisk Send
osascript << APPLESCRIPT3
tell application "Google Chrome"
    tell active tab of window 1
        execute javascript "
            var btn = document.querySelector('[data-testid=\"send-button\"]');
            if (btn) { btn.click(); 'OK'; } else { 'BRAK_PRZYCISKU'; }
        "
    end tell
end tell
APPLESCRIPT3

echo "[JARVIS] Prompt wyslany. Czekam ${WAIT}s na odpowiedz..."
sleep "$WAIT"

# Krok 4: Odczytaj odpowiedź
RESPONSE=$(osascript << APPLESCRIPT4
tell application "Google Chrome"
    tell active tab of window 1
        set resp to execute javascript "
            var dataRole = document.querySelectorAll('[data-message-author-role=\"assistant\"]');
            var prose = document.querySelectorAll('[class*=\"prose\"]');
            var text = '';
            if (dataRole.length > 0) {
                text = dataRole[dataRole.length-1].innerText;
            } else if (prose.length > 0) {
                text = prose[prose.length-1].innerText;
            }
            text || 'BRAK_ODPOWIEDZI';
        "
        return resp
    end tell
end tell
APPLESCRIPT4
)

if [ -n "$RESPONSE" ] && [ "$RESPONSE" != "BRAK_ODPOWIEDZI" ]; then
    echo "$RESPONSE" > "$OUTPUT_FILE"
    echo "$RESPONSE" | pbcopy
    echo ""
    echo "========================================="
    echo "[JARVIS] ODPOWIEDZ ChatGPT:"
    echo "========================================="
    echo "$RESPONSE"
    echo "========================================="
    echo "[JARVIS] Zapisano: $OUTPUT_FILE | Skopiowano do schowka"
else
    echo "[JARVIS] BLAD: Brak odpowiedzi. Zwieksz WAIT (obecny: ${WAIT}s) lub sprawdz Chrome."
    exit 1
fi
