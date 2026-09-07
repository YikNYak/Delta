#!/usr/bin/env python3
"""
Delta — Made by okaydrku — https://discord.com/users/920058671281602660
OGS-Style Terminal | V1 — 24.08.2026
See HOW_IT_WORKS.txt for details
"""
from __future__ import annotations
import argparse, json, os, re, shutil, sys, zipfile, tempfile, io, webbrowser, secrets, hashlib, base64
from pathlib import Path
import pathlib
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote


# ============================================================
# DELTA — OGS-STYLE TERMINAL
# Visual only — no actual features
# ============================================================

# Enable ANSI support on Windows
if os.name == "nt":
    os.system("")

try:
    from rich.console import Console
    from rich.text import Text
    from rich.align import Align
    import pyfiglet
except ImportError:
    print("Missing requirements.")
    print()
    print("Install them with:")
    print("    pip install rich pyfiglet")
    print()
    input("Press Enter to exit...")
    sys.exit(1)


console = Console(legacy_windows=False, force_terminal=True)

def banner():
    logo = make_logo()
    for line in logo:
        console.print(Align.center(line))
    console.print()
    print_header()
try:
    from colorama import Fore as _Fore, Style as _Style
    Fore = _Fore
    Style = _Style
except:
    class Fore:
        CYAN=""; GREEN=""; YELLOW=""; RED=""; MAGENTA=""; WHITE=""; BLUE=""
    class Style:
        BRIGHT=""; RESET_ALL=""; DIM="" 

try:
    import requests
    SESSION = requests.Session()
    SESSION.headers.update({"User-Agent":"Mozilla/5.0"})
except ImportError:
    print("Missing requirements.")
    print("pip install requests rich pyfiglet")
    import sys as _sys
    _sys.exit(1)

# fix Windows cp1252 console for Cyrillic fix titles (like S&Box)
import html
# Detect utf support: need tty + utf encoding + chcp 65001 on Windows
try:
    _orig_enc = (sys.stdout.encoding or "").lower()
except:
    _orig_enc = ""
IS_UTF = "utf" in _orig_enc or "utf" in (os.environ.get("PYTHONIOENCODING","").lower()) or "utf" in (os.environ.get("PYTHONUTF8","").lower())
if not IS_UTF and os.name == "nt":
    try:
        import subprocess as _sp
        cp = _sp.check_output("chcp", shell=True, text=True, stderr=_sp.DEVNULL)
        if "65001" in cp:
            IS_UTF = True
    except: pass
try:
    import sys as _sys2
    _sys2.stdout.reconfigure(encoding='utf-8', errors='replace')
    _sys2.stderr.reconfigure(encoding='utf-8', errors='replace')
except: pass


# ------------------------------------------------------------
# COLORS
# ------------------------------------------------------------

PINK = "#ff00d9"
HOT_PINK = "#ff00ee"
PURPLE = "#a000ff"
DARK_PURPLE = "#4d0088"
VERY_DARK_PURPLE = "#250044"

WHITE = "#eeeeee"
GRAY = "#777777"
DARK_GRAY = "#3d3d3d"


# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------

UI_MARGIN = 5
LOGO_FONT = "ansi_shadow"
# Fallback for Windows cmd without utf-8 (block chars fail)
try:
    enc = (sys.stdout.encoding or "").lower()
    if "utf" not in enc:
        LOGO_FONT = "standard"
except:
    pass


# ------------------------------------------------------------
# COLOR UTILITIES
# ------------------------------------------------------------

def interpolate(c1, c2, t):
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)

    return r, g, b


def hex_rgb(value):
    value = value.lstrip("#")

    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )


def gradient_colors():
    return [
        hex_rgb("#ff00e6"),
        hex_rgb("#e000ff"),
        hex_rgb("#a000ff"),
        hex_rgb("#6500c9"),
    ]


def gradient_at(t):
    colors = gradient_colors()

    t = max(0.0, min(1.0, t))

    scaled = t * (len(colors) - 1)

    index = min(
        int(scaled),
        len(colors) - 2
    )

    local_t = scaled - index

    return interpolate(
        colors[index],
        colors[index + 1],
        local_t
    )


# ------------------------------------------------------------
# LOGO
# ------------------------------------------------------------

def make_logo():
    try:
        raw = pyfiglet.figlet_format(
            "DELTA",
            font=LOGO_FONT
        )
    except:
        raw = "DELTA"

    lines = raw.rstrip("\n").splitlines()

    lines = [
        line.rstrip()
        for line in lines
        if line.strip()
    ]

    max_width = max(
        len(line)
        for line in lines
    )

    result = []

    for y, line in enumerate(lines):

        t = y / max(
            1,
            len(lines) - 1
        )

        r, g, b = gradient_at(t)

        text = Text()

        padding = max(
            0,
            (max_width - len(line)) // 2
        )

        centered = (
            " " * padding
            + line
        )

        for char in centered:

            if char == " ":
                text.append(" ")

            else:
                text.append(
                    char,
                    style=f"rgb({r},{g},{b}) bold"
                )

        result.append(text)

    return result


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

def make_header():
    header = Text()

    header.append(
        "dev: ",
        style="rgb(105,105,105)"
    )

    header.append(
        "okaydrku",
        style="white"
    )

    header.append(
        "     |     ",
        style="rgb(85,85,85)"
    )

    header.append(
        "discord: ",
        style="rgb(105,105,105)"
    )

    header.append(
        "@okaydrku",
        style="rgb(150,0,255)"
    )

    header.append(
        "     |     ",
        style="rgb(85,85,85)"
    )

    header.append(
        "Edition: ",
        style="rgb(105,105,105)"
    )

    header.append(
        "Private V1.8",
        style="rgb(255,0,210) bold"
    )

    return header


def print_header():

    header = make_header()

    # Center header directly underneath DELTA
    console.print(
        Align.center(header)
    )

    # Slightly longer bar than the header
    separator = "─" * (
        len(header.plain) + 8
    )

    console.print(
        Align.center(separator)
    )

    console.print()


# ------------------------------------------------------------
# MAIN MENU HEADER
# ------------------------------------------------------------

def menu_header():

    text = Text()

    text.append(
        " " * UI_MARGIN
    )

    text.append(
        "╭",
        style="rgb(65,65,65)"
    )

    text.append(
        "────── ",
        style="rgb(65,65,65)"
    )

    text.append(
        "MAIN MENU",
        style="white bold"
    )

    text.append(
        " ────────────────────",
        style="rgb(65,65,65)"
    )

    console.print(text)

    console.print()


# ------------------------------------------------------------
# MENU OPTIONS
# ------------------------------------------------------------

def option(number, title, description):

    prefix = " " * UI_MARGIN

    # Main option
    text = Text()

    text.append(prefix)

    text.append(
        str(number),
        style=f"{PINK} bold"
    )

    text.append("  ")

    text.append(
        "|",
        style="rgb(65,65,65)"
    )

    text.append(" ")

    text.append(
        title,
        style="white"
    )

    console.print(text)

    # Description with connected ╰─
    desc = Text()

    desc.append(prefix)

    desc.append("   ")

    desc.append(
        "╰─",
        style="rgb(65,65,65)"
    )

    desc.append("   ")

    desc.append(
        description,
        style="rgb(75,75,75)"
    )

    console.print(desc)

    # Space between options
    console.print()


# ------------------------------------------------------------
# PROMPT
# ------------------------------------------------------------

def prompt():

    text = Text()

    text.append(
        " " * UI_MARGIN
    )

    text.append(
        "Select option ",
        style="white"
    )

    text.append(
        "›",
        style=f"{PINK} bold"
    )

    console.print(
        text,
        end=" "
    )

    try:
        return input()
    except (KeyboardInterrupt, EOFError):
        console.print("\n  Exiting...", style="rgb(120,120,120)")
        raise SystemExit(0)


# ------------------------------------------------------------
# DETAIL HEADER — styled like n.py option 3 (╭────── ... ─────────────────)
# ------------------------------------------------------------
def detail_header(title: str):
    text = Text()
    text.append(" " * UI_MARGIN)
    text.append("╭", style=DARK_GRAY)
    text.append("────── ", style=DARK_GRAY)
    text.append(title, style="white bold")
    text.append(" ─────────────────", style=DARK_GRAY)
    console.print(text)
    console.print()

def show_about():
    console.clear()
    # Logo
    logo = make_logo()
    for line in logo:
        console.print(Align.center(line))
    console.print()
    print_header()
    detail_header("ABOUT DELTA")
    # Under header — left aligned with UI_MARGIN (not centered)
    info = Text()
    info.append(" " * UI_MARGIN, style="white")
    info.append("Made by ", style="rgb(120,120,120)")
    info.append("@okaydrku", style="white bold")
    console.print(info)
    link = Text()
    link.append(" " * UI_MARGIN, style="white")
    link.append("https://discord.com/users/920058671281602660", style="rgb(150,0,255) underline")
    console.print(link)
    console.print()
    date = Text()
    date.append(" " * UI_MARGIN, style="white")
    date.append("Released on ", style="rgb(100,100,100)")
    date.append("24.08.2026", style="white")
    console.print(date)
    console.print()
    # Special thanks box
    box_top = Text()
    box_top.append(" " * UI_MARGIN + "╭─ Special Thanks ", style=DARK_GRAY)
    box_top.append("─" * 22, style=DARK_GRAY)
    console.print(box_top)
    # Use ascii fallbacks if not utf8
    _is_utf = "utf" in (sys.stdout.encoding or "").lower()
    star = "★" if _is_utf else "*"
    dash = " — " if _is_utf else " - "
    heart = "♥" if _is_utf else "<3"
    thanks = [
        ("Online-Fix", "online multiplayer patches & community fixes"),
        ("Public Resources", "Steam API, SteamDB, api.steamcmd.net"),
    ]
    for name, desc in thanks:
        line = Text()
        line.append(" " * UI_MARGIN + "│  ", style=DARK_GRAY)
        line.append(f"{star} ", style="#ffff00" if _is_utf else "yellow")
        line.append(f"{name:<16}", style="white bold")
        line.append(f"{dash}{desc}", style="rgb(90,90,90)")
        console.print(line)
    bottom = Text()
    bottom.append(" " * UI_MARGIN + "╰" + "─" * 38, style=DARK_GRAY)
    console.print(bottom)
    console.print()
    footer = Text()
    footer.append("  Delta — unlock, fix & play. Made with ", style="rgb(80,80,80)")
    footer.append(heart, style="#ff00d9")
    console.print(Align.center(footer))
    console.print()
    pr = Text()
    pr.append("  Press Enter to return ", style="white")
    pr.append("›", style=f"{PINK} bold")
    console.print(pr, end=" ")
    try:
        input()
    except: pass

# ---------- Auth (Supabase PKCE like Delta AuthService, 25/day) ----------
CACHE_FILE = Path(os.environ.get("APPDATA", str(Path.home()))) / "Delta" / "cache.json"
VAULT_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / "Delta" / "vault"
TOKEN_FILE = Path(__file__).parent / ".delta_token"
SUPABASE_URL = base64.b64decode("aHR0cHM6Ly9kYi5sdWEudG9vbHM=").decode()
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NzYwMzkzNzYsImV4cCI6MTg5MzQ1NjAwMCwicm9sZSI6ImFub24iLCJpc3MiOiJzdXBhYmFzZSJ9.f_-K38u3odjltP-g_67FVmG32Vg-_-k-lNBvIaVUVBM"
API_BASE = base64.b64decode("aHR0cHM6Ly9sdWEudG9vbHM=").decode()
OAUTH_PORT = 53789
OAUTH_URL = f"http://localhost:{OAUTH_PORT}/callback"

