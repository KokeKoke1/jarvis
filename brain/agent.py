"""JARVIS agent — runs Claude tasks with streaming, stages, and stop support."""
import subprocess, json, time, threading
from .config import CLAUDE_BIN, SYSTEM_PROMPT, TOOL_NAMES, TIMEOUT
from . import memory

LOCK = threading.Lock()
JOBS = {}
JOB_COUNTER = 0
PROCESSES = {}


def new_job(prompt):
    """Create a new job and start it in background."""
    global JOB_COUNTER
    with LOCK:
        JOB_COUNTER += 1
        jid = JOB_COUNTER
        JOBS[jid] = {
            "id": jid, "prompt": prompt, "status": "running",
            "result": "", "started": time.time(), "elapsed": "",
            "stage": "Mysle...", "stage_tool": "thinking",
        }
    threading.Thread(target=_run, args=(jid, prompt), daemon=True).start()
    return jid


def stop_job(jid):
    """Stop a running job."""
    with LOCK:
        if jid in JOBS and JOBS[jid]["status"] == "running":
            JOBS[jid]["status"] = "stopped"
            JOBS[jid]["result"] = "Zatrzymane przez uzytkownika"
            JOBS[jid]["stage"] = ""
            proc = PROCESSES.get(jid)
            if proc:
                try:
                    proc.kill()
                except:
                    pass
            return True
    return False


def get_jobs():
    """Get all jobs sorted by time (newest first)."""
    with LOCK:
        return sorted(JOBS.values(), key=lambda j: j["started"], reverse=True)[:30]


def _run(job_id, prompt):
    """Execute Claude with streaming output and stage tracking."""
    memory.add_user(prompt)
    full_prompt = memory.build_context(prompt)

    try:
        proc = subprocess.Popen(
            [CLAUDE_BIN, "-p", full_prompt,
             "--output-format", "stream-json", "--verbose",
             "--dangerously-skip-permissions",
             "--append-system-prompt", SYSTEM_PROMPT],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            cwd=memory.os.path.expanduser("~/Documents/AI Core")
        )
        with LOCK:
            PROCESSES[job_id] = proc

        start = time.time()
        result_text = ""

        for line in proc.stdout:
            # Check if stopped
            with LOCK:
                if JOBS.get(job_id, {}).get("status") == "stopped":
                    proc.kill()
                    PROCESSES.pop(job_id, None)
                    return

            elapsed = time.time() - start
            if elapsed > 10:
                mins, secs = int(elapsed // 60), int(elapsed % 60)
                with LOCK:
                    JOBS[job_id]["elapsed"] = f"{mins}m {secs}s"

            if elapsed > TIMEOUT:
                proc.kill()
                with LOCK:
                    JOBS[job_id]["status"] = "error"
                    JOBS[job_id]["result"] = f"Timeout po {int(elapsed // 60)}m. Podziel zadanie na mniejsze kroki, Sir."
                    JOBS[job_id]["stage"] = ""
                    PROCESSES.pop(job_id, None)
                return

            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                _parse_stage(job_id, data)
                if data.get("type") == "result":
                    result_text = data.get("result", "")
            except json.JSONDecodeError:
                pass

        proc.wait()

        if not result_text:
            result_text = proc.stderr.read().strip() or "(brak odpowiedzi)"

        with LOCK:
            if JOBS.get(job_id, {}).get("status") == "stopped":
                PROCESSES.pop(job_id, None)
                return

        # Process response through memory (extracts [LEARNED:] tags)
        cleaned = memory.add_jarvis(result_text)

        with LOCK:
            JOBS[job_id]["status"] = "done"
            JOBS[job_id]["result"] = cleaned
            JOBS[job_id]["stage"] = ""
            PROCESSES.pop(job_id, None)

    except Exception as e:
        with LOCK:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["result"] = f"Blad: {e}"
            JOBS[job_id]["stage"] = ""
            PROCESSES.pop(job_id, None)


def _parse_stage(job_id, data):
    """Extract current tool/stage from stream-json data."""
    msg = data.get("message", {})
    content = msg.get("content", [])
    if not isinstance(content, list):
        return
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        tool = block.get("name", "")
        stage_text = TOOL_NAMES.get(tool, f"Uzywa {tool}...")
        inp = block.get("input", {})
        if tool == "Bash" and "command" in inp:
            stage_text = f"$ {inp['command'][:80]}"
        elif tool in ("Edit", "Write", "Read") and "file_path" in inp:
            fname = inp["file_path"].split("/")[-1]
            stage_text = f"{TOOL_NAMES.get(tool, tool)} {fname}"
        with LOCK:
            JOBS[job_id]["stage"] = stage_text
            JOBS[job_id]["stage_tool"] = tool
