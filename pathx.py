#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
██████╗  █████╗ ████████╗██╗  ██╗██╗  ██╗
██╔══██╗██╔══██╗╚══██╔══╝██║  ██║╚██╗██╔╝
██████╔╝███████║   ██║   ███████║ ╚███╔╝
██╔═══╝ ██╔══██║   ██║   ██╔══██║ ██╔██╗
██║     ██║  ██║   ██║   ██║  ██║██╔╝ ██╗
╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝

PathX — Directory & Endpoint Discovery Scanner
Made by Mindless — Founder & CEO of Linxploit
https://linxploit.com | https://linxploit.com/founder

DISCLAIMER:
    PathX requests a list of common, publicly-documented path names
    against a target (the same kind of request any browser or search
    engine crawler makes) and reports which ones respond. It sends no
    exploit payloads and performs no authentication bypass attempts.

    A discovered path is a starting point for manual review, not proof
    of a vulnerability. Sending many requests to a target you don't
    control or don't have permission to test may be illegal and can
    place real load on someone else's infrastructure — use the
    built-in rate limiting and only test authorized targets.
"""

import argparse
import concurrent.futures
import csv
import json
import os
import random
import string
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import requests
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

TOOL_NAME = "PathX"
VERSION = "2.0.0"
AUTHOR = "Mindless"
ORG = "Linxploit"
SITE = "https://linxploit.com"
PORTFOLIO = "https://linxploit.com/founder"

requests.packages.urllib3.disable_warnings()  # noqa


GRADIENT = [
    "\033[38;5;196m",  # red
    "\033[38;5;202m",
    "\033[38;5;208m",
    "\033[38;5;214m",
    "\033[38;5;220m",
    "\033[38;5;226m",
    "\033[38;5;190m",
    "\033[38;5;154m",
    "\033[38;5;118m",
    "\033[38;5;82m",
]
RESET = Style.RESET_ALL
DIM = Style.DIM
BOLD = Style.BRIGHT

C_OK = Fore.GREEN + BOLD
C_WARN = Fore.YELLOW + BOLD
C_BAD = Fore.RED + BOLD
C_INFO = Fore.CYAN
C_MUTE = Fore.WHITE + DIM
C_ACC = "\033[38;5;208m" + BOLD  # orange accent


def gradient_line(text: str) -> str:
    out = []
    n = max(len(GRADIENT) - 1, 1)
    for i, ch in enumerate(text):
        color = GRADIENT[int((i / max(len(text) - 1, 1)) * n)]
        out.append(color + ch)
    return "".join(out) + RESET


def supports_unicode() -> bool:
    enc = (sys.stdout.encoding or "").lower()
    return "utf" in enc


UNICODE_OK = supports_unicode()

BOX = {
    "tl": "╔" if UNICODE_OK else "+",
    "tr": "╗" if UNICODE_OK else "+",
    "bl": "╚" if UNICODE_OK else "+",
    "br": "╝" if UNICODE_OK else "+",
    "h": "═" if UNICODE_OK else "-",
    "v": "║" if UNICODE_OK else "|",
    "lt": "╠" if UNICODE_OK else "+",
    "rt": "╣" if UNICODE_OK else "+",
    "arrow": "➤" if UNICODE_OK else ">",
    "bullet": "●" if UNICODE_OK else "*",
    "check": "✔" if UNICODE_OK else "OK",
    "cross": "✘" if UNICODE_OK else "X",
    "warn": "⚠" if UNICODE_OK else "!",
    "spark": "✦" if UNICODE_OK else "*",
    "compass": "🧭" if UNICODE_OK else "[>]",
}

BANNER_ART = r"""
██████╗  █████╗ ████████╗██╗  ██╗██╗  ██╗
██╔══██╗██╔══██╗╚══██╔══╝██║  ██║╚██╗██╔╝
██████╔╝███████║   ██║   ███████║ ╚███╔╝
██╔═══╝ ██╔══██║   ██║   ██╔══██║ ██╔██╗
██║     ██║  ██║   ██║   ██║  ██║██╔╝ ██╗
╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
""".rstrip("\n")

BANNER_ART_ASCII = r"""
 ____   __   ____  _  _  _  _
(  _ \ / _\ (_  _)/ )( \( \/ )
 )___//    \  )(  ) __ ( )  (
