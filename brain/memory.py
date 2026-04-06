"""JARVIS persistent memory — conversation history + learned user profile."""
import json, os, time, re, datetime, threading
from .config import MEMORY_FILE, MAX_HISTORY

LOCK = threading.Lock()
HISTORY = []
USER_PROFILE = {}


def load():
    """Load memory from disk."""
    global HISTORY, USER_PROFILE
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
            with LOCK:
                HISTORY = data.get("history", [])[-MAX_HISTORY * 2:]
                USER_PROFILE = data.get("profile", {})
            print(f"  Memory: {len(HISTORY)} messages, {len(USER_PROFILE)} profile entries")
    except Exception as e:
        print(f"  Memory load error: {e}")


def save():
    """Save memory to disk."""
    try:
        with LOCK:
            data = {
                "history": HISTORY[-MAX_HISTORY * 2:],
                "profile": USER_PROFILE,
                "saved": time.time(),
            }
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  Memory save error: {e}")


def auto_save_loop():
    """Background thread: save every 60s."""
    while True:
        time.sleep(60)
        save()


def add_user(text):
    """Add user message to history."""
    with LOCK:
        HISTORY.append({"role": "user", "text": text, "time": time.time()})
        if len(HISTORY) > MAX_HISTORY * 2:
            del HISTORY[:len(HISTORY) - MAX_HISTORY * 2]


def add_jarvis(text):
    """Add JARVIS response to history + extract learned preferences."""
    cleaned = extract_learned(text)
    with LOCK:
        HISTORY.append({"role": "claude", "text": cleaned, "time": time.time()})
        if len(HISTORY) > MAX_HISTORY * 2:
            del HISTORY[:len(HISTORY) - MAX_HISTORY * 2]
    save()
    return cleaned


def extract_learned(text):
    """Extract [LEARNED: key = value] tags and update profile."""
    matches = re.findall(r'\[LEARNED:\s*(.+?)\s*=\s*(.+?)\]', text)
    if matches:
        with LOCK:
            for key, val in matches:
                USER_PROFILE[key.strip()] = val.strip()
    return re.sub(r'\s*\[LEARNED:\s*.+?\]', '', text).strip()


def build_context(prompt):
    """Build full prompt with history, profile, and time context."""
    now = datetime.datetime.now()
    with LOCK:
        hc = list(HISTORY)
        profile = dict(USER_PROFILE)

    parts = [f"[KONTEKST CZASOWY] {now.strftime('%A %d %B %Y, %H:%M')} (Europe/Warsaw)"]

    if profile:
        parts.append("\n[PROFIL UZYTKOWNIKA]")
        for k, v in profile.items():
            parts.append(f"- {k}: {v}")

    if hc:
        parts.append("\n[HISTORIA ROZMOWY]")
        for h in hc[-20:]:
            ts = datetime.datetime.fromtimestamp(h.get("time", 0)).strftime("%H:%M") if h.get("time") else "?"
            role = "Sir" if h["role"] == "user" else "JARVIS"
            # Truncate long messages in history
            text = h["text"][:500] + "..." if len(h["text"]) > 500 else h["text"]
            parts.append(f"[{ts}] {role}: {text}")

    parts.append(f"\n[NOWE POLECENIE] {prompt}")
    parts.append("\nOdpowiedz na polecenie Sir. Wykorzystaj kontekst.")
    parts.append("Nowe preferencje oznacz: [LEARNED: klucz = wartosc]")

    return "\n".join(parts)
