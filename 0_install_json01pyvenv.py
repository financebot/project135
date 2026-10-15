#!/usr/bin/env python3
"""
0_install_json01pyvenv.py

Crea un virtualenv 'json01pyvenv' in /mnt/d.05a/pyenv/json01pyvenv
per installare tutte le librerie necessarie alla conversione Python_to_json
(BeautifulSoup + html.parser / lxml).
"""

import os
import subprocess
import sys

VENV_DIR = "/mnt/d.05a/pyenv/json01pyvenv"

# Librerie necessarie per la conversione Python_to_json
PACKAGES = [
    "beautifulsoup4",   # BeautifulSoup
    "lxml",             # parser veloce/robusto
    "html5lib",         # parser HTML5 opzionale
    "requests",         # per scaricare HTML
]


def run(cmd):
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    # 1) Crea il venv
    os.makedirs(os.path.dirname(VENV_DIR), exist_ok=True)
    if not os.path.exists(VENV_DIR):
        print(f"Creo il venv in {VENV_DIR} ...")
        run([sys.executable, "-m", "venv", VENV_DIR])
    else:
        print(f"Il venv esiste gia: {VENV_DIR}")

    # 2) Percorsi di pip e python del venv
    pip = os.path.join(VENV_DIR, "bin", "pip")
    python = os.path.join(VENV_DIR, "bin", "python")

    # 3) Aggiorna pip
    run([pip, "install", "--upgrade", "pip"])

    # 4) Installa le librerie
    run([pip, "install"] + PACKAGES)

    # 5) Verifica
    print("\n--- Verifica installazione ---")
    run([python, "-c", "import bs4, lxml; print('bs4', bs4.__version__); print('lxml', lxml.__version__)"])

    print(f"\nFatto. Per attivare: source {VENV_DIR}/bin/activate")


if __name__ == "__main__":
    main()
