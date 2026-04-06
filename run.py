#!/usr/bin/env python3
"""J.A.R.V.I.S. — Enhanced Main Entry Point."""
import http.server
import ssl
import os
import threading
import sys
import json
from queue import Queue
import subprocess
from datetime import datetime
from brain.planner import plan_task
from brain.vector_memory import MEMORY


# Konfiguracja
PORT = 8080
SSL_DIR = "ssl"
USE_SSL = os.path.exists(SSL_DIR)
HISTORY_FILE = "memory/history.json"

# --------------------------
# Prosta pamięć
# --------------------------
HISTORY = []

def load_memory():
    global HISTORY
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            HISTORY = json.load(f)

def save_memory():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(HISTORY, f, indent=2)

# --------------------------
# Task Queue (Planner)
# --------------------------
TASK_QUEUE = Queue()

def add_task(task):
    """Dodaje task do kolejki i do pamięci wektorowej"""
    TASK_QUEUE.put(task)
    MEMORY.add(task, meta={"task": task})
    print(f"[Memory] Task dodany do vector memory: {task}")

def process_tasks():
    while True:
        task = TASK_QUEUE.get()
        if task is None:
            break
        print(f"[Executor] Processing task: {task}")
        execute_task(task)
        TASK_QUEUE.task_done()

def add_goal(goal):
    """Przyjmuje cel od Claude i rozbija go na taski"""
    tasks = plan_task(goal, history=HISTORY)
    for t in tasks:
        add_task(t)
    print(f"[Planner] Rozbiłem cel na {len(tasks)} tasków")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --------------------------
# Executor
# --------------------------
def execute_task(task):
    """Prosty executor: shell, file actions, etc."""
    timestamp = datetime.now().isoformat()
    HISTORY.append({"time": timestamp, "task": task})
    
    if task.startswith("shell:"):
        cmd = task.replace("shell:", "", 1).strip()
        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            print(f"[Shell] {result}")
        except subprocess.CalledProcessError as e:
            print(f"[Shell Error] {e.output}")
    elif task.startswith("log:"):
        msg = task.replace("log:", "", 1).strip()
        print(f"[Log] {msg}")
    # tutaj można dodać więcej typów akcji
    save_memory()

# --------------------------
# HTTP Handler
# --------------------------
class JarvisHandler(http.server.BaseHTTPRequestHandler):
    def _send(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
        

    def do_GET(self):
        if self.path == "/history":
            self._send({"history": HISTORY})
        else:
            self._send({"status": "ready"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        data = json.loads(body)

        # Obsługa goal
        if 'goal' in data:
            add_goal(data['goal'])
            self._send({"status": "goal added", "goal": data['goal']})
            return

        # Obsługa zwykłych tasków
        task = data.get("task")
        if task:
            add_task(task)
            self._send({"status": "task added", "task": task})
            return

        # Brak tasku/goal
        self._send({"status": "no task or goal received"})
            

# --------------------------
# Main
# --------------------------
def main():
    load_memory()
    threading.Thread(target=process_tasks, daemon=True).start()

    server = http.server.HTTPServer(("0.0.0.0", PORT), JarvisHandler)
    
    if USE_SSL:
        server.socket = ssl.wrap_socket(
            server.socket,
            server_side=True,
            certfile=os.path.join(SSL_DIR, "cert.pem"),
            keyfile=os.path.join(SSL_DIR, "key.pem"),
            ssl_version=ssl.PROTOCOL_TLS
        )
    
    print(f"J.A.R.V.I.S. Enhanced running on port {PORT} (SSL={USE_SSL})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        save_memory()
        TASK_QUEUE.put(None)
        server.server_close()

if __name__ == "__main__":
    main()