(__)  \_/\_/ (__) \_)(_/(_/\_)
""".rstrip("\n")

import re  # noqa: E402
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


def render_banner():
    art = BANNER_ART if UNICODE_OK else BANNER_ART_ASCII
    width = max(len(line) for line in art.splitlines()) + 4

    print()
    for line in art.splitlines():
        print(gradient_line(line))

    tagline = f"{BOX['spark']} Directory & Endpoint Discovery Scanner {BOX['spark']}"
    print()
    print(C_ACC + tagline.center(width) + RESET)
    sub = f"v{VERSION} · Common paths only. Rate-limited. Not exhaustive."
    print(C_MUTE + sub.center(width) + RESET)
    print()

    info_box(
        [
            f"{BOX['bullet']} Author   : {AUTHOR}  ({ORG} — Founder & CEO)",
            f"{BOX['bullet']} Website  : {SITE}",
            f"{BOX['bullet']} Portfolio: {PORTFOLIO}",
        ],
        title="ABOUT",
        color=Fore.MAGENTA,
    )


def info_box(lines: List[str], title: str = "", color: str = Fore.CYAN, width: Optional[int] = None):
    content_width = width or (max((len(strip_ansi(l)) for l in lines), default=20) + 4)
    top = f"{color}{BOX['tl']}{BOX['h'] * content_width}{BOX['tr']}{RESET}"
    bot = f"{color}{BOX['bl']}{BOX['h'] * content_width}{BOX['br']}{RESET}"
    print(top)
    if title:
        pad = content_width - len(title) - 2
        left = pad // 2
        right = pad - left
        print(f"{color}{BOX['v']}{RESET} {' ' * left}{BOLD}{title}{RESET}{' ' * right} {color}{BOX['v']}{RESET}")
        print(f"{color}{BOX['lt']}{BOX['h'] * content_width}{BOX['rt']}{RESET}")
    for line in lines:
        pad = max(content_width - len(strip_ansi(line)) - 1, 0)
        print(f"{color}{BOX['v']}{RESET} {Fore.WHITE}{line}{RESET}{' ' * pad}{color}{BOX['v']}{RESET}")
    print(bot)


def section_header(title: str, color: str = Fore.CYAN, icon: str = None):
    icon = icon or BOX["arrow"]
    print()
    print(color + BOLD + f"{BOX['h'] * 3} {icon} {title} " + BOX['h'] * max(0, 50 - len(title)) + RESET)


def hr(color=C_MUTE, width=62):
    print(color + BOX["h"] * width + RESET)


def status_color(code: int) -> str:
    if code in (200, 204):
        return C_OK
    if code in (301, 302, 307, 308):
        return C_INFO
    if code in (401, 403):
        return C_WARN
    return C_MUTE


import threading  # noqa: E402

_progress_lock = threading.Lock()


def progress_bar(current: int, total: int, label: str = "", width: int = 32):
    ratio = current / total if total else 1
    filled = int(width * ratio)
    bar_char = "█" if UNICODE_OK else "#"
    empty_char = "░" if UNICODE_OK else "-"
    bar = bar_char * filled + empty_char * (width - filled)
    pct = int(ratio * 100)
    color = C_OK if pct == 100 else C_INFO
    with _progress_lock:
        sys.stdout.write(f"\r{color}[{bar}]{RESET} {pct:3d}%  {C_MUTE}{label}{RESET}   ")
        sys.stdout.flush()
        if current >= total:
            sys.stdout.write("\n")



DEFAULT_WORDLIST = [
    "admin", "administrator", "login", "logout", "dashboard", "portal",
    "uploads", "upload", "images", "assets", "static", "media",
    "api", "api/v1", "api/v2", "graphql",
    "test", "testing", "demo", "dev", "staging",
    "backup", "backups", "old", "tmp", "temp",
    "config", "configuration", "settings",
    "wp-admin", "wp-login.php", "wp-content", "wp-includes",
    "phpmyadmin", "adminer", "server-status",
    ".git", ".git/config", ".env", ".env.example",
    ".well-known", "robots.txt", "sitemap.xml",
    "console", "swagger", "swagger-ui", "docs", "documentation",
]

ACCEPTED_STATUS_DEFAULT = [200, 204, 301, 302, 307, 401, 403]


def load_wordlist(path: Optional[str]) -> List[str]:
    if not path:
        return list(DEFAULT_WORDLIST)
    if not os.path.isfile(path):
        print(C_BAD + f"[!] Wordlist file not found: {path}" + RESET)
        sys.exit(1)
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def expand_with_extensions(words: List[str], extensions: List[str]) -> List[str]:
    if not extensions:
        return words
    expanded = list(words)
    for word in words:
        if "." in word:  # already has an extension / is a file-like entry
            continue
        for ext in extensions:
            ext = ext.lstrip(".")
            expanded.append(f"{word}.{ext}")
    return expanded


@dataclass
class PathHit:
    path: str
    url: str
    status_code: int
    content_length: Optional[int] = None
    redirect_location: Optional[str] = None
    likely_soft_404: bool = False


@dataclass
class ScanResult:
    base_url: str
    hits: List[PathHit] = field(default_factory=list)
    paths_tested: int = 0
    baseline_status: Optional[int] = None
    baseline_length: Optional[int] = None
    soft_404_detected: bool = False
    error: Optional[str] = None


def detect_baseline(base_url: str, timeout: int, headers: dict, cookies: dict, verify_ssl: bool) -> Tuple[Optional[int], Optional[int]]:
    """Probe a random, near-certainly-nonexistent path to fingerprint the
    server's 'not found' response, so real soft-404 pages don't get
    reported as genuine hits."""
    marker = "pathx_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    test_url = f"{base_url.rstrip('/')}/{marker}"
    try:
        r = requests.get(test_url, timeout=timeout, headers=headers, cookies=cookies,
                          verify=verify_ssl, allow_redirects=False)
        return r.status_code, len(r.content)
    except Exception:
        return None, None


def probe_path(
    base_url: str,
    path: str,
    timeout: int,
    headers: dict,
    cookies: dict,
    verify_ssl: bool,
    accepted_statuses: List[int],
    baseline_status: Optional[int],
    baseline_length: Optional[int],
    length_tolerance: int,
) -> Optional[PathHit]:
    test_url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    try:
        r = requests.get(test_url, timeout=timeout, headers=headers, cookies=cookies,
                          verify=verify_ssl, allow_redirects=False)
    except Exception:
        return None

    if r.status_code not in accepted_statuses:
        return None

    content_length = len(r.content)
    likely_soft = False
    if (baseline_status is not None and r.status_code == baseline_status and
            baseline_length is not None and abs(content_length - baseline_length) <= length_tolerance):
        likely_soft = True

    return PathHit(
        path=path,
        url=test_url,
        status_code=r.status_code,
        content_length=content_length,
        redirect_location=r.headers.get("Location"),
        likely_soft_404=likely_soft,
    )


def scan_target(
    base_url: str,
    wordlist: List[str],
    timeout: int,
    headers: dict,
    cookies: dict,
    verify_ssl: bool,
    accepted_statuses: List[int],
    threads: int,
    delay: float,
    detect_soft_404: bool,
    progress_cb=None,
) -> ScanResult:
    result = ScanResult(base_url=base_url, paths_tested=len(wordlist))

    baseline_status, baseline_length = (None, None)
    if detect_soft_404:
        baseline_status, baseline_length = detect_baseline(base_url, timeout, headers, cookies, verify_ssl)
        result.baseline_status = baseline_status
        result.baseline_length = baseline_length

    completed = 0
    completed_lock = threading.Lock()

    def _task(path):
        nonlocal completed
        if delay:
            time.sleep(delay)
        hit = probe_path(
            base_url, path, timeout, headers, cookies, verify_ssl,
            accepted_statuses, baseline_status, baseline_length, length_tolerance=25,
        )
        with completed_lock:
            completed += 1
            if progress_cb:
                progress_cb(completed, len(wordlist))
        return hit

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as pool:
            for hit in pool.map(_task, wordlist):
                if hit:
                    result.hits.append(hit)
    except Exception as e:  # noqa
        result.error = str(e)

    if any(h.likely_soft_404 for h in result.hits):
        result.soft_404_detected = True

    return result


def print_result_header(base_url: str):
    print()
    section_header(f"TARGET: {base_url}", Fore.CYAN, BOX["compass"])


def print_hits(result: ScanResult, verbose: bool):
    if result.error:
        print(f"{C_BAD}[{BOX['cross']} ERROR ]{RESET} {result.error}")
        return

    if result.soft_404_detected:
        print(f"{C_WARN}{BOX['warn']} This server appears to return the same page for unknown paths "
              f"(soft-404). Suspicious hits matching that baseline are marked below.{RESET}\n")

    real_hits = [h for h in result.hits if not h.likely_soft_404]
    soft_hits = [h for h in result.hits if h.likely_soft_404]

    if not result.hits:
        print(f"{C_MUTE}[ NOT FOUND ] No common endpoints responded out of {result.paths_tested} tested{RESET}")
        return

    for hit in sorted(real_hits, key=lambda h: h.path):
        color = status_color(hit.status_code)
        extra = f"  → {hit.redirect_location}" if hit.redirect_location else ""
        size = f"{hit.content_length}b" if hit.content_length is not None else "?"
        print(f"{color}[ FOUND ] {hit.url:<55}{RESET} {color}({hit.status_code}){RESET} "
              f"{C_MUTE}{size}{extra}{RESET}")

    if verbose and soft_hits:
        print(f"\n{C_MUTE}  Filtered as likely soft-404 (matched baseline response):{RESET}")
        for hit in sorted(soft_hits, key=lambda h: h.path):
            print(f"{C_MUTE}  ~ {hit.url} ({hit.status_code}){RESET}")

    print(f"\n{C_MUTE}[*] {len(real_hits)} likely-real hit(s) out of {result.paths_tested} paths tested.{RESET}")


def print_summary(results: List[ScanResult]):
    section_header("SCAN SUMMARY", Fore.MAGENTA, BOX["spark"])
    total_hits = sum(len([h for h in r.hits if not h.likely_soft_404]) for r in results)
    total_paths = sum(r.paths_tested for r in results)
    soft_flagged = sum(1 for r in results if r.soft_404_detected)

    print(f"  {BOLD}Targets scanned:{RESET} {len(results)}")
    print(f"  {BOLD}Paths tested per target:{RESET} {total_paths // len(results) if results else 0}")
    print(f"  {C_OK}Total likely-real hits:{RESET} {total_hits}")
    if soft_flagged:
        print(f"  {C_WARN}{soft_flagged} target(s) showed soft-404 behavior (false positives filtered){RESET}")
    print()


def save_json(results: List[ScanResult], path: str):
    data = {
        "tool": TOOL_NAME,
        "version": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "author": AUTHOR,
        "organization": ORG,
        "results": [
            {
                "base_url": r.base_url,
                "paths_tested": r.paths_tested,
                "baseline_status": r.baseline_status,
                "baseline_length": r.baseline_length,
                "soft_404_detected": r.soft_404_detected,
                "error": r.error,
                "hits": [asdict(h) for h in r.hits],
            }
            for r in results
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_csv(results: List[ScanResult], path: str):
    fields = ["base_url", "path", "url", "status_code", "content_length",
              "redirect_location", "likely_soft_404"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            for h in r.hits:
                row = asdict(h)
                row["base_url"] = r.base_url
                writer.writerow({k: row.get(k) for k in fields})


def parse_header_list(items: Optional[List[str]]) -> dict:
    headers = {}
    if not items:
        return headers
    for item in items:
        if ":" in item:
            k, v = item.split(":", 1)
            headers[k.strip()] = v.strip()
    return headers


def parse_cookie_string(cookie_str: Optional[str]) -> dict:
    cookies = {}
    if not cookie_str:
        return cookies
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies


def load_targets(args) -> List[str]:
    targets = []
    if args.url:
        targets.append(args.url)
    if args.list:
        if not os.path.isfile(args.list):
            print(C_BAD + f"[!] File not found: {args.list}" + RESET)
            sys.exit(1)
        with open(args.list, "r", encoding="utf-8") as f:
            targets.extend(line.strip() for line in f if line.strip() and not line.startswith("#"))
    return targets


def confirm_authorization(skip: bool, num_paths: int) -> bool:
    if skip:
        return True
    info_box(
        [
            f"{BOX['warn']} PathX will send ~{num_paths} requests per target.",
            f"{BOX['warn']} Only assess targets you OWN or are AUTHORIZED to test.",
            f"{BOX['warn']} Use --delay / --threads responsibly on shared infrastructure.",
        ],
        title="AUTHORIZATION",
        color=Fore.YELLOW,
    )
    try:
        answer = input(f"{BOLD}Type 'yes' to confirm you are authorized: {RESET}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer == "yes"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pathx",
        description=f"{TOOL_NAME} — Directory & Endpoint Discovery Scanner by {AUTHOR} ({ORG})",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  pathx.py -u https://example.com\n"
            "  pathx.py -u https://example.com -w custom_wordlist.txt --ext php,bak\n"
            "  pathx.py -l targets.txt --threads 8 --delay 0.1 -o report.json\n"
        ),
    )
    parser.add_argument("-u", "--url", help="Target base URL to scan")
    parser.add_argument("-l", "--list", help="File containing a list of target base URLs (one per line)")
    parser.add_argument("-w", "--wordlist", help="Path to a custom wordlist file (default: built-in common paths)")
    parser.add_argument("--ext", help="Comma-separated extensions to append to each word (e.g. php,html,bak)")
    parser.add_argument("-t", "--timeout", type=int, default=6, help="Per-request timeout in seconds (default: 6)")
    parser.add_argument("--threads", type=int, default=8, help="Concurrent worker threads per target (default: 8)")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay in seconds before each request (default: 0)")
    parser.add_argument("--status-codes", default=",".join(map(str, ACCEPTED_STATUS_DEFAULT)),
                         help="Comma-separated status codes considered a 'hit' "
                              f"(default: {','.join(map(str, ACCEPTED_STATUS_DEFAULT))})")
    parser.add_argument("--no-soft-404-detection", action="store_true",
                         help="Disable the automatic soft-404 baseline check")
    parser.add_argument("-H", "--header", action="append", help="Custom header 'Key: Value' (repeatable)")
    parser.add_argument("-b", "--cookies", help="Cookie string 'a=1; b=2'")
    parser.add_argument("--no-verify-ssl", action="store_true", help="Disable SSL certificate verification")
    parser.add_argument("-o", "--output", help="Save results to file (.json or .csv, inferred from extension)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Also show paths filtered as likely soft-404")
    parser.add_argument("--yes", action="store_true", help="Skip the authorization confirmation prompt")
    parser.add_argument("--no-banner", action="store_true", help="Suppress the ASCII banner")
    parser.add_argument("--version", action="store_true", help="Show version information and exit")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        print(f"{TOOL_NAME} v{VERSION} — by {AUTHOR} ({ORG})")
        return

    if not args.no_banner:
        render_banner()

    targets = load_targets(args)
    if not targets:
        parser.print_help()
        print(C_BAD + "\n[!] No target provided. Use -u/--url or -l/--list.\n" + RESET)
        sys.exit(1)

    wordlist = load_wordlist(args.wordlist)
    extensions = [e.strip() for e in args.ext.split(",")] if args.ext else []
    wordlist = expand_with_extensions(wordlist, extensions)

    try:
        accepted_statuses = [int(c.strip()) for c in args.status_codes.split(",") if c.strip()]
    except ValueError:
        print(C_BAD + "[!] --status-codes must be a comma-separated list of integers.\n" + RESET)
        sys.exit(1)

    if not confirm_authorization(args.yes, len(wordlist)):
        print(C_BAD + "\n[!] Authorization not confirmed. Aborting.\n" + RESET)
        sys.exit(1)

    headers = parse_header_list(args.header)
    cookies = parse_cookie_string(args.cookies)
    headers.setdefault("User-Agent", f"Mozilla/5.0 ({TOOL_NAME}/{VERSION}; +{SITE})")

    section_header(f"SCANNING {len(targets)} TARGET(S)", Fore.CYAN, BOX["arrow"])
    print(f"{C_MUTE}  wordlist={len(wordlist)} paths  threads={args.threads}  "
          f"timeout={args.timeout}s  delay={args.delay}s{RESET}")

    results: List[ScanResult] = []
    for base_url in targets:
        print_result_header(base_url)

        def _progress(done, total, _url=base_url):
            progress_bar(done, total, label=f"probing {_url}")

        result = scan_target(
            base_url, wordlist, args.timeout, headers, cookies, not args.no_verify_ssl,
            accepted_statuses, args.threads, args.delay, not args.no_soft_404_detection,
            progress_cb=_progress,
        )
        results.append(result)
        print()
        print_hits(result, args.verbose)

    print()
    print_summary(results)

    if args.output:
        ext = os.path.splitext(args.output)[1].lower()
        if ext == ".csv":
            save_csv(results, args.output)
        else:
            save_json(results, args.output)
        print(C_OK + f"{BOX['check']} Report saved to: {args.output}\n" + RESET)

    print(C_MUTE + f"{BOX['h']*62}" + RESET)
    print(C_ACC + f"  {TOOL_NAME} · Made by {AUTHOR} — Founder & CEO of {ORG}" + RESET)
    print(C_MUTE + f"  {SITE}  |  {PORTFOLIO}" + RESET)
    print(C_MUTE + f"{BOX['h']*62}\n" + RESET)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(C_WARN + "\n\n[!] Interrupted by user. Exiting.\n" + RESET)
        sys.exit(130)