def b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def get_auth_token() -> str | None:
    if os.environ.get("DELTA_TOKEN"):
        return os.environ["DELTA_TOKEN"].strip()
    if TOKEN_FILE.exists():
        try:
            raw = TOKEN_FILE.read_text(encoding="utf-8").strip()
            if not raw:
                return None
            j = json.loads(raw) if raw.startswith("{") else None
            if isinstance(j, dict) and "access_token" in j:
                return j["access_token"]
            if j and isinstance(j, dict):
                # fallback if json but no access_token
                pass
            if len(raw) > 20 and not raw.startswith("{"):
                return raw
            if raw.startswith("{"):
                try:
                    return json.loads(raw).get("access_token")
                except:
                    pass
        except:
            pass
    return None

def save_auth_session(access_token: str, refresh_token: str = "", expires_in: int = 3600):
    try:
        data = {"access_token": access_token, "refresh_token": refresh_token, "expires_at": time.time() + expires_in}
        TOKEN_FILE.write_text(json.dumps(data), encoding="utf-8")
        print(f"{Fore.GREEN}[+] Login saved to {TOKEN_FILE}{Style.RESET_ALL}")
    except Exception as e:
        print(f"[!] Could not save token: {e}")

def save_auth_token(token: str):
    save_auth_session(token, "", 3600)

def prompt_login() -> str | None:
    print(f"\n{Fore.YELLOW}[!] Fixes download requires login (Delta, 25/day limit){Style.RESET_ALL}")
    print("    Run Delta login for auto browser PKCE (recommended)")
    print("    Or paste token from F12 -> Application -> Local Storage -> sb-db-auth-token")
    t = input("Token (Enter to skip): ").strip().strip('"').strip("'")
    if not t or len(t) < 20:
        return None
    # Handle full JSON paste (user pasted whole localStorage value)
    try:
        if t.strip().startswith("{") or '"access_token"' in t:
            # Try to parse as JSON (may be double-encoded)
            import json as _json
            # The pasted value from the user was a JSON string containing the session object
            # Try to extract access_token
            # First, try direct JSON
            try:
                j = _json.loads(t)
                if isinstance(j, dict) and "access_token" in j:
                    t = j["access_token"]
                elif isinstance(j, dict) and "access_token" in str(j):
                    # nested
                    pass
            except:
                # Try to find access_token via regex
                import re as _re
                m = _re.search(r'"access_token"\s*:\s*"([^"]+)"', t)
                if m:
                    t = m.group(1)
                else:
                    # Try base64 decode? The pasted value was base64 JSON
                    import base64 as _b64
                    try:
                        # The pasted value was like "jcxMjgxNjAy..." which is base64
                        # Try to decode
                        decoded = _b64.b64decode(t + "==").decode('utf-8', errors='ignore')
                        m2 = _re.search(r'"access_token"\s*:\s*"([^"]+)"', decoded)
                        if m2:
                            t = m2.group(1)
                    except: pass
    except: pass
    if len(t) > 20:
        save_auth_token(t)
        return t
    return None

def auth_headers(token: str | None = None) -> dict:
    tok = token or get_auth_token()
    h = {"User-Agent":"Mozilla/5.0"}
    if tok:
        h["Authorization"] = f"Bearer {tok}"
        h["apikey"] = SUPABASE_ANON_KEY
    return h

def _load_cache():
    try:
        if CACHE_FILE.exists():
            j = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            if isinstance(j, dict) and "_ts" in j:
                if time.time() - j["_ts"] > 14*24*3600:
                    return {}
            return j
    except: pass
    return {}

def _save_cache(d):
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        d["_ts"] = time.time()
        CACHE_FILE.write_text(json.dumps(d), encoding="utf-8")
    except: pass

def _vault_hash(data: bytes) -> str:
    import hashlib as _hl
    return _hl.sha256(data).hexdigest()[:16]

def vault_capture(appid: str, data: bytes, buildid: str | None = None):
    try:
        h = _vault_hash(data)
        appid = str(appid)
        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        app_dir = VAULT_DIR / appid
        app_dir.mkdir(parents=True, exist_ok=True)
        name = f"{appid}_{buildid}.lua" if buildid else f"{appid}_{h}.lua"
        (app_dir / name).write_bytes(data)
        (app_dir / f"{appid}.lua").write_bytes(data)
        idx = app_dir / "index.json"
        j = {}
        if idx.exists():
            try: j = json.loads(idx.read_text(encoding="utf-8"))
            except: j = {}
        j[h] = {"buildid": buildid, "ts": time.time(), "size": len(data)}
        idx.write_text(json.dumps(j, indent=2), encoding="utf-8")
    except: pass

def do_pkce_login():
    verifier = b64url(secrets.token_bytes(32))
    challenge = b64url(hashlib.sha256(verifier.encode()).digest())
    auth_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=discord&redirect_to={quote(OAUTH_URL)}&code_challenge={challenge}&code_challenge_method=s256"
    # start local server
    code_holder = {}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            qs = parse_qs(urlparse(self.path).query)
            code = qs.get("code", [None])[0]
            err = qs.get("error_description", [None])[0]
            if code:
                code_holder["code"] = code
                self.send_response(200)
                self.send_header("Content-Type","text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Delta login success - return to cmd</h1>")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f"<h1>Error: {err}</h1>".encode())
        def log_message(self, *a, **k): pass
    httpd = HTTPServer(("127.0.0.1", OAUTH_PORT), Handler)
    import threading
    th = threading.Thread(target=httpd.handle_request, daemon=True)
    th.start()
    print(f"{Fore.CYAN}[*] Opening browser for Discord login...{Style.RESET_ALL}")
    print(f"    {auth_url}")
    webbrowser.open(auth_url)
    print("    Waiting for callback on http://localhost:53789/callback (5 min)...")
    th.join(timeout=300)
    httpd.server_close()
    code = code_holder.get("code")
    if not code:
        print(f"{Fore.RED}[!] Login timed out or denied{Style.RESET_ALL}")
        return None
    # exchange code for session
    try:
        r = requests.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=pkce",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type":"application/json"},
            json={"auth_code": code, "code_verifier": verifier}, timeout=15)
        r.raise_for_status()
        j = r.json()
        access = j.get("access_token")
        refresh = j.get("refresh_token","")
        expires = j.get("expires_in",3600)
        if access:
            save_auth_session(access, refresh, expires)
            print(f"{Fore.GREEN}[+] Logged in as {j.get('user',{}).get('email','')}{Style.RESET_ALL}")
            return access
    except Exception as e:
        print(f"{Fore.RED}[!] Token exchange failed: {e}{Style.RESET_ALL}")
    return None

# ---------- Steam discovery ----------
def find_steam_path() -> Path | None:
    # 1. env override
    if os.environ.get("STEAM_PATH"):
        p = Path(os.environ["STEAM_PATH"])
        if p.exists():
            return p
    # 2. registry
    try:
        import winreg  # type: ignore
        for hive, key in [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
        ]:
            try:
                with winreg.OpenKey(hive, key) as k:
                    v, _ = winreg.QueryValueEx(k, "SteamPath")
                    if v and Path(v).exists():
                        return Path(v)
                    v2, _ = winreg.QueryValueEx(k, "InstallPath")
                    if v2 and Path(v2).exists():
                        return Path(v2)
            except FileNotFoundError:
                continue
    except Exception:
        pass
    # 3. common defaults
    for cand in [
        Path("C:/Program Files (x86)/Steam"),
        Path("C:/Program Files/Steam"),
        Path.home() / ".steam/steam",
        Path.home() / ".local/share/Steam",
    ]:
        if (cand / "steam.exe").exists() or (cand / "steam.sh").exists() or cand.exists():
            return cand
    return None

def st_plugin_dir(steam_path: Path) -> Path:
    # Delta watches <steam>/config/stplug-in  (new) and <steam>/config/st_plugin on older builds
    # Also supports custom lua paths via delta.toml [lua] paths = []
    primary = steam_path / "config" / "stplug-in"
    legacy = steam_path / "config" / "st_plugin"
    # prefer primary; create if neither exists
    if primary.exists():
        return primary
    if legacy.exists():
        return legacy
    return primary  # will be created

def game_install_dir(steam_path: Path, appid: str | int) -> Path | None:
    """Try to find installed game folder via libraryfolders.vdf + appmanifest"""
    steamapps = steam_path / "steamapps"
    # check main
    m = steamapps / f"appmanifest_{appid}.acf"
    if m.exists():
        # parse installdir
        try:
            txt = m.read_text(encoding="utf-8", errors="ignore")
            mm = re.search(r'"installdir"\s+"([^"]+)"', txt)
            if mm:
                return steamapps / "common" / mm.group(1)
        except: pass
        return steamapps / "common"  # fallback
    # scan libraryfolders
    try:
        lib = steamapps / "libraryfolders.vdf"
        if lib.exists():
            txt = lib.read_text(errors="ignore")
            paths = re.findall(r'"path"\s+"([^"]+)"', txt)
            for p in paths:
                cand = Path(p.replace("\\\\", "\\")) / "steamapps" / f"appmanifest_{appid}.acf"
                if cand.exists():
                    txt2 = cand.read_text(errors="ignore")
                    mm = re.search(r'"installdir"\s+"([^"]+)"', txt2)
                    if mm:
                        return Path(p.replace("\\\\","\\")) / "steamapps" / "common" / mm.group(1)
    except: pass
    # fallback guess: steamapps/common/<appid>
    return None

