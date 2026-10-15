#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1. github_init_upload.py

2. Turn a directory into a GitHub repository,
   with git init + commit + push.

3. Credentials and settings are loaded from external JSON files:
     - credential.github.json
     - settings.project.github.json
   The hardcoded values below are used as FALLBACK if the JSON files
   are missing or invalid.

4. Use:
    python3 github_init_upload.py
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

# ============================================================
# FALLBACK CONFIGURATION (used if JSON files are missing/invalid)
# ============================================================

DIR_WS      = "/mnt/disk01/project531"

GH_USER     = "user001"
GH_EMAIL    = "user001@email.com"
GH_TOKEN    = "ghp_FAKE000f76fg6f6fffiW"

REPO_NAME   = "project531"
REPO_DESC   = "project531"
REPO_VISIB  = "public"          # public | private
REPO_TOPICS = "project531"

BRANCH      = "main"
COMMIT_MSG  = "commit0001: upload message646914"

# ============================================================
# EXTERNAL CONFIG FILES
# ============================================================

BASE_DIR            = os.path.dirname(os.path.abspath(__file__))
CREDENTIAL_FILE     = os.path.join(BASE_DIR, "gitignore.actual.d", "credential.github.json")
SETTINGS_FILE       = os.path.join(BASE_DIR, "settings.project.github.json")


def log(msg):
    print(msg, flush=True)


def load_json(path):
    """Load a JSON file, return dict or None on any problem."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            log(f"  loaded: {path}")
            return data
        log(f"  [WARN] {path} is not a JSON object, using fallback")
        return None
    except FileNotFoundError:
        log(f"  [WARN] {path} not found, using fallback")
        return None
    except Exception as e:
        log(f"  [WARN] {path} invalid ({e}), using fallback")
        return None


def resolve_config():
    """Merge external JSON config over the hardcoded fallback values."""
    cred = load_json(CREDENTIAL_FILE) or {}
    sett = load_json(SETTINGS_FILE) or {}

    cfg = {
        # credentials (fallback -> external)
        "GH_USER":     cred.get("GH_USER",  GH_USER),
        "GH_EMAIL":    cred.get("GH_EMAIL", GH_EMAIL),
        "GH_TOKEN":    cred.get("GH_TOKEN", GH_TOKEN),
        # settings (fallback -> external)
        "DIR_WS":      sett.get("DIR_WS",      DIR_WS),
        "REPO_NAME":   sett.get("REPO_NAME",   REPO_NAME),
        "REPO_DESC":   sett.get("REPO_DESC",   REPO_DESC),
        "REPO_VISIB":  sett.get("REPO_VISIB",  REPO_VISIB),
        "REPO_TOPICS": sett.get("REPO_TOPICS", REPO_TOPICS),
        "BRANCH":      sett.get("BRANCH",      BRANCH),
        "COMMIT_MSG":  sett.get("COMMIT_MSG",  COMMIT_MSG),
    }
    return cfg


def run(cmd, cwd=None, check=True, env=None):
    log(f"$ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=cwd, text=True,
                       capture_output=True, env=env)
    if r.stdout: log(r.stdout.rstrip())
    if r.stderr: log(r.stderr.rstrip())
    if check and r.returncode != 0:
        log(f"[ERRORE] exit={r.returncode}")
        sys.exit(r.returncode)
    return r


def main():
    cfg = resolve_config()

    gh_user     = cfg["GH_USER"]
    gh_email    = cfg["GH_EMAIL"]
    gh_token    = cfg["GH_TOKEN"]
    dir_ws      = cfg["DIR_WS"]
    repo_name   = cfg["REPO_NAME"]
    repo_desc   = cfg["REPO_DESC"]
    repo_visib  = cfg["REPO_VISIB"]
    repo_topics = cfg["REPO_TOPICS"]
    branch      = cfg["BRANCH"]
    commit_msg  = cfg["COMMIT_MSG"]

    ws = Path(dir_ws)
    if not ws.is_dir():
        log(f"[FATAL] directory non trovata: {ws}")
        sys.exit(1)

    os.chdir(ws)
    log(f"== Working dir: {ws}")

    # 1) tools
    for t in ("git", "gh"):
        if shutil.which(t) is None:
            log(f"[FATAL] '{t}' non nel PATH")
            sys.exit(1)

    # 2) git config globale
    run(["git", "config", "--global", "user.name",  gh_user])
    run(["git", "config", "--global", "user.email", gh_email])

    # 3) git init
    if not (ws / ".git").exists():
        run(["git", "init"])
        run(["git", "branch", "-M", branch])
    else:
        log("  .git già presente, salto init")

    # 4) add + commit
    run(["git", "add", "."])
    run(["git", "commit", "-m", commit_msg], check=False)

    # 5) env per gh (token)
    env = os.environ.copy()
    env["GH_TOKEN"] = gh_token

    # 6) auth check -> login con token se serve
    r = run(["gh", "auth", "status"], check=False, env=env)
    if r.returncode != 0:
        log("  login con token...")
        p = subprocess.run(
            ["gh", "auth", "login", "--with-token"],
            input=gh_token + "\n", text=True,
            capture_output=True, env=env
        )
        log(p.stdout); log(p.stderr)

    # 7) crea repo remoto + push
    r = run(["gh", "repo", "view", f"{gh_user}/{repo_name}"],
            check=False, env=env)
    if r.returncode == 0:
        log("  repo remoto esiste già -> imposto remote e pusho")
        run(["git", "remote", "remove", "origin"], check=False)
        url = f"git@github.com:{gh_user}/{repo_name}.git"
        run(["git", "remote", "add", "origin", url])
        run(["git", "push", "-u", "origin", branch])
    else:
        run(["gh", "repo", "create", repo_name,
             f"--{repo_visib}",
             "--source=.", "--remote=origin", "--push"],
            env=env)

    # 8) description + topics
    run(["gh", "repo", "edit", "--description", repo_desc], env=env)
    run(["gh", "repo", "edit", "--add-topic", repo_topics], env=env)

    log("\n✅ Fatto.")
    log(f"   https://github.com/{gh_user}/{repo_name}")


if __name__ == "__main__":
    main()
