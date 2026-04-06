#!/usr/bin/env python3
"""J.A.R.V.I.S. — Main entry point."""
import http.server, ssl, os, threading, sys

# Add parent to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.brain.config import PORT, SSL_DIR
from jarvis.brain import memory
from jarvis.server.handler import JarvisHandler


def get_ip():
    """Get local IP address."""
    import subprocess
    try:
        return subprocess.check_output(["ipconfig", "getifaddr", "en0"],
                                        text=True).strip()
    except:
        try:
            return subprocess.check_output(["ipconfig", "getifaddr", "en1"],
                                            text=True).strip()
        except:
            return "localhost"


def main():
    # Load persistent memory
    memory.load()

    # Start auto-save thread
    threading.Thread(target=memory.auto_save_loop, daemon=True).start()

    # Create server
    server = http.server.HTTPServer(("0.0.0.0", PORT), JarvisHandler)

    # SSL setup
    cert_file = os.path.join(SSL_DIR, "cert.pem")
    key_file = os.path.join(SSL_DIR, "key.pem")
    use_ssl = False
    if os.path.exists(cert_file) and os.path.exists(key_file):
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.set_ciphers('DEFAULT:!aNULL:!eNULL:!MD5')
            ctx.load_cert_chain(cert_file, key_file)
            server.socket = ctx.wrap_socket(server.socket, server_side=True)
            use_ssl = True
        except Exception as e:
            print(f"  SSL failed: {e}")

    proto = "https" if use_ssl else "http"
    ip = get_ip()

    print(f"""
\033[38;5;214m
       ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
       ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
       ██║███████║██████╔╝██║   ██║██║███████╗
  ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
  ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
   ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
\033[0m
  \033[1mJ.A.R.V.I.S.\033[0m  v5.1 — Just A Rather Very Intelligent System
  ──────────────────────────────────────────
  \033[38;5;214m>\033[0m Phone:   {proto}://{ip}:{PORT}
  \033[38;5;214m>\033[0m Local:   {proto}://localhost:{PORT}
  \033[38;5;214m>\033[0m SSL:     {'ON' if use_ssl else 'OFF'}
  \033[38;5;214m>\033[0m Memory:  {len(memory.HISTORY)} messages
  ──────────────────────────────────────────
  "At your service, Sir."
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down... saving memory.")
        memory.save()
        server.server_close()
        print("  Goodbye, Sir.")


if __name__ == "__main__":
    main()

