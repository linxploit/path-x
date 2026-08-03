<div align="center">

```
 ██████╗  █████╗ ████████╗██╗  ██╗██╗  ██╗
 ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║╚██╗██╔╝
██████╔╝███████║   ██║   ███████║ ╚███╔╝
██╔═══╝ ██╔══██║   ██║   ██╔══██║ ██╔██╗
 ██║     ██║  ██║   ██║   ██║  ██║██╔╝ ██╗
 ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝
```

###  Directory & Endpoint Discovery Scanner 

**Common paths only. Rate-limited. Not exhaustive.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Made by Mindless](https://img.shields.io/badge/Made%20by-Mindless-ff69b4.svg)](https://linxploit.com/founder)
[![Linxploit](https://img.shields.io/badge/Linxploit-linxploit.com-black.svg)](https://linxploit.com)

**Made by [Mindless](https://linxploit.com/founder) — Founder & CEO of [Linxploit](https://linxploit.com)**

</div>

---

## 🧠 What is PathX?

**PathX** checks a target for common, publicly-known paths — admin panels, API routes, backup folders, `.git`/`.env` leftovers, and more — and reports which ones actually respond.

What sets it apart from a bare status-code loop is that it **fingerprints the server's own "not found" behavior first**. Plenty of modern sites (SPAs, misconfigured routers) return `200 OK` with the same page for *every* path — which turns a naive fuzzer into a wall of false positives. PathX probes a random, near-certainly-nonexistent path up front, and filters out any "hit" that just matches that baseline.

It's a discovery tool, not an exploitation tool: it says exactly which paths responded and how, and leaves the judgment call to you.

---

## ✨ Features

- 🎨 **Ultra-clean ASCII UI** — gradient banner, boxed panels, live per-target progress bar, and color-coded status output.
- 🧭 **Soft-404 baseline detection** — probes a random nonexistent path first and filters out hits that just match the server's generic "not found" response, dramatically cutting false positives.
- 📋 **Built-in wordlist of ~45 common paths** — admin panels, API routes, backup/config leftovers, `.git`/`.env` exposure, CMS defaults, and more — or bring your own with `-w`.
- 🧩 **Extension expansion** — `--ext php,bak,zip` automatically appends extensions to every word in the list.
- ⚡ **Concurrent scanning** — configurable thread count per target, with an optional `--delay` to stay gentle on shared infrastructure.
- 🎯 **Configurable status-code matching** — decide what counts as a "hit" (`200,204,301,302,307,401,403` by default).
- 🌐 **Multi-target support** — a single URL or an entire list, one after another, each with its own baseline check.
- 🔐 **Custom headers, cookies & SSL control** — scan behind authentication the same way a logged-in browser would.
- 📊 **Exportable reports** — full **JSON** (every hit + baseline info) or flat **CSV**.
- 🛡️ **Authorization gate** — tells you up front roughly how many requests it's about to send, and confirms you're allowed to test the target before sending a single one (skippable with `--yes` for your own pipelines).

---

## 📸 Preview

```
  ✦ Directory & Endpoint Discovery Scanner ✦
v2.0.0 · Common paths only. Rate-limited. Not exhaustive.

═══ ➤ SCANNING 1 TARGET(S) ══════════════════════════════
  wordlist=48 paths  threads=8  timeout=6s  delay=0.0s

═══ 🧭 TARGET: https://example.com ═══════════════════════
[████████████████████████████████] 100%

[ FOUND ] https://example.com/.git/config                (200) 36b
[ FOUND ] https://example.com/admin                       (200) 5421b
[ FOUND ] https://example.com/api                         (200) 15b
[ FOUND ] https://example.com/backup                      (403) 9b

[*] 4 likely-real hit(s) out of 48 paths tested.

═══ ✦ SCAN SUMMARY ══════════════════════════════════════
  Targets scanned: 1
  Paths tested per target: 48
  Total likely-real hits: 4
```

On a site that returns `200 OK` for everything (SPA catch-all / soft-404 behavior), PathX calls it out instead of reporting 48 false hits:

```
⚠ This server appears to return the same page for unknown paths
  (soft-404). Suspicious hits matching that baseline are marked below.

[*] 0 likely-real hit(s) out of 48 paths tested.
```

---

## 📦 Installation

```bash
git clone https://github.com/linxploit/path-x.git
cd pathx
pip install -r requirements.txt
```

Requires **Python 3.8+**.

---

## 🚀 Usage

### Scan a single target with the built-in wordlist

```bash
python3 pathx.py -u "https://example.com"
```

### Scan a list of targets

```bash
python3 pathx.py -l examples/targets.txt --threads 8
```

### Use a custom wordlist, with extensions

```bash
python3 pathx.py -u "https://example.com" -w examples/wordlist.txt --ext php,bak,zip
```

### Be gentle on the target (rate limiting)

```bash
python3 pathx.py -u "https://example.com" --threads 3 --delay 0.25
```

### Scan behind authentication

```bash
python3 pathx.py -u "https://example.com/internal" \
  -H "Authorization: Bearer <token>" \
  -b "session=abc123"
```

### Save a report

```bash
python3 pathx.py -l examples/targets.txt -o report.json
python3 pathx.py -l examples/targets.txt -o report.csv
```

### Skip the authorization prompt (for your own automated pipelines)

```bash
python3 pathx.py -u "https://example.com" --yes
```

### Full option reference

```bash
python3 pathx.py --help
```

| Flag | Description |
|---|---|
| `-u`, `--url` | Single target base URL |
| `-l`, `--list` | File with one target base URL per line |
| `-w`, `--wordlist` | Custom wordlist file (default: built-in common paths) |
| `--ext` | Comma-separated extensions to append to each word |
| `-t`, `--timeout` | Per-request timeout in seconds (default: `6`) |
| `--threads` | Concurrent worker threads per target (default: `8`) |
| `--delay` | Delay in seconds before each request (default: `0`) |
| `--status-codes` | Comma-separated status codes considered a "hit" |
| `--no-soft-404-detection` | Disable the automatic baseline check |
| `-H`, `--header` | Custom header `"Key: Value"`, repeatable |
| `-b`, `--cookies` | Cookie string `"a=1; b=2"` |
| `--no-verify-ssl` | Disable SSL certificate verification |
| `-o`, `--output` | Save report to `.json` or `.csv` |
| `-v`, `--verbose` | Also show paths filtered as likely soft-404 |
| `--yes` | Skip the authorization confirmation prompt |
| `--no-banner` | Suppress the ASCII banner |
| `--version` | Print version info and exit |

---

## 🧭 How soft-404 detection works

Before testing the wordlist, PathX requests one random path that's virtually guaranteed not to exist (e.g. `/pathx_x7f2ndq1k9pl`). It records that response's status code and content length as a **baseline**.

For every subsequent "hit," if the status code *and* content length are both suspiciously close to that baseline, PathX marks it `likely_soft_404` and excludes it from the main results — while still showing it under `-v` for full transparency. This single check eliminates the majority of false positives you'd otherwise get from single-page apps and catch-all routers.

> ⚠️ **A discovered path is a starting point, not a finding.** Confirm manually what's actually being served, whether it's genuinely reachable in your threat model, and whether it needs to be addressed, before reporting or acting on results.

---

## ⚖️ Responsible use

PathX sends a modest, configurable number of ordinary GET requests per target. Still:

- Only run PathX against targets you **own** or have **explicit permission** to assess.
- PathX tells you up front roughly how many requests it's about to send and asks you to confirm authorization every time, unless you pass `--yes`.
- Use `--threads` and `--delay` responsibly, especially against shared or production infrastructure.
- You are solely responsible for how you use this tool and for complying with all applicable laws and the terms of any authorization you've been granted.

---

## 🛠️ Project structure

```
pathx/
├── pathx.py               # Main executable — the tool itself
├── requirements.txt        # Python dependencies
├── examples/
│   ├── targets.txt           # Example target list for -l/--list
│   └── wordlist.txt          # Example custom wordlist for -w/--wordlist
├── tests/
│   └── test_pathx.py         # Unit tests for wordlist/discovery logic
├── LICENSE                 # MIT License
└── README.md                # You are here
```

---

## 🤝 Contributing

Issues and pull requests are welcome — expanded default wordlists, smarter soft-404 heuristics, and additional export formats are all great contributions. Please keep additions passive/read-only and respectful of target load, in line with PathX's design.

---

## 📜 License

Released under the [MIT License](LICENSE).

---

<div align="center">

### Made by **Mindless**
**Founder & CEO of [Linxploit](https://linxploit.com)**

🌐 [linxploit.com](https://linxploit.com) &nbsp;·&nbsp; 👤 [linxploit.com/founder](https://linxploit.com/founder)

</div>
