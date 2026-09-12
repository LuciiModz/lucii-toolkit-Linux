# LUCII'S TOOLKIT — The Ultimate Linux Hacking Suite

```
██╗     ██╗   ██╗ ██████╗██╗██╗███████╗    ████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗
██║     ██║   ██║██╔════╝██║██║██╔════╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝
██║     ██║   ██║██║     ██║██║███████╗       ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║
██║     ██║   ██║██║     ██║██║╚════██║       ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║
███████╗╚██████╔╝╚██████╗██║██║███████║       ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║
╚══════╝ ╚═════╝  ╚═════╝╚═╝╚═╝╚══════╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝
```

**made by lucii**

164 tools · 15 categories · Terminal-native · No browser needed

---

## Install

```bash
git clone https://github.com/LuciiModz/lucii-toolkit-Linux.git
cd lucii-toolkit-Linux
chmod +x install.sh && sudo ./install.sh
pip install -r requirements.txt --break-system-packages
python3 lucii.py
```

---

## Categories

| # | Category          | Tools | Coverage |
|---|------------------|-------|----------|
| 1  | RECON & OSINT    | 20    | nmap x3, gobuster, ffuf, amass, shodan, wayback, crt.sh, masscan, dnsrecon |
| 2  | WEB ATTACK       | 15    | sqlmap, xsstrike, nikto, wpscan, commix, CORS, JWT crack, param miner, XXE |
| 3  | PRIVESC          | 15    | linpeas, SUID, caps, cron, pspy, GTFOBins, LXD, NFS, env secrets |
| 4  | NETWORK & MITM   | 14    | tcpdump, ARP spoof, chisel, responder, mitm6, bettercap, VLAN hop, socat |
| 5  | EXPLOIT          | 13    | MSF, revshell x7, msfvenom, EternalBlue, PrintNightmare, ROP, ret2libc |
| 6  | CREDS & HASHES   | 14    | hashcat x3, john, hydra x3, CME, PTH, secretsdump, zip2john, kerbrute |
| 7  | ACTIVE DIRECTORY | 11    | bloodhound, kerberoast, AS-REP, DCSync, golden ticket, zerologon, SMB relay |
| 8  | PERSISTENCE      | 7     | cron, systemd, bashrc, SSH key, MOTD, LD_PRELOAD, at job |
| 9  | LOG CLEAR        | 7     | full wipe, history nuke, utmp, shred, stomp, disable syslog, selective edit |
| 10 | FORENSICS        | 10    | volatility3, binwalk, exiftool, yara, PCAP extract, disk image, entropy |
| 11 | PHISHING & SE    | 7     | GoPhish, SET, evilginx2, beef-xss, site clone, email spoof check |
| 12 | MOBILE / APK     | 7     | apktool, frida, SSL bypass, ADB, MobSF, static analysis |
| 13 | CRYPTO & ENCODING| 10    | b64, ROT13, caesar brute, XOR, hash gen, openssl, steghide, cyberchef |
| 14 | CLOUD ATTACK     | 7     | AWS/GCP/Azure metadata SSRF, S3 enum, docker registry, kubernetes |
| 15 | MALWARE ANALYSIS | 7     | VirusTotal, PE analysis, strace, packer detect, deobfuscate PowerShell |
| 16 | C2 FRAMEWORK     | 8     | Sliver C2 Server, Sliver Implant Gen, Havoc C2 Start, Covenant C2, SimpleHTTP C2, DNS C2 Setup, ICMP C2, Cobalt Strike Aggressor |
| 17 | WIRELESS / RF    | 10    | WiFi Monitor Mode, WPA Handshake Cap, Deauth Attack, WPA Crack Hashcat, PMKID Attack, Evil Twin AP, Bluetooth Scan, BLE Scan, SDR Signal Capture, WPS Pin Attack |
| ... | PLUS 4 MORE TABS | 28   | INSTALL THE TOOL TODAY AND HAVE FUN YOU LITTLE HACKERS |
---

## Usage

```
python3 lucii.py

  1-15  select category
  c     cheat sheet (20 quick-reference one-liners)
  q     quit

Inside a category:
  #     select tool
  b     back

Inside a tool:
  fill fields → r (run) / g (regenerate) / b (back)
```

---

## Requirements

- Python 3.8+
- `rich`, `impacket`, `ldap3`, `ldapdomaindump` (pip)
- See `requirements.txt` for full Python dep list
- See `install.sh` for all system tools (apt, gem, binary)

---

## Platform

Tested on Kali Linux, Parrot OS, Ubuntu 22.04+. Most tools are pre-installed on Kali — `install.sh` handles the rest.