# ---------- Search ----------
def steam_search_store(term: str, cc="US", lang="english") -> list[dict]:
    """Public Steam Store search — no auth needed (mirrors  search)"""
    url = "https://store.steampowered.com/api/storesearch/"
    params = {"term": term, "l": lang, "cc": cc}
    r = requests.get(url, params=params, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    data = r.json()
    return data.get("items", [])

def steam_details(appid: str | int) -> dict | None:
    """Try Delta public details first, fallback to store API — cached like SteamAppInfoCache"""
    appid = str(appid)
    # Check cache first (14d TTL)
    try:
        cache = _load_cache()
        key = f"details_{appid}"
        if key in cache:
            return cache[key]
    except: pass
    # Delta backend endpoint (public, no auth)
    try:
        r = SESSION.get(f"{base64.b64decode("aHR0cHM6Ly9sdWEudG9vbHM=").decode()}/api/steam/details", params={"appid": appid}, timeout=8)
        if r.ok:
            j = r.json()
            if j and "name" in j:
                res = {"appid": j["appid"], "name": j["name"], "type": j.get("type","game"), "header": j.get("headerImage")}
                try:
                    c = _load_cache()
                    c[f"details_{appid}"] = res
                    _save_cache(c)
                except: pass
                return res
    except: pass
    # fallback: store appdetails
    try:
        r = SESSION.get(f"https://store.steampowered.com/api/appdetails", params={"appids": appid, "l":"english"}, timeout=8)
        if r.ok:
            j = r.json()
            if j.get(appid, {}).get("success"):
                d = j[appid]["data"]
                return {"appid": int(appid), "name": d["name"], "type": d.get("type","game"), "header": d.get("header_image")}
    except: pass
    return None

def delta_fixes_index() -> list[dict]:
    """Scrape /fixes page + public API — returns [{appid,name,header,fixCount}]"""
    # Try public API first (same as Delta: /api/denuvo/listings)
    try:
        r = requests.get(base64.b64decode("aHR0cHM6Ly9sdWEudG9vbHMvYXBpL2RlbnV2by9saXN0aW5ncw==").decode(), timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        if r.ok:
            j = r.json()
            games = j.get("games", []) if isinstance(j, dict) else []
            if games:
                return [{"appid": str(g.get("AppId") or g.get("appid") or g.get("appId")), "name": g.get("Name") or g.get("name"), "header": g.get("HeaderImage") or "", "fixCount": g.get("FixCount", 1)} for g in games[:100]]
    except: pass
    # Fallback: scrape /fixes page
    try:
        r = requests.get(base64.b64decode("aHR0cHM6Ly9sdWEudG9vbHMvZml4ZXM=").decode(), timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        html = r.text
        appids = re.findall(r'href="/fixes/(\d+)"', html)
        seen=set(); uniq=[]
        for a in appids:
            if a not in seen:
                seen.add(a); uniq.append(a)
        out=[]
        for a in uniq[:100]:
            d = steam_details(a)
            out.append({"appid":a, "name": d["name"] if d else f"App {a}", "header": d.get("header") if d else ""})
        return out
    except Exception as e:
        print(f"[!] fixes index fetch failed: {e}")
        return []

def get_denuvo_fixes(appid: str | int) -> list[dict]:
    """Fetch fixes for a game via public /api/denuvo/fixes?appid= (no auth)"""
    try:
        r = requests.get(f"{base64.b64decode("aHR0cHM6Ly9sdWEudG9vbHM=").decode()}/api/denuvo/fixes?appid={appid}", timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        if r.ok:
            j = r.json()
            # Delta returns {Fixes:[{Id,Title,Description,Tags,HasManifest,HasFix}]}
            if isinstance(j, dict) and "Fixes" in j:
                return j["Fixes"]
            if isinstance(j, dict) and "fixes" in j:
                return j["fixes"]
            if isinstance(j, list):
                return j
    except Exception as e:
        print(f"[!] get fixes failed: {e}")
    return []

def get_fix_signed_url(fix_id: str, slot: str, token: str | None = None) -> str | None:
    """DownloadDenuvoAsync: GET /api/denuvo/download?fix=&slot= with Bearer, returns signed R2 URL. Handles 401 by PKCE login."""
    headers = {"User-Agent":"Mozilla/5.0"}
    tok = token or get_auth_token()
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
        headers["apikey"] = SUPABASE_ANON_KEY
    try:
        r = SESSION.get(f"{API_BASE}/api/denuvo/download?fix={fix_id}&slot={slot}", headers=headers, timeout=15)
        if r.status_code == 401:
            print(f"{Fore.YELLOW}[!] 401 Unauthorized — login required (like Delta Status, 25/day){Style.RESET_ALL}")
            print(f"  Opening browser for Discord login (same as Status → Login)...")
            tok = do_pkce_login()
            if tok:
                headers["Authorization"] = f"Bearer {tok}"
                headers["apikey"] = SUPABASE_ANON_KEY
                r = SESSION.get(f"{API_BASE}/api/denuvo/download?fix={fix_id}&slot={slot}", headers=headers, timeout=15)
        if r.ok:
            j = r.json()
            url = j.get("Url") or j.get("url")
            if url:
                return url
            print(f"[!] No URL in response: {j}")
        else:
            try:
                print(f"[!] Download failed {r.status_code}: {r.text[:400]}")
            except: pass
    except Exception as e:
        print(f"[!] Fix download error: {e}")
    return None

def set_launch_options(appid: str | int, enable_onlinefix: bool = True, steam_path: Path | None = None) -> bool:
    """Add/remove -onlinefix to LaunchOptions in localconfig.vdf like Delta."""
    if steam_path is None:
        steam_path = find_steam_path()
    if not steam_path:
        print("[!] Steam not found")
        return False
    userdata = steam_path / "userdata"
    if not userdata.exists():
        print("[!] userdata not found")
        return False
    appid_str = str(appid)
    found = False
    for userdir in userdata.iterdir():
        cfg = userdir / "config" / "localconfig.vdf"
        if not cfg.exists():
            continue
        try:
            txt = cfg.read_text(encoding="utf-8", errors="ignore")
            # Check if appid block exists
            if f'"{appid_str}"' not in txt:
                if enable_onlinefix and '"Apps"' in txt:
                    # Insert new app block with LaunchOptions
                    # Find Apps { and insert after it
                    import re as _re
                    pat = r'("Apps"\s*\{)'
                    repl = r'\1\n\t\t\t"' + appid_str + '"\n\t\t\t{\n\t\t\t\t"LaunchOptions"\t\t"-onlinefix"\n\t\t\t}'
                    new_txt, n = _re.subn(pat, repl, txt, count=1)
                    if n:
                        cfg.write_text(new_txt, encoding="utf-8")
                        print(f"[+] Added -onlinefix to {cfg} for {appid_str} (new entry)")
                        found = True
                        break
                continue
            # App exists — find its LaunchOptions line
            import re as _re
            # Find the appid block and its LaunchOptions
            # Use a pattern that captures the LaunchOptions value near appid
            idx = txt.find(f'"{appid_str}"')
            snippet = txt[idx:idx+3000]
            m = _re.search(r'"LaunchOptions"\s+"([^"]*)"', snippet)
            if enable_onlinefix:
                if m:
                    cur = m.group(1)
                    if "-onlinefix" not in cur:
                        new_val = (cur + " -onlinefix").strip()
                        # Replace only this app's LaunchOptions
                        new_snippet = snippet.replace(f'"LaunchOptions"\t\t"{cur}"', f'"LaunchOptions"\t\t"{new_val}"', 1)
                        # Fallback if tabs differ
                        if new_snippet == snippet:
                            new_snippet = snippet.replace(f'"LaunchOptions" "{cur}"', f'"LaunchOptions" "{new_val}"', 1)
                        if new_snippet == snippet:
                            new_snippet = _re.sub(r'"LaunchOptions"\s+"[^"]*"', f'"LaunchOptions"\t\t"{new_val}"', snippet, count=1)
                        txt = txt[:idx] + new_snippet + txt[idx+3000:]
                        cfg.write_text(txt, encoding="utf-8")
                        print(f"[+] Added -onlinefix to {appid_str} in {cfg}")
                    else:
                        print(f"[*] Already has -onlinefix for {appid_str}")
                    found = True
                    break
                else:
                    # No LaunchOptions yet, insert it inside app block: after "appid" {
                    pat2 = f'"{appid_str}"\\s*\\{{'
                    new_txt, n = _re.subn(pat2, f'"{appid_str}"\\n\\t\\t\\t{{\\n\\t\\t\\t\\t"LaunchOptions"\\t\\t"-onlinefix"', txt, count=1)
                    if n:
                        cfg.write_text(new_txt, encoding="utf-8")
                        print(f"[+] Added -onlinefix to {appid_str} (new LaunchOptions)")
                        found = True
                        break
            else:
                # Remove
                if m:
                    cur = m.group(1)
                    if "-onlinefix" in cur:
                        new_val = cur.replace("-onlinefix","").strip().replace("  "," ")
                        # Replace
                        new_snippet = snippet.replace(f'"LaunchOptions"\t\t"{cur}"', f'"LaunchOptions"\t\t"{new_val}"', 1)
                        if new_snippet == snippet:
                            new_snippet = _re.sub(r'"LaunchOptions"\s+"[^"]*"', f'"LaunchOptions"\t\t"{new_val}"' if new_val else '"LaunchOptions"\t\t""', snippet, count=1)
                        txt = txt[:idx] + new_snippet + txt[idx+3000:]
                        cfg.write_text(txt, encoding="utf-8")
                        print(f"[-] Removed -onlinefix from {appid_str}")
                    else:
                        print(f"[*] No -onlinefix to remove for {appid_str}")
                    found = True
                    break
                else:
                    print(f"[*] No LaunchOptions for {appid_str} to remove")
                    found = True
                    break
        except Exception as e:
            print(f"[!] Failed {cfg}: {e}")
            continue
    if not found:
        if enable_onlinefix:
            print(f"[!] Could not find Apps section to add {appid_str}")
        else:
            print(f"[!] No LaunchOptions found for {appid_str}")
        return False
    return found

def generate_dlc_lua(dlc_appid: str | int, base_appid: str | int, steam_path: Path | None = None) -> bool:
    """Generate DLC lua via /api/dlc/generate?appid=&base="""
    if steam_path is None:
        steam_path = find_steam_path()
    tok = get_auth_token()
    headers = {"User-Agent":"Mozilla/5.0"}
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
        headers["apikey"] = SUPABASE_ANON_KEY
    url = f"{API_BASE}/api/dlc/generate?appid={dlc_appid}&base={base_appid}"
    try:
        r = SESSION.get(url, headers=headers, timeout=20)
        if r.status_code == 401:
            print("[!] DLC generate requires login (401). Run Delta login")
            return False
        r.raise_for_status()
        # response is a lua file binary
        data = r.content
        # save to stplug-in
        plug = st_plugin_dir(steam_path) if steam_path else None
        if not plug:
            print("[!] Steam not found")
            return False
        plug.mkdir(parents=True, exist_ok=True)
        dst = plug / f"{dlc_appid}.lua"
        dst.write_bytes(data)
        print(f"[+] DLC {dlc_appid} (base {base_appid}) -> {dst} ({len(data)}b)")
        # also check DlcInfo
        return True
    except Exception as e:
        print(f"[!] DLC generate failed: {e}")
        return False


def resolve_appid(inp: str) -> str | None:
    """Resolve appid from numeric or name search (like Delta Search) — for fixes/update/remove with name."""
    inp = inp.strip()
    if not inp:
        return None
    if inp.isdigit():
        return inp
    # search by name
    try:
        items = steam_search_store(inp)
        if not items:
            return inp  # fallback to original
        # if exact match, pick it, else first result
        for it in items:
            if it["name"].lower() == inp.lower():
                return str(it["id"])
        return str(items[0]["id"])
    except:
        return inp

def ensure_unlocker(steam_path: Path | None = None) -> bool:
    """Ensure BetterSteamTools unlocker is installed like Delta"""
    if steam_path is None:
        steam_path = find_steam_path()
    if not steam_path or not steam_path.exists():
        print("[!] Steam not found — cannot install unlocker")
        return False
    # Check if already installed (Bst files present)
    needed = ["dwmapi.dll", "xinput1_4.dll", "OpenSteamTool.dll"]
    # Also check for winmm.dll (old) — if present, still need Bst
    has_all = all((steam_path / f).exists() for f in needed)
    if has_all:
        # Verify OpenSteamTool.dll is not zero-byte and recent
        try:
            if (steam_path / "OpenSteamTool.dll").stat().st_size > 10000:
                return True
        except: pass
    print(f"{Fore.YELLOW}[*] Unlocker not found — installing BetterSteamTools (like Delta")
    # Try to fetch Bst manifest for latest version/hash
    manifest_url = "https://raw.githubusercontent.com/madoiscool/BetterSteamTools/refs/heads/updates/opensteamtool/latest.toml"
    zip_url = None
    version = "latest"
    try:
        r = SESSION.get(manifest_url, timeout=10)
        if r.ok:
            # TOML: version = "x.y.z" file = "OpenSteamTool.dll" sha256 = "..."
            import re as _re
            m = _re.search(r'version\s*=\s*"([^"]+)"', r.text)
            if m:
                version = m.group(1)
            # Try to get zip URL from manifest or fallback to releases
            # Fallback: use GitHub releases latest
            zip_url = f"https://github.com/madoiscool/BetterSteamTools/releases/download/{version}/OpenSteamTool-{version}-Release.zip"
            # If version is latest, try to get actual latest via API
            if version == "latest" or "latest" in version:
                # Try GitHub API for latest release
                try:
                    api = SESSION.get("https://api.github.com/repos/madoiscool/BetterSteamTools/releases/latest", timeout=8)
                    if api.ok:
                        j = api.json()
                        tag = j.get("tag_name", version)
                        zip_url = f"https://github.com/madoiscool/BetterSteamTools/releases/download/{tag}/OpenSteamTool-{tag}-Release.zip"
                        version = tag
                except: pass
    except Exception as e:
        print(f"[!] Could not fetch Bst manifest: {e}")
    if not zip_url:
        zip_url = "https://github.com/madoiscool/BetterSteamTools/releases/latest/download/OpenSteamTool-Release.zip"
        # Try via ghproxy for China/fresh PC without direct GitHub
        # Use proxy list like Delta
        for proxy in ["https://ghproxy.net/", "https://ghfast.top/", ""]:
            try:
                test_url = proxy + zip_url if proxy else zip_url
                # we will try download later
                break
            except: pass
    # Try download with proxies
    proxies = ["", "https://ghproxy.net/", "https://ghfast.top/", "https://gh.ddlc.top/"]
    data = None
    for proxy in proxies:
        try_url = proxy + zip_url if proxy else zip_url
        # Also try raw fallback: https://raw.githubusercontent.com/madoiscool/BetterSteamTools/main/...
        try:
            print(f"[*] Downloading Bst {version} from {try_url[:80]}...")
            r = SESSION.get(try_url, timeout=30)
            if r.ok and len(r.content) > 10000 and r.content[:2] == b'PK':
                data = r.content
                print(f"[+] Downloaded {len(data)//1024}KB")
                break
            else:
                print(f"  -> {r.status_code} not zip")
        except Exception as e:
            print(f"  -> failed {e}")
            continue
    if not data:
        print(f"{Fore.RED}[!] Failed to download Bst unlocker. Manual install: https://github.com/madoiscool/BetterSteamTools/releases{Style.RESET_ALL}")
        print(f"    Download OpenSteamTool-*-Release.zip and extract dwmapi.dll, xinput1_4.dll, OpenSteamTool.dll to {steam_path}")
        print(f"    Or run Delta as admin and try again, or install Delta ")
        return False
    # Need Steam closed (like Delta
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'steam' in proc.info['name'].lower():
                print(f"[!] Steam is running — closing for unlocker install (like Delta")
                try:
                    import os as _os, signal as _sig
                    # Try graceful close via taskkill
                    import subprocess as _sp
                    _sp.run(["taskkill", "/IM", "steam.exe", "/F"], capture_output=True, timeout=5)
                    import time as _time
                    _time.sleep(2)
                except: pass
                break
    except: pass
    # Also try via SteamService.IsSteamRunning equivalent: check via psutil or tasklist
    # Extract zip
    try:
        import zipfile, io as _io, tempfile as _tf
        z = zipfile.ZipFile(_io.BytesIO(data))
        # Find files to place (may be inside folder)
        for name in needed:
            # Find matching entry
            found = None
            for n in z.namelist():
                if n.lower().endswith(name.lower()):
                    found = n
                    break
            if not found:
                print(f"[!] {name} not in zip")
                continue
            out = steam_path / name
            # Backup existing if present
            if out.exists():
                try:
                    bak = out.with_suffix(out.suffix + ".bak")
                    if not bak.exists():
                        out.rename(bak)
                except: pass
            # Write new file (need admin for Program Files)
            try:
                out.write_bytes(z.read(found))
                print(f"[+] Installed {name} -> {out}")
            except PermissionError:
                print(f"{Fore.RED}[!] Permission denied writing {out} — run Delta as admin (right-click Run as administrator){Style.RESET_ALL}")
                return False
        print(f"{Fore.GREEN}[+] BetterSteamTools installed — restart Steam{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"[!] Unlocker install failed: {e}")
        return False

def set_stat(appid: str | int, steamid: str, steam_path=None):
    """setStat(appid, steamid) like Delta BetterSteamTools — spoofs achievements."""
    steam_path = find_steam_path() if steam_path is None else steam_path
    if not steam_path:
        print("[!] Steam not found")
        return False
    plug = st_plugin_dir(steam_path)
    plug.mkdir(parents=True, exist_ok=True)
    dst = plug / f"{appid}.lua"
    # Append setStat to lua (create if not exists)
    line = f'setStat({appid}, "{steamid}") -- Delta setStat override (default 76561198028121353)'
    if dst.exists():
        txt = dst.read_text(encoding='utf-8', errors='ignore')
        if "setStat" in txt:
            # replace existing setStat for this appid
            import re as _re
            new_txt, n = _re.subn(rf'setStat\s*\(\s*{appid}\s*,.*?\)', line, txt, flags=re.IGNORECASE)
            if n:
                dst.write_text(new_txt, encoding='utf-8')
                print(f"[+] Updated setStat for {appid} -> {steamid} in {dst}")
                return True
        # append
        with open(dst, "a", encoding='utf-8') as f:
            f.write("\n" + line + "\n")
    else:
        dst.write_text(f'addappid({appid})\n{line}\n', encoding='utf-8')
    print(f"[+] setStat {appid} {steamid} -> {dst}")
    return True

def set_cloud_redirect(enable: bool = True):
    """CloudRedirect like Delta Future — simple toggle via opensteamtool.toml [cloud] enable."""
    import pathlib as _pl
    steam_path = find_steam_path()
    if not steam_path:
        print("[!] Steam not found")
        return False
    toml = steam_path / "opensteamtool.toml"
    # Minimal: add [cloud] enable = true/false
    content = ""
    if toml.exists():
        content = toml.read_text(encoding='utf-8', errors='ignore')
    if enable:
        if "[cloud]" not in content:
            content += "\n[cloud]\nenable = true\n"
            # Also ensure CloudRedirect support note
            content += "# CloudRedirect via Delta — local saves (like Selectively11/CloudRedirect)\n"
        else:
            import re as _re
            content = _re.sub(r'\[cloud\].*?enable\s*=\s*\w+', '[cloud]\nenable = true', content, flags=re.S)
        toml.write_text(content, encoding='utf-8')
        print(f"[+] CloudRedirect enabled in {toml} — saves go local (like Delta Future)")
    else:
        if "[cloud]" in content:
            import re as _re
            content = _re.sub(r'\[cloud\].*?enable\s*=\s*true', '[cloud]\nenable = false', content, flags=re.S)
            toml.write_text(content, encoding='utf-8')
        print(f"[-] CloudRedirect disabled")
    print("    Note: Full CloudRedirect needs OST-Nightly + CloudRedirect.exe from Selectively11/CloudRedirect")
    return True

def list_installed_library(steam_path: Path | None = None) -> list[dict]:
    """List installed Delta luas — mirrors Delta Manage page (Delta.EnumerateInstalled)"""
    if steam_path is None:
        steam_path = find_steam_path()
    if not steam_path:
        return []
    plug = st_plugin_dir(steam_path)
    if not plug.exists():
        return []
    out=[]
    for p in plug.glob("*.lua"):
        try:
            appid = p.stem.split("_")[0]
            if not appid.isdigit():
                continue
            d = steam_details(appid)
            name = d["name"] if d else f"App {appid}"
            # parse lua for HasKey / pinned
            txt = p.read_text(errors="ignore")
            has_key = "DecryptionKey" in txt or re.search(r'addappid\s*\(\s*\d+\s*,\s*\d+\s*,\s*"[^"]+"', txt)
            manifests = len(re.findall(r'setManifestid', txt, re.I))
            out.append({"appid": appid, "name": name, "path": str(p), "size": p.stat().st_size, "has_key": bool(has_key), "manifests": manifests})
        except: continue
    return sorted(out, key=lambda x: x["name"].lower())

# ---------- Add game (create lua) — Delta-accurate ----------
def fetch_steamcmd_info(appid: str | int) -> dict | None:
    """Fetch depots + DLCs via api.steamcmd.net (public, no auth). Used to build Delta-style lua. Cached 14d."""
    try:
        # Check cache
        cache = _load_cache()
        key = f"steamcmd_{appid}"
        if key in cache:
            return cache[key]
    except: pass
    try:
        r = SESSION.get(f"https://api.steamcmd.net/v1/info/{appid}", timeout=10)
        if not r.ok:
            return None
        j = r.json()
        if "data" not in j or str(appid) not in j["data"]:
            return None
        res = j["data"][str(appid)]
        try:
            c = _load_cache()
            c[f"steamcmd_{appid}"] = res
            _save_cache(c)
        except: pass
        return res
    except Exception:
        return None

def fetch_dlc_appids(appid: str | int) -> list[int]:
    """Get DLC appids via Store appdetails (public)."""
    try:
        r = requests.get("https://store.steampowered.com/api/appdetails", params={"appids": appid}, timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        if r.ok:
            j = r.json()
            d = j.get(str(appid), {})
            if d.get("success"):
                return d["data"].get("dlc", []) or []
    except Exception:
        pass
    return []

# ---------- Depot key handling (fixes "content still encrypted") ----------
def get_depot_keys_from_config_vdf(steam_path: Path | None) -> dict[str, str]:
    """Extract depot decryption keys from Steam/config/config.vdf (cached after license)."""
    if not steam_path:
        steam_path = find_steam_path()
    if not steam_path:
        return {}
    vdf = steam_path / "config" / "config.vdf"
    if not vdf.exists():
        return {}
    try:
        txt = vdf.read_text(encoding="utf-8", errors="ignore")
        # pattern: "123456" { "DecryptionKey" "hex64" }
        keys = {}
        for m in re.finditer(r'"(\d+)"\s*\{\s*"DecryptionKey"\s*"([0-9a-fA-F]{64})"', txt, re.DOTALL):
            keys[m.group(1)] = m.group(2).lower()
        # also flat
        for m in re.finditer(r'"(\d+)"\s*\{\s*"DecryptionKey"\s*"([0-9a-fA-F]+)"', txt):
            if len(m.group(2)) == 64:
                keys[m.group(1)] = m.group(2).lower()
        return keys
    except Exception:
        return {}

def try_fetch_key_from_public_sources(depot_id: str) -> str | None:
    """Try public key servers (best-effort). Returns 64hex or None."""
    headers = {"User-Agent":"Mozilla/5.0"}
    candidates = [
        f"https://raw.githubusercontent.com/okaydrku/Delta/main/keys/{depot_id}.txt",
        f"https://raw.githubusercontent.com/eudaimence/OpenDepot/main/{depot_id}.txt",
    ]
    for url in candidates:
        try:
            r = requests.get(url, timeout=4, headers=headers)
            if r.ok and len(r.text.strip()) == 64 and re.match(r"^[0-9a-fA-F]{64}$", r.text.strip()):
                return r.text.strip().lower()
        except Exception:
            continue
    return None

def install_from_manifest_backend(appid: str | int, steam_path: Path | None = None) -> bool:
    """Try Delta manifest backend (http://167.235.229.108/<appid>) — same as Delta app.
    Returns True if zip was downloaded and installed to stplug-in + depotcache (fixes 'content still encrypted')."""
    if steam_path is None:
        steam_path = find_steam_path()
    if not steam_path:
        return False
    # check availability first (fast)
    try:
        chk = requests.get(f"{base64.b64decode("aHR0cDovLzE2Ny4yMzUuMjI5LjEwOA==").decode()}/check_apis?appid={appid}", headers={"User-Agent":"secretgoonpoon"}, timeout=5)
        if chk.ok:
            avail = chk.json()
            # if all unavailable, skip download
            if avail and all(v == "unavailable" for v in avail.values()):
                return False
    except Exception:
        pass
    try:
        r = requests.get(f"{base64.b64decode("aHR0cDovLzE2Ny4yMzUuMjI5LjEwOA==").decode()}/{appid}", headers={"User-Agent":"secretgoonpoon"}, timeout=20)
        if not r.ok or len(r.content) < 100:
            return False
        # validate zip
        bio = io.BytesIO(r.content)
        if not zipfile.is_zipfile(bio):
            return False
        bio.seek(0)
        z = zipfile.ZipFile(bio)
        # install lua to stplug-in (overwrites)
        plug = st_plugin_dir(steam_path)
        plug.mkdir(parents=True, exist_ok=True)
        # depotcache is Steam/depotcache (not config/depotcache) — verified from Delta
        # Delta 
        depotcache = steam_path / "config" / "depotcache"
        depotcache.mkdir(parents=True, exist_ok=True)
        # also ensure Steam/depotcache exists for Steam's own cache (some builds read there)
        alt_cache = steam_path / "depotcache"
        alt_cache.mkdir(parents=True, exist_ok=True)
        installed_lua = False
        installed_manifests = 0
        for name in z.namelist():
            data = z.read(name)
            if name.lower().endswith(".lua"):
                dst = plug / f"{appid}.lua"
                if dst.exists():
                    bak = dst.with_suffix(".lua.bak")
                    try:
                        shutil.copy2(dst, bak)
                    except: pass
                dst.write_bytes(data)
                installed_lua = True
            elif name.lower().endswith(".manifest"):
                dst = depotcache / Path(name).name
                dst.write_bytes(data)
                # also copy to alt cache for compatibility
                try:
                    (alt_cache / Path(name).name).write_bytes(data)
                except: pass
                installed_manifests += 1
            elif name.lower().endswith(".vdf") or name.lower().endswith(".json"):
                # optional, keep for debugging but not needed for Steam
                pass
        if installed_lua:
            # Like LuaTools AutoUpdate: comment setManifestid unless forceLocked/buildId
            try:
                _lua_path = plug / f"{appid}.lua"
                if _lua_path.exists():
                    _txt = _lua_path.read_text(encoding="utf-8", errors="ignore")
                    # Check if this is a build variant (like <appid>_<buildid>.lua) — keep pins
                    _is_build = False
                    # For Delta, backend lua is plain <appid>.lua, so treat as AutoUpdate on -> comment pins
                    # Read setting: for now, AutoUpdate = True (like LuaTools default)
                    _auto = True
                    if _auto and not _is_build:
                        # Comment out setManifestid lines (like LuaInstaller.CommentOutManifestPins)
                        import re as _re2
                        _txt2 = _re.sub(r'^(\s*)(setManifestid\s*\()', r'\1-- \2', _txt, flags=re.MULTILINE|re.IGNORECASE)
                        if _txt2 != _txt:
                            _lua_path.write_text(_txt2, encoding="utf-8")
            except: pass
            print(f"[+] Manifest backend: installed lua + {installed_manifests} manifest(s) for {appid} to {plug} / {depotcache} (AutoUpdate: unpinned, Steam follows latest)")
            # Vault capture for backend installs
            try:
                _data = (plug / f"{appid}.lua").read_bytes()
                _build2 = None
                try:
                    _sd2 = fetch_steamcmd_info(appid)
                    if _sd2 and "depots" in _sd2:
                        _build2 = _sd2["depots"].get("branches",{}).get("public",{}).get("buildid")
                except: pass
                vault_capture(appid, _data, _build2)
            except: pass
            return True
    except Exception as e:
        print(f"[!] Manifest backend failed for {appid}: {e}")
    return False

def build_delta_lua(appid: str | int, name: str, steamcmd_data: dict | None, dlc_ids: list[int] | None, depot_key: str | None = None, manifest_gid: str | None = None, depot_id: str | None = None, steam_path: Path | None = None) -> str:
    """Build Delta-accurate lua like / — avoids 0B by emitting depots + DLCs. Handles decryption keys."""
    import datetime
    appid = str(appid)
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    # try to get cached keys
    cached_keys = get_depot_keys_from_config_vdf(steam_path)
    lines = []
    lines.append(f"-- Generated by Delta/ (by Delta)")
    lines.append(f"-- {appid} - {name}")
    lines.append(f"-- Generated {now}")
    buildid = None
    if steamcmd_data and "depots" in steamcmd_data:
        buildid = steamcmd_data["depots"].get("branches", {}).get("public", {}).get("buildid")
        if buildid:
            lines.append(f"-- BuildID {buildid} via api.steamcmd.net")
    lines.append("")
    lines.append("-- Main AppID")
    if depot_key and manifest_gid:
        dep = depot_id or appid
        # explicit key for main depot
        lines.append(f"addappid({dep}, 1, \"{depot_key}\")")
        lines.append(f"setManifestid({dep}, \"{manifest_gid}\")")
        if dep != appid:
            lines.append(f"addappid({appid})")
    else:
        lines.append(f"addappid({appid})")
    lines.append("")

    # Main depots from steamcmd
    if steamcmd_data and "depots" in steamcmd_data:
        depots = steamcmd_data["depots"]
        main_depots = []
        for k, v in depots.items():
            if k.isdigit() and isinstance(v, dict) and "manifests" in v:
                gid = v["manifests"].get("public", {}).get("gid")
                size = v["manifests"].get("public", {}).get("size")
                dlcappid = v.get("dlcappid")
                if dlcappid:
                    continue
                main_depots.append((k, gid, size))
        if main_depots:
            lines.append("-- Main Depots (from api.steamcmd.net)")
            for dep, gid, size in main_depots:
                # skip if already emitted as explicit --depot-key target (duplicate)
                if depot_key and depot_id == dep:
                    continue
                key = None
                if dep in cached_keys:
                    key = cached_keys[dep]
                else:
                    key = try_fetch_key_from_public_sources(dep)
                if key:
                    lines.append(f"addappid({dep}, 1, \"{key}\")")
                    if gid:
                        lines.append(f"setManifestid({dep}, \"{gid}\", {size})")
                else:
                    lines.append(f"addappid({dep})")
                    if gid:
                        lines.append(f"-- setManifestid({dep}, \"{gid}\", {size})")
            lines.append("-- Uncomment setManifestid if download shows 0B or wrong build")
            lines.append("-- If 'content still encrypted' -> add key: addappid(depot, 1, \"64hex\") or --depot-key")
            lines.append("")

    # DLCs
    if dlc_ids:
        lines.append("-- DLCs (unlock only, no key needed for most)")
        for dlc in dlc_ids[:30]:
            d = steam_details(dlc)
            dlc_name = d["name"] if d else f"DLC {dlc}"
            dlc_gid = None
            dlc_size = None
            if steamcmd_data:
                for k, v in steamcmd_data.get("depots", {}).items():
                    if isinstance(v, dict) and str(v.get("dlcappid")) == str(dlc):
                        m = v.get("manifests", {}).get("public", {})
                        dlc_gid = m.get("gid")
                        dlc_size = m.get("size")
                        break
            lines.append(f"addappid({dlc}) -- {dlc_name}")
            if dlc_gid:
                lines.append(f"-- setManifestid({dlc}, \"{dlc_gid}\", {dlc_size})")
        lines.append("")

    lines.append("-- Shared Depots (Runtimes) — keys are public")
    lines.append("addappid(228988, 1, \"1845444d5e2cfd0ae65ae4a8fedb6e2fbf776fcc5b913ab4ac461bc9a74f8358\") -- VC2019 windows")
    lines.append("addappid(228990, 1, \"44d8c45ce229a11c4f231a3d2a350eaf80b0d69a8af938ec7ccca720f694b0e8\") -- VC2019 windows")
    lines.append("")
    lines.append("-- Notes: Delta auto-fetches manifests via delta backend if setManifestid is commented.")
    lines.append("-- If 'content still encrypted', add DecryptionKey: addappid(depot, 1, \"key\") — get from Delta App or --depot-key")
    lines.append("-- OnlineFix: add -onlinefix to Steam -> Right-click game -> Properties -> General -> Launch Options")
    return "\n".join(lines) + "\n"

LUA_TEMPLATE_SIMPLE = """-- Generated by Delta.py (Delta)
-- App: {name} ({appid})
-- Place this file in Steam/config/stplug-in/ and restart Steam (or wait for hot-reload)
addappid({appid})
"""

LUA_TEMPLATE_FULL = """-- Generated by Delta.py
-- App: {name} ({appid}) Depot {depot} Manifest {manifest}
addappid({depot}, 0, "{key}")
setManifestid({depot}, "{manifest}"{size_suffix})
addappid({appid})
"""

def add_game_to_steam(appid: str | int, name: str | None = None, steam_path: Path | None = None,
                       depot_key: str | None = None, manifest_gid: str | None = None, depot_id: str | None = None,
                       stub: bool = False) -> Path:
    """Create <appid>.lua in stplug-in. By default builds Delta-accurate lua (avoids 0B). Use stub=True for minimal addappid."""
    appid = str(appid)
    if not name:
        d = steam_details(appid)
        name = d["name"] if d and d.get("name") else f"App {appid}"
    if steam_path is None:
        steam_path = find_steam_path()
        if not steam_path:
            raise FileNotFoundError("Steam not found. Pass --steam-path or set STEAM_PATH.")

    # Ensure unlocker installed (fixes fresh PC missing license / not appearing) like Delta
    try:
        ensure_unlocker(steam_path)
    except Exception as e:
        print(f"[!] Unlocker check failed: {e} — continuing (game may not appear without dwmapi.dll)")

    plug = st_plugin_dir(steam_path)
    plug.mkdir(parents=True, exist_ok=True)

    # Decide content: stub vs backend vs Delta
    if stub:
        content = LUA_TEMPLATE_SIMPLE.format(name=name, appid=appid)
    elif depot_key and manifest_gid:
        # explicit key -> still use Delta with injected key (avoids stub)
        steamcmd_data = fetch_steamcmd_info(appid)
        dlc_ids = fetch_dlc_appids(appid)
        content = build_delta_lua(appid, name, steamcmd_data, dlc_ids, depot_key, manifest_gid, depot_id, steam_path)
    else:
        # Try manifest backend first (same as Delta app) — fixes "content still encrypted" with real keys
        if install_from_manifest_backend(appid, steam_path):
            # backend installed lua+manifest, no need to generate
            # need to also ensure name is correct for logging
            dst = st_plugin_dir(steam_path) / f"{appid}.lua"
            print(f"[+] Added {name} ({appid}) -> {dst} (via manifest backend, with decryption keys)")
            print(f"    -> Restart Steam (or wait ~5s for hot-reload). Game appears in Library -> trigger download.")
            # verify manifests
            depotcache = steam_path / "depotcache"
            manifests = list(depotcache.glob(f"{appid}*.manifest")) + list(depotcache.glob("*_*.manifest"))
            # just return
            return dst
        # fallback to Delta-accurate generation
        steamcmd_data = fetch_steamcmd_info(appid)
        dlc_ids = fetch_dlc_appids(appid)
        content = build_delta_lua(appid, name, steamcmd_data, dlc_ids, depot_key, manifest_gid, depot_id, steam_path)

    dst = plug / f"{appid}.lua"
    if dst.exists():
        bak = dst.with_suffix(".lua.bak")
        shutil.copy2(dst, bak)
        print(f"[*] Existing {dst.name} backed up -> {bak.name}")

    dst.write_text(content, encoding="utf-8")
    # Vault capture (like Delta) — keep build history
    try:
        # try to get buildid from steamcmd
        _build = None
        try:
            _sd = fetch_steamcmd_info(appid)
            if _sd and "depots" in _sd:
                _build = _sd["depots"].get("branches",{}).get("public",{}).get("buildid")
        except: pass
        vault_capture(appid, content.encode('utf-8'), _build)
    except: pass
    print(f"[+] Added {name} ({appid}) -> {dst} ({len(content)}b, {content.count(chr(10))+1} lines)")
    print(f"    -> Restart Steam (or wait ~5s for hot-reload). Game appears in Library -> trigger download.")
    if stub:
        print("    NOTE: stub mode — may show 0B if depot encrypted. Re-run without --stub for full lua.")
    else:
        print("    Delta-style lua with depots+DLCs — if 0B uncomment setManifestid lines or use --depot-key/--manifest-gid")
    return dst

# ---------- Online Fix ----------
def apply_online_fix(appid: str | int, fix_url: str | None = None, fix_zip_path: str | None = None,
                     steam_path: Path | None = None, game_dir: str | None = None):
    appid = str(appid)
    if steam_path is None:
        steam_path = find_steam_path()

    # Resolve install dir
    target_dir: Path | None = None
    if game_dir:
        target_dir = Path(game_dir)
        # explicit override -> use as-is (will be created)
    elif steam_path:
        target_dir = game_install_dir(steam_path, appid)
        if target_dir and not target_dir.exists():
            print(f"[!] Detected install dir does not exist yet: {target_dir}")
            print(f"    Install the game first via Steam (it will be in Library after add).")
            # ask to pick manual path
            target_dir = None

    if not target_dir or (not target_dir.exists() and not game_dir):
        print("[?] Game folder not found automatically.")
        if steam_path:
            print(f"    Hint: check {steam_path/'steamapps'/'common'}")
        manual = input("Enter full path to game folder (or leave empty to just download fix): ").strip().strip('"')
        if manual:
            target_dir = Path(manual)
        else:
            target_dir = Path.cwd() / f"fix_{appid}_extracted"

    # Acquire ZIP
    zip_bytes: bytes | None = None
    zip_src = fix_zip_path or fix_url
    if not zip_src:
        # Offer to browse  fixes
        print(f"[?] No fix URL provided for {appid}. Opening /fixes/{appid}")
        try:
            webbrowser.open(f"{base64.b64decode("aHR0cHM6Ly9sdWEudG9vbHM=").decode()}/fixes/{appid}")
        except: pass
        zip_src = input("Paste direct ZIP URL (or local .zip path): ").strip().strip('"')
        if not zip_src:
            print("Aborted.")
            return

    if Path(zip_src).exists():
        print(f"[*] Using local ZIP: {zip_src}")
        zip_bytes = Path(zip_src).read_bytes()
    else:
        # treat as URL
        print(f"[*] Downloading fix from {zip_src} ...")
        r = requests.get(zip_src, timeout=60, headers={"User-Agent":"Mozilla/5.0"}, stream=True)
        r.raise_for_status()
        zip_bytes = r.content
        print(f"    -> {len(zip_bytes)/1024/1024:.2f} MB")

    # Backup + extract (like Delta.ApplyFix — per-file best-effort)
    target_dir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            members = [m for m in z.namelist() if not m.endswith("/")]
            print(f"[*] ZIP contains {len(members)} files -> extracting to {target_dir}")
            for m in members[:15]:
                print(f"    - {m}")
            if len(members)>15:
                print(f"    ... and {len(members)-15} more")
            failed = 0
            for member in members:
                dest = target_dir / member
                # backup
                if dest.exists():
                    try:
                        bak = dest.with_suffix(dest.suffix + ".bak")
                        if not bak.exists():
                            shutil.copy2(dest, bak)
                    except: pass
                try:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(member) as src, open(dest, "wb") as out:
                        shutil.copyfileobj(src, out)
                except PermissionError:
                    failed += 1
                    print(f"    [!] Locked (close game/Steam): {member}")
                except Exception as e:
                    failed += 1
                    print(f"    [!] Failed {member}: {e}")
            if failed:
                print(f"[!] {failed} file(s) locked — close game/Steam and retry, or run as admin")
                print(f"[+] Partially applied to {target_dir} ({len(members)-failed}/{len(members)})")
            else:
                print(f"[+] OnlineFix applied to {target_dir}")
            print(f"    Launch the game from Steam. If lobby fix: add '-onlinefix' to Launch Options (right-click -> Properties).")
            print(f"    Some fixes use Goldberg/EOS - read included Readme.txt if present.")
    except zipfile.BadZipFile:
        try:
            out = target_dir / Path(zip_src).name
            out.write_bytes(zip_bytes)
            print(f"[+] Saved single file -> {out}")
        except PermissionError:
            print(f"[!] Permission denied: close game/Steam or run as admin")
        except Exception as e:
            print(f"[!] Save failed: {e}")

# ---------- CLI ----------
def cmd_login(args):
    banner()
    tok = do_pkce_login()
    if tok:
        print(f"{Fore.GREEN}Logged in! Try Delta fixes now.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Login failed. You can also paste token manually:{Style.RESET_ALL}")
        print("Delta will prompt for token on fixes download, or set DELTA_TOKEN env")

def cmd_logout(args):
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
        print(f"{Fore.GREEN}Logged out — token removed{Style.RESET_ALL}")
    else:
        print("Not logged in")

def cmd_status(args):
    banner()
    steam_path = find_steam_path()
    print(f"{Fore.CYAN}Steam:{Style.RESET_ALL} {steam_path or 'not found'}")
    print(f"{Fore.CYAN}Plugin:{Style.RESET_ALL} {st_plugin_dir(steam_path) if steam_path else 'n/a'}")
    print(f"{Fore.CYAN}Library:{Style.RESET_ALL} {len(list_installed_library(steam_path))} games" if steam_path else "Library: n/a")
    tok = get_auth_token()
    if tok:
        # try to validate via supporter-status
        try:
            r = SESSION.get(f"{API_BASE}/api/me/supporter-status", headers=auth_headers(tok), timeout=8)
            if r.ok:
                print(f"{Fore.GREEN}Login: OK (supporter check passed){Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Login: token present but check failed {r.status_code}{Style.RESET_ALL}")
        except Exception as e:
            print(f"Login: token present ({e})")
    else:
        print(f"{Fore.YELLOW}Login: not logged in (fixes need login, 25/day){Style.RESET_ALL}")
        print(f"  Run {Fore.CYAN}Delta login{Style.RESET_ALL} for Discord OAuth")

def cmd_unlocker(args):
    steam_path = pathlib.Path(args.steam_path) if getattr(args, "steam_path", None) else find_steam_path()
    if not steam_path:
        print("[!] Steam not found")
        return
    ok = ensure_unlocker(steam_path)
    if ok:
        print("[+] Unlocker ready — games will appear")
    else:
        print("[!] Unlocker not installed — run as admin or install Delta ")

def cmd_search(args):
    items = steam_search_store(args.term, cc=args.cc)
    if not items:
        print("No results from Store API, trying  details as fallback for numeric AppID...")
        if args.term.isdigit():
            d = steam_details(args.term)
            if d:
                print(f"  {d['appid']:>8} | {d['name']} | {d.get('type')}")
                return
        print("  (no results)")
        return
    print(f"{Fore.CYAN}Found {len(items)} results for '{Fore.WHITE}{args.term}{Fore.CYAN}':{Style.RESET_ALL}")
    # pretty table
    hdr = f"{Fore.YELLOW}{'AppID':>8} | {'Name':<45} | {'Price':<8} | Score{Style.RESET_ALL}"
    print(hdr)
    print(f"{Style.DIM}{'-'*80}{Style.RESET_ALL}")
    for it in items[: args.limit]:
        price = it.get("price", {})
        final = price.get("final", 0)/100 if price else 0
        name = it['name'][:44]
        col = Fore.GREEN if it.get('metascore') else Fore.WHITE
        print(f"  {Fore.CYAN}{it['id']:>8}{Style.RESET_ALL} | {col}{name:<45}{Style.RESET_ALL} | {Fore.GREEN}${final:.2f}{Style.RESET_ALL} | {it.get('metascore','')}")

def cmd_add(args):
    steam_path = Path(args.steam_path) if args.steam_path else find_steam_path()
    if not steam_path:
        print("[!] Steam not found. Use --steam-path C:\\Program Files (x86)\\Steam")
        sys.exit(2)
    print(f"[*] Steam: {steam_path}")
    plug = st_plugin_dir(steam_path)
    print(f"[*] Plugin dir: {plug} ({'exists' if plug.exists() else 'will be created'})")
    dst = add_game_to_steam(args.appid, name=args.name, steam_path=steam_path,
                            depot_key=args.depot_key, manifest_gid=args.manifest_gid, depot_id=args.depot_id,
                            stub=getattr(args, "stub", False))
    if args.fix_url or args.fix_zip:
        print("\n[*] Also applying OnlineFix ...")
        apply_online_fix(args.appid, fix_url=args.fix_url, fix_zip_path=args.fix_zip, steam_path=steam_path)

def cmd_fix(args):
    # resolve name to appid if needed
    args.appid = resolve_appid(str(args.appid))
    steam_path = Path(args.steam_path) if args.steam_path else find_steam_path()
    # auto mode: if no url/zip given, try to fetch fixes like Delta Fixes page
    if not args.fix_url and not args.fix_zip:
        fixes = get_denuvo_fixes(args.appid)
        if fixes:
            print(f"[+] Found {len(fixes)} fix(es) for {args.appid}:")
            for i, f in enumerate(fixes, 1):
                title = html.unescape(f.get("Title") or f.get("title") or f.get("Id") or "")
                if not IS_UTF:
                    title = title.encode("ascii", errors="replace").decode() or "Fix"
                print(f'  [{i}] {title}  HasManifest={f.get("hasManifest", f.get("HasManifest"))} HasFix={f.get("hasFix", f.get("HasFix"))}')
            sel = input("Pick fix # to auto-download (or Enter for manual URL): ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(fixes):
                fix = fixes[int(sel)-1]
                slot = "fix" if fix.get("hasFix", fix.get("HasFix")) else "manifest"
                fix_id = fix.get("Id") or fix.get("id")
                print(f"[*] Trying auto-download fix {fix_id} slot {slot} (requires login, like Delta)...")
                try:
                    url = get_fix_signed_url(fix_id, slot)
                    if not url:
                        print("[!] Login required or download failed. Opening browser...")
                        webbrowser.open(f"{base64.b64decode("aHR0cHM6Ly9sdWEudG9vbHM=").decode()}/fixes/{args.appid}")
                        return
                    print(f"[*] Got signed URL -> downloading")
                    return apply_online_fix(args.appid, fix_url=url, steam_path=steam_path, game_dir=args.game_dir)
                except Exception as e:
                    print(f"[!] Auto-download error: {e}")
        print("[*] Falling back to manual fix URL...")
    apply_online_fix(args.appid, fix_url=args.fix_url, fix_zip_path=args.fix_zip, steam_path=steam_path, game_dir=args.game_dir)

def cmd_library(args):
    steam_path = Path(args.steam_path) if args.steam_path else find_steam_path()
    libs = list_installed_library(steam_path)
    if not libs:
        print("No Delta luas found. Use `Delta add <appid>`")
        return
    print(f"{Fore.CYAN}Installed Delta library ({len(libs)}) — {Fore.GREEN}Delta Manage{Style.RESET_ALL}:")
    print(f"{Style.DIM}{'AppID':>8} | {'Name':<35} | Size | Key | Manifests{Style.RESET_ALL}")
    for it in libs:
        tag = f"{Fore.GREEN}key{Style.RESET_ALL}" if it["has_key"] else f"{Fore.RED}no-key{Style.RESET_ALL}"
        print(f"  {Fore.CYAN}{it['appid']:>8}{Style.RESET_ALL} | {it['name'][:34]:<35} | {it['size']}b | {tag} | {it['manifests']}")

def cmd_info(args):
    d = steam_details(args.appid)
    if d:
        print(f"{d['appid']} — {d['name']} [{d.get('type')}]")
    sd = fetch_steamcmd_info(args.appid)
    if sd:
        depots = sd.get("depots", {})
        print(f"BuildID {depots.get('branches',{}).get('public',{}).get('buildid')} | depots: {len([k for k in depots if k.isdigit()])}")
        for k, v in depots.items():
            if k.isdigit() and isinstance(v, dict) and "manifests" in v:
                gid = v["manifests"].get("public",{}).get("gid")
                size = v["manifests"].get("public",{}).get("size")
                print(f"  depot {k} -> {gid} {size}")
    else:
        print("No steamcmd info")

def cmd_remove(args):
    args.appid = resolve_appid(str(args.appid))
    steam_path = Path(args.steam_path) if args.steam_path else find_steam_path()
    plug = st_plugin_dir(steam_path) if steam_path else None
    if not plug:
        print("Steam not found")
        return
    dst = plug / f"{args.appid}.lua"
    if dst.exists():
        dst.unlink()
        print(f"[-] Removed {dst}")
        # also manifests? keep
    else:
        print(f"Not installed: {dst}")

def cmd_launch(args):
    ok = set_launch_options(args.appid, enable_onlinefix=not args.remove)
    if ok:
        print(f"{'Removed' if args.remove else 'Added'} -onlinefix for {args.appid} — restart Steam to apply (like Delta)")
    else:
        print(f"[!] Failed to set launch option for {args.appid} — is Steam installed? Is localconfig.vdf present?")

def cmd_dlc(args):
    ok = generate_dlc_lua(args.appid, args.base)
    if ok:
        print(f"[+] DLC unlock ready — restart Steam")

def cmd_setstat(args):
    set_stat(args.appid, args.steamid)

def cmd_cloud(args):
    if args.enable:
        set_cloud_redirect(True)
    elif args.disable:
        set_cloud_redirect(False)
    else:
        # toggle show status
        p = find_steam_path()
        toml = p / "opensteamtool.toml" if p else None
        print(f"CloudRedirect: {'enabled' if toml and 'enable = true' in toml.read_text(errors='ignore') else 'disabled'} (Delta Future)")

def cmd_fixes(args):
    if args.appid:
        args.appid = resolve_appid(str(args.appid))
        fixes = get_denuvo_fixes(args.appid)
        if not fixes:
            print(f"No fixes for {args.appid} (or API unavailable). Opening browser...")
            webbrowser.open(f"{base64.b64decode("aHR0cHM6Ly9sdWEudG9vbHM=").decode()}/fixes/{args.appid}")
            return
        print(f"Fixes for {args.appid}:")
        for i, f in enumerate(fixes, 1):
            title = html.unescape(f.get("Title") or f.get("title") or f.get("Id") or "")
            if not IS_UTF:
                title = title.encode("ascii", errors="replace").decode()
            print(f'  [{i}] {title} | HasManifest={f.get("hasManifest", f.get("HasManifest"))} HasFix={f.get("hasFix", f.get("HasFix"))}')
        sel = input("Download # (or Enter to skip): ").strip()
        if sel.isdigit() and 1 <= int(sel) <= len(fixes):
            fix = fixes[int(sel)-1]
            slot = "fix" if fix.get("hasFix", fix.get("HasFix")) else "manifest"
            fix_id = fix.get("Id") or fix.get("id")
            steam_path = Path(args.steam_path) if args.steam_path else find_steam_path()
            print(f"[*] Downloading {fix_id} slot {slot}...")
            try:
                url = get_fix_signed_url(fix_id, slot)
                if not url:
                    print("[!] Login required. Opening browser...")
                    webbrowser.open(f"{base64.b64decode("aHR0cHM6Ly9sdWEudG9vbHM=").decode()}/fixes/{args.appid}")
                    return
                if url:
                    steam_path = Path(args.steam_path) if args.steam_path else find_steam_path()
                    if slot == "manifest":
                        # install lua force-locked like Delta.InstallManifest
                        import tempfile
                        tmp = Path(tempfile.gettempdir()) / f"delta_fix_{fix_id}.zip"
                        tmp.write_bytes(requests.get(url, headers={"User-Agent":"Mozilla/5.0"}).content)
                        # use installer logic: unzip to stplug-in forceLocked
                        print(f"[+] Manifest fix downloaded to {tmp} — installing (forceLocked)")
                        with zipfile.ZipFile(tmp) as z:
                            for name in z.namelist():
                                if name.lower().endswith(".lua"):
                                    plug = st_plugin_dir(steam_path) if steam_path else None
                                    if plug:
                                        plug.mkdir(parents=True, exist_ok=True)
                                        dst = plug / f"{args.appid}.lua"
                                        dst.write_bytes(z.read(name))
                                        print(f"[+] Installed manifest lua -> {dst}")
                        return
                    else:
                        return apply_online_fix(args.appid, fix_url=url, steam_path=steam_path)
            except Exception as e:
                print(f"[!] {e}")
                webbrowser.open(f"{base64.b64decode("aHR0cHM6Ly9sdWEudG9vbHM=").decode()}/fixes/{args.appid}")
        return
    # no appid -> list games
    idx = delta_fixes_index()
    for it in idx[:40]:
        print(f"  {it['appid']:>8} | {it['name']}")
    print(f"Showing {min(40,len(idx))}/{len(idx)} — use `Delta fixes <appid>` for details")

def auto_update_all(sp=None):
    """On Delta start, update all installed games if newer manifest available — parallel like Delta (fast)."""
    if sp is None:
        sp = find_steam_path()
    if not sp:
        return
    libs = list_installed_library(sp)
    if not libs:
        return
    # Skip if cache fresh (<1h) to avoid slow 47 checks every launch
    try:
        import time as _ti
        last = 0
        try:
            last = float(_load_cache().get("_last_auto_update", 0))
        except: pass
        if _ti.time() - last < 3600:
            return
    except: pass
    console.print(f"  Checking {len(libs)} installed for updates (parallel)...", style="rgb(120,120,120)")
    import concurrent.futures as _cf, re as _re
    def check_one(it):
        appid = it["appid"]
        try:
            cur = None
            try:
                cur_txt = (st_plugin_dir(sp) / f"{appid}.lua").read_text(encoding="utf-8", errors="ignore")
                m = _re.search(r'setManifestid\s*\(\s*\d+\s*,\s*"(\d+)"', cur_txt)
                if m:
                    cur = m.group(1)
            except: pass
            sd = fetch_steamcmd_info(appid)
            latest = None
            if sd and "depots" in sd:
                for k,v in sd["depots"].items():
                    if k.isdigit() and isinstance(v, dict) and "manifests" in v and not v.get("dlcappid"):
                        latest = v["manifests"].get("public",{}).get("gid")
                        if latest:
                            break
            if latest and cur and latest != cur:
                return (appid, it["name"], cur, latest)
        except: pass
        return None
    to_update = []
    try:
        with _cf.ThreadPoolExecutor(max_workers=12) as ex:
            futs = {ex.submit(check_one, it): it for it in libs}
            for fut in _cf.as_completed(futs):
                r = fut.result()
                if r:
                    to_update.append(r)
    except:
        # Fallback sequential if threads fail
        for it in libs:
            r = check_one(it)
            if r:
                to_update.append(r)
    # Save last check time
    try:
        c = _load_cache()
        c["_last_auto_update"] = time.time()
        _save_cache(c)
    except: pass
    if not to_update:
        console.print(f"  No updates needed", style="rgb(100,100,100)")
        return
    console.print(f"  Found {len(to_update)} update(s) — applying...", style="yellow")
    updated = 0
    for appid, name, cur, latest in to_update:
        try:
            console.print(f"  Updating {appid} {name} {cur[:8]}.. -> {latest[:8]}..", style="yellow")
            if install_from_manifest_backend(appid, sp):
                console.print(f"  [✓] Updated {appid}", style="green")
                updated += 1
            else:
                add_game_to_steam(appid, name=name, steam_path=sp)
                updated += 1
        except Exception as e:
            print(f"  [!] Update {appid} failed: {e}")
    if updated:
        console.print(f"  [✓] Auto-updated {updated} game(s) — restart Steam", style="green")

def cmd_interactive(args):
    # OGS-STYLE TERMINAL — keep how test.py looks
    sp = find_steam_path()
    # Auto unlocker on double-click (like LuaTools UnlockerService)
    try:
        if sp:
            ensure_unlocker(sp)
    except: pass
    while True:
        if os.name == "nt":
            os.system("title DELTA")
        console.clear()
        # DELTA LOGO
        logo = make_logo()
        for line in logo:
            console.print(Align.center(line))
        console.print()
        print_header()
        menu_header()
        # Keep visual exactly as test.py — but titles mapped to Delta functions (random -> real)
        option(1, "Search", "Search games on Steam")
        option(2, "Add Game", "Add game to Steam via backend")
        option(3, "Library", "View installed Delta library")
        option(4, "Fixes", "Browse & auto-apply fixes")
        option(5, "Status", "Login / logout / system status")
        option(6, "Remove", "Remove Delta lua from Steam")
        option(7, "Update", "Update game to latest manifest")
        option(8, "About", "Credits, version & special thanks")
        # prompt (OGS style)
        choice = prompt()
        choice = choice.strip()
        if choice == "1":
            console.clear()
            selp = Text()
            selp.append("Select option ", style="white")
            selp.append("›", style=f"{PINK} bold")
            selp.append(" 1", style="white")
            console.print(selp)
            console.print()
            detail_header("SEARCH")
            # styled input
            pr = Text()
            pr.append("  Search term ", style="white")
            pr.append("›", style=f"{PINK} bold")
            console.print(pr, end=" ")
            q = input().strip()
            if not q:
                input("  Press Enter...")
                continue
            items = steam_search_store(q)
            console.print()
            if not items:
                console.print("  [no results]", style="rgb(120,120,120)")
            else:
                for i, it in enumerate(items[:10], 1):
                    console.print(f"  [{i}] {it['id']} | {it['name']}", style="white")
                console.print()
                pr2 = Text()
                pr2.append("  Pick # or AppID to add ", style="white")
                pr2.append("›", style=f"{PINK} bold")
                console.print(pr2, end=" ")
                sel = input().strip()
                if sel.isdigit() and 1 <= int(sel) <= len(items[:10]):
                    it = items[int(sel)-1]
                    console.print()
                    console.print(f"  Adding {it['name']} ({it['id']})...", style="white")
                    add_game_to_steam(it['id'], name=it['name'], steam_path=sp)
                    console.print(f"  [✓] Added — restart Steam", style="green")
                    input("  Press Enter...")
                elif sel.isdigit():
                    add_game_to_steam(sel, steam_path=sp)
                    input("  Press Enter...")
        elif choice == "2":
            console.clear()
            selp = Text()
            selp.append("Select option ", style="white")
            selp.append("›", style=f"{PINK} bold")
            selp.append(" 2", style="white")
            console.print(selp)
            console.print()
            detail_header("ADD GAME")
            pr = Text()
            pr.append("  AppID ", style="white")
            pr.append("›", style=f"{PINK} bold")
            console.print(pr, end=" ")
            appid = input().strip()
            if not appid:
                continue
            try:
                add_game_to_steam(appid, steam_path=sp)
            except Exception as e:
                console.print(f"  [!] {e}", style="red")
            input("  Press Enter...")
        elif choice == "3":
            console.clear()
            sel = Text()
            sel.append("Select option ", style="white")
            sel.append("›", style=f"{PINK} bold")
            sel.append(" 3", style="white")
            console.print(sel)
            console.print()
            detail_header("LIBRARY")
            libs = list_installed_library(sp)
            if not libs:
                console.print("  No Delta luas installed", style="rgb(120,120,120)")
            else:
                for it in libs:
                    line = Text()
                    line.append(f"  {it['appid']:>8} | ", style="white")
                    line.append(it['name'][:34], style="white")
                    console.print(line)
            # styled prompt like n.py
            console.print()
            txt = Text()
            txt.append("  Press Enter to return ", style="white")
            txt.append("›", style=f"{PINK} bold")
            console.print(txt, end=" ")
            input()
        elif choice == "4":
            console.clear()
            selp = Text()
            selp.append(" " * UI_MARGIN, style="white")
            selp.append("Select option ", style="white")
            selp.append("›", style=f"{PINK} bold")
            selp.append(" 4", style="white")
            console.print(selp)
            console.print()
            detail_header("FIXES")
            pr = Text()
            pr.append(" " * UI_MARGIN + "Search fixes ", style="white")
            pr.append("›", style=f"{PINK} bold")
            console.print(pr, end=" ")
            q_raw = input().strip()
            # Resolve name to appid (so Terraria -> 105600) like CLI
            q = resolve_appid(q_raw) if q_raw and not q_raw.isdigit() else q_raw
            if q and q.isdigit():
                fixes = get_denuvo_fixes(q)
                console.print(f"\n  Fixes for {q}: {len(fixes)}", style="white")
                if fixes:
                    for i, f in enumerate(fixes, 1):
                        title = html.unescape(f.get("Title") or f.get("title") or f.get("Id") or "")
                        if not IS_UTF:
                            title = title.encode("ascii", errors="replace").decode()
                        console.print(f"  [{i}] {title}", style="white")
                    sel = input("  Pick # to download (Enter to skip): ").strip()
                    if sel.isdigit() and 1 <= int(sel) <= len(fixes):
                        fix = fixes[int(sel)-1]
                        slot = "fix" if fix.get("hasFix", fix.get("HasFix")) else "manifest"
                        fix_id = fix.get("Id") or fix.get("id")
                        url = get_fix_signed_url(fix_id, slot)
                        if url:
                            apply_online_fix(q, fix_url=url, steam_path=sp)
                        else:
                            console.print("  Login required — run Delta login (same as Status)", style="yellow")
                    input("  Press Enter...")
                    continue
                else:
                    console.print(f"  No fixes for {q} (try different name)", style="yellow")
                    input("  Press Enter...")
                    continue
            idx = delta_fixes_index()
            for it in idx[:20]:
                console.print(f"  {it['appid']:>8} | {it['name']}", style="white")
            input("\n  Press Enter...")
        elif choice == "5":
            console.clear()
            selp = Text()
            selp.append(" " * UI_MARGIN, style="white")
            selp.append("Select option ", style="white")
            selp.append("›", style=f"{PINK} bold")
            selp.append(" 5", style="white")
            console.print(selp)
            console.print()
            detail_header("STATUS")
            # Status / Login
            steam_path = find_steam_path()
            console.print(f"Steam: {steam_path or 'not found'}", style="cyan")
            console.print(f"Library: {len(list_installed_library(steam_path))} games" if steam_path else "Library: n/a", style="white")
            tok = get_auth_token()
            if tok:
                console.print("Login: OK", style="green")
            else:
                console.print("Login: not logged in — fixes need login", style="yellow")
                console.print("Run Delta login for Discord OAuth", style="rgb(120,120,120)")
            # mini menu for login/logout
            sub = input("  [L]ogin / [O]ut / Enter to back: ").strip().lower()
            if sub == "l":
                do_pkce_login()
                input("  Press Enter...")
            elif sub == "o":
                if TOKEN_FILE.exists():
                    TOKEN_FILE.unlink()
                    console.print("Logged out", style="green")
                input("  Press Enter...")
        elif choice == "6":
            console.clear()
            selp = Text()
            selp.append(" " * UI_MARGIN, style="white")
            selp.append("Select option ", style="white")
            selp.append("›", style=f"{PINK} bold")
            selp.append(" 6", style="white")
            console.print(selp)
            console.print()
            detail_header("REMOVE")
            pr = Text()
            pr.append("  AppID to remove ", style="white")
            pr.append("›", style=f"{PINK} bold")
            console.print(pr, end=" ")
            raw = input().strip()
            if raw.lower() == "all":
                libs = list_installed_library(sp)
                if not libs:
                    console.print("  No games to remove", style="yellow")
                else:
                    console.print(f"  Removing {len(libs)} games...", style="yellow")
                    plug = st_plugin_dir(sp) if sp else None
                    cnt=0
                    for it in libs:
                        dst = plug / f"{it['appid']}.lua" if plug else None
                        if dst and dst.exists():
                            try:
                                dst.unlink()
                                cnt+=1
                            except: pass
                    console.print(f"  [-] Removed {cnt}/{len(libs)}", style="yellow")
            elif raw:
                appid = resolve_appid(raw)
                if appid and appid.isdigit():
                    plug = st_plugin_dir(sp) if sp else None
                    if plug:
                        dst = plug / f"{appid}.lua"
                        if dst.exists():
                            dst.unlink()
                            console.print(f"  [-] Removed {appid}", style="yellow")
                        else:
                            console.print(f"  Not installed: {appid}", style="red")
            input("  Press Enter...")
        elif choice == "7":
            console.clear()
            selp = Text()
            selp.append(" " * UI_MARGIN, style="white")
            selp.append("Select option ", style="white")
            selp.append("›", style=f"{PINK} bold")
            selp.append(" 7", style="white")
            console.print(selp)
            console.print()
            detail_header("UPDATE")
            pr = Text()
            pr.append("  AppID to update ", style="white")
            pr.append("›", style=f"{PINK} bold")
            console.print(pr, end=" ")
            raw = input().strip()
            if raw.lower() == "all":
                libs = list_installed_library(sp)
                if not libs:
                    console.print("  No games to update", style="yellow")
                else:
                    console.print(f"  Updating {len(libs)} games to latest...", style="white")
                    for it in libs:
                        try:
                            console.print(f"  → {it['appid']} {it['name']}", style="white")
                            add_game_to_steam(it['appid'], name=it['name'], steam_path=sp)
                        except Exception as e:
                            console.print(f"    [!] {e}", style="red")
                    console.print(f"  [✓] Updated {len(libs)} — restart Steam", style="green")
            elif raw:
                appid = resolve_appid(raw)
                if appid and appid.isdigit():
                    console.print(f"  Updating {appid} to latest...", style="white")
                    add_game_to_steam(appid, steam_path=sp)
                    console.print(f"  [✓] Updated — restart Steam", style="green")
            input("  Press Enter...")
        elif choice == "8":
            show_about()

        elif choice == "0" or choice.lower() in ["q","exit"]:
            break
        else:
            console.print(f"  Unknown option: {choice}", style="yellow")
            input("  Press Enter...")


def main():
    # Like LuaTools: ensure unlocker on every run, but NOT auto re-download All (AutoUpdate = unpinned)
    try:
        sp0 = find_steam_path()
        if sp0:
            try:
                ensure_unlocker(sp0)
            except: pass
    except: pass
    p = argparse.ArgumentParser(description="Delta by okaydrku — search, add to Steam, apply OnlineFix (Delta)")
    p.add_argument("--steam-path", help="Path to Steam folder (e.g. C:\\Program Files (x86)\\Steam)")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("search", help="Search Steam Store")
    s.add_argument("term", help="Game name or AppID fragment")
    s.add_argument("--cc", default="US")
    s.add_argument("--limit", type=int, default=10)
    s.set_defaults(func=cmd_search)

    a = sub.add_parser("add", help="Add game to Steam (create .lua)")
    a.add_argument("appid", help="Steam AppID")
    a.add_argument("--name", help="Game name (auto-fetched if omitted)")
    a.add_argument("--depot-key", help="Depot decryption key (hex) for full manifest unlock")
    a.add_argument("--manifest-gid", help="Manifest GID to pin")
    a.add_argument("--depot-id", help="Depot ID (default = appid)")
    a.add_argument("--stub", action="store_true", help="Create minimal addappid stub (old behavior, may show 0B)")
    a.add_argument("--fix-url", help="Optional: also apply OnlineFix from URL")
    a.add_argument("--fix-zip", help="Optional: also apply fix from local ZIP path")
    a.set_defaults(func=cmd_add)

    f = sub.add_parser("fix", help="Apply Fix (auto like Delta Fixes page, or manual ZIP)")
    f.add_argument("appid", help="Steam AppID")
    f.add_argument("--fix-url", help="Direct URL to fix ZIP (manual)")
    f.add_argument("--fix-zip", help="Local path to fix ZIP (manual)")
    f.add_argument("--game-dir", help="Override game install folder")
    f.add_argument("--auto", action="store_true", help="Try auto-download from fixes API first (like Delta)")
    f.set_defaults(func=cmd_fix)

    lib = sub.add_parser("library", help="List installed Delta games (like Delta Manage)")
    lib.set_defaults(func=cmd_library)

    info = sub.add_parser("info", help="Show depot/manifest info for AppID")
    info.add_argument("appid", help="Steam AppID")
    info.set_defaults(func=cmd_info)

    rem = sub.add_parser("remove", help="Remove Delta lua for AppID")
    rem.add_argument("appid", help="Steam AppID")
    rem.set_defaults(func=cmd_remove)

    fixes = sub.add_parser("fixes", help="Browse Delta fixes (auto, like Delta Fixes page)")
    fixes.add_argument("appid", nargs="?", default=None, help="AppID to show fixes for, or empty to list games")
    fixes.set_defaults(func=cmd_fixes)

    login = sub.add_parser("login", help="Login to Delta (Discord OAuth, like Delta app)")
    login.set_defaults(func=cmd_login)
    logout = sub.add_parser("logout", help="Logout and remove saved token")
    logout.set_defaults(func=cmd_logout)
    status = sub.add_parser("status", help="Show Delta status (Steam, library, login)")
    status.set_defaults(func=cmd_status)

    unlocker = sub.add_parser("unlocker", help="Install BetterSteamTools unlocker (fixes missing license / not appearing, like Delta")
    unlocker.set_defaults(func=cmd_unlocker)

    about = sub.add_parser("about", help="Show Delta credits & info")
    about.set_defaults(func=lambda args: show_about())

    launch = sub.add_parser("launch", help="Add/remove -onlinefix launch option (like Delta)")
    launch.add_argument("appid", help="Steam AppID")
    launch.add_argument("--remove", action="store_true", help="Remove -onlinefix instead of adding")
    launch.set_defaults(func=cmd_launch)

    dlc = sub.add_parser("dlc", help="Generate DLC lua via /api/dlc/generate (like Delta)")
    dlc.add_argument("appid", help="DLC AppID")
    dlc.add_argument("--base", required=True, help="Base game AppID")
    dlc.set_defaults(func=cmd_dlc)

    st = sub.add_parser("setstat", help="setStat(appid, steamid) for achievements (like Delta BetterSteamTools)")
    st.add_argument("appid", help="AppID")
    st.add_argument("steamid", help="SteamID64 (e.g. 76561197960287930) or https://stats.opensteamtool.com/{appid} default 76561198028121353")
    st.set_defaults(func=cmd_setstat)

    cl = sub.add_parser("cloud", help="CloudRedirect toggle (Delta Future — local saves)")
    cl.add_argument("--enable", action="store_true", help="Enable CloudRedirect")
    cl.add_argument("--disable", action="store_true", help="Disable")
    cl.set_defaults(func=cmd_cloud)

    upd = sub.add_parser("update", help="Update game to latest manifest (re-add, like Delta Manage update)")
    upd.add_argument("appid", help="Steam AppID or name (resolved via search)")
    upd.set_defaults(func=lambda args: add_game_to_steam(resolve_appid(str(args.appid)) or args.appid, steam_path=Path(args.steam_path) if getattr(args, "steam_path", None) else find_steam_path()))

    det = sub.add_parser("details", help="Alias for info — show depot/manifest info for AppID")
    det.add_argument("appid", help="Steam AppID")
    det.set_defaults(func=cmd_info)

    # default = interactive if no subcommand
    args = p.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        cmd_interactive(args)

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        try:
            console.print("\n  Exiting...", style="rgb(120,120,120)")
        except: pass
        sys.exit(0)