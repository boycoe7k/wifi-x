#!/usr/bin/env python3
"""
WIFI-X — Terminal WiFi Network Scanner
Part of the Dephine Tools collection
"""

import os
import sys
import subprocess
import time
import threading
import re

# ─────────────────────────────────────────────
#  ANSI COLORS
# ─────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    NEON    = "\033[1;36m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    BLUE    = "\033[94m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    WHITE   = "\033[97m"
    GREY    = "\033[90m"

def c(text, *codes):
    return "".join(codes) + str(text) + C.RESET

# ─────────────────────────────────────────────
#  BANNER  —  WIFI-X
# ─────────────────────────────────────────────
def print_banner():
    os.system("clear")
    print(C.NEON)
    print("  ██╗    ██╗██╗███████╗██╗      ██╗  ██╗")
    print("  ██║    ██║██║██╔════╝██║      ╚██╗██╔╝")
    print("  ██║ █╗ ██║██║█████╗  ██║       ╚███╔╝ ")
    print("  ██║███╗██║██║██╔══╝  ██║       ██╔██╗ ")
    print("  ╚███╔███╔╝██║██║     ██║      ██╔╝ ██╗")
    print("   ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝      ╚═╝  ╚═╝")
    print("")
    print("           📡  WIFI-X TERMINAL SCANNER  📡")
    print(C.RESET)
    print(c("  " + "═" * 50, C.NEON))
    print(c("  Scans nearby WiFi · Signal · Band · Security", C.DIM + C.CYAN))
    print(c("  " + "═" * 50, C.NEON))
    print()

# ─────────────────────────────────────────────
#  SPINNER
# ─────────────────────────────────────────────
class Spinner:
    FRAMES = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    def __init__(self, msg="Scanning"):
        self.msg     = msg
        self._stop   = threading.Event()
        self._thread = threading.Thread(target=self._spin, daemon=True)

    def _spin(self):
        i = 0
        while not self._stop.is_set():
            frame = self.FRAMES[i % len(self.FRAMES)]
            sys.stdout.write(
                f"\r  {c(frame, C.NEON, C.BOLD)} "
                f"{c(self.msg + '...', C.DIM, C.WHITE)}"
            )
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1

    def start(self): self._thread.start()
    def stop(self):
        self._stop.set()
        self._thread.join()
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()

# ─────────────────────────────────────────────
#  SIGNAL STRENGTH BAR
# ─────────────────────────────────────────────
def signal_bar(level):
    try:
        lvl = int(level)
    except:
        return c("░░░░░", C.GREY), "Unknown"

    if lvl >= -50:
        bars, color, label = 5, C.GREEN,  "Excellent"
    elif lvl >= -60:
        bars, color, label = 4, C.GREEN,  "Good"
    elif lvl >= -70:
        bars, color, label = 3, C.YELLOW, "Fair"
    elif lvl >= -80:
        bars, color, label = 2, C.YELLOW, "Weak"
    else:
        bars, color, label = 1, C.RED,    "Poor"

    filled = c("█" * bars,       color, C.BOLD)
    empty  = c("░" * (5 - bars), C.GREY)
    return filled + empty, label

# ─────────────────────────────────────────────
#  SECURITY ICON
# ─────────────────────────────────────────────
def security_icon(flags):
    f = flags.upper()
    if "WPA3" in f:              return c("🔒 WPA3", C.GREEN, C.BOLD)
    elif "WPA2" in f:            return c("🔒 WPA2", C.GREEN)
    elif "WPA"  in f:            return c("🔑 WPA ", C.YELLOW)
    elif "WEP"  in f:            return c("⚠️  WEP ", C.RED)
    elif "ESS"  in f:            return c("🔓 OPEN ", C.RED, C.BOLD)
    else:                        return c("❓ ????", C.GREY)

# ─────────────────────────────────────────────
#  FREQUENCY → BAND
# ─────────────────────────────────────────────
def freq_band(freq):
    try:
        f = float(str(freq).replace("GHz","").replace("MHz",""))
        if f > 1000: f = f / 1000
        return c("5GHz", C.MAGENTA, C.BOLD) if f >= 5.0 else c("2.4G", C.CYAN)
    except:
        return c("????", C.GREY)

# ─────────────────────────────────────────────
#  SCAN — termux-wifi-scaninfo
# ─────────────────────────────────────────────
def scan_termux():
    import json
    result = subprocess.run(
        ["termux-wifi-scaninfo"],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    data = json.loads(result.stdout)
    networks = []
    for ap in data:
        networks.append({
            "ssid":  ap.get("ssid", "<hidden>") or "<hidden>",
            "bssid": ap.get("bssid", "??:??:??:??:??:??"),
            "level": str(ap.get("level", -100)),
            "freq":  str(ap.get("frequency", 0)),
            "flags": ap.get("capabilities", ""),
        })
    return networks

# ─────────────────────────────────────────────
#  SCAN — nmcli fallback
# ─────────────────────────────────────────────
def scan_nmcli():
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,BSSID,SIGNAL,FREQ,SECURITY", "dev", "wifi"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0: return None
        networks = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 4:
                networks.append({
                    "ssid":  parts[0] or "<hidden>",
                    "bssid": parts[1],
                    "level": str(int(parts[2]) - 100) if parts[2].isdigit() else "-70",
                    "freq":  parts[3],
                    "flags": parts[4] if len(parts) > 4 else "WPA2",
                })
        return networks if networks else None
    except FileNotFoundError:
        return None

# ─────────────────────────────────────────────
#  SCAN — iwlist fallback
# ─────────────────────────────────────────────
def scan_iwlist():
    for iface in ["wlan0","wlan1","wlp2s0"]:
        try:
            result = subprocess.run(
                ["iwlist", iface, "scan"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0 and "ESSID" in result.stdout:
                return parse_iwlist(result.stdout)
        except:
            continue
    return None

def parse_iwlist(output):
    networks = []
    for cell in output.split("Cell ")[1:]:
        ssid  = re.search(r'ESSID:"([^"]*)"', cell)
        bssid = re.search(r'Address: ([0-9A-Fa-f:]{17})', cell)
        level = re.search(r'Signal level=(-\d+)', cell)
        freq  = re.search(r'Frequency:(\S+)', cell)
        enc   = re.search(r'Encryption key:(on|off)', cell)
        wpa   = "WPA2" if "WPA2" in cell else ("WPA" if "WPA" in cell else "")
        flags = wpa if wpa else ("WEP" if enc and enc.group(1)=="on" else "ESS")
        networks.append({
            "ssid":  ssid.group(1)  if ssid  else "<hidden>",
            "bssid": bssid.group(1) if bssid else "??:??:??:??:??:??",
            "level": level.group(1) if level else "-100",
            "freq":  freq.group(1).split(" ")[0] if freq else "0",
            "flags": flags,
        })
    return networks

# ─────────────────────────────────────────────
#  DISPLAY RESULTS
# ─────────────────────────────────────────────
def display_networks(networks):
    networks.sort(key=lambda x: int(x.get("level", -100)), reverse=True)

    print(c("  " + "─" * 64, C.NEON))
    print(
        c("  #  ", C.GREY) +
        c(f"{'SSID':<22}", C.YELLOW, C.BOLD) +
        c(f"{'SIGNAL':<14}", C.WHITE) +
        c(f"{'BAND':<7}", C.WHITE) +
        c(f"{'SECURITY':<12}", C.WHITE) +
        c("BSSID", C.GREY)
    )
    print(c("  " + "─" * 64, C.NEON))

    for i, net in enumerate(networks, 1):
        ssid        = (net["ssid"] or "<hidden>")[:21]
        bar, _      = signal_bar(net["level"])
        band        = freq_band(net["freq"])
        sec         = security_icon(net["flags"])
        bssid       = c(net["bssid"], C.GREY)
        num         = c(f"  {i:<3}", C.GREY)
        db          = c(f"{net['level']}dBm", C.DIM + C.WHITE)
        print(f"{num}{c(f'{ssid:<22}', C.WHITE, C.BOLD)}{bar} {db:<5}  {band}  {sec}  {bssid}")

    print(c("  " + "─" * 64, C.NEON))
    print(c(f"\n  📡 Found {len(networks)} networks\n", C.CYAN, C.BOLD))

# ─────────────────────────────────────────────
#  HELP
# ─────────────────────────────────────────────
def print_help():
    print()
    print(c("  ┌─ Commands ──────────────────────────────┐", C.NEON))
    for cmd, desc in [
        ("/scan  or s", "Scan for WiFi networks"),
        ("/clear or c", "Clear screen & redraw banner"),
        ("/help  or h", "Show this help"),
        ("/exit  or q", "Quit WIFI-X"),
    ]:
        print(c("  │  ", C.NEON) + c(f"{cmd:<12}", C.YELLOW, C.BOLD) + c(f"  {desc}", C.WHITE))
    print(c("  └─────────────────────────────────────────┘", C.NEON))
    print()
    print(c("  💡 Tip: Install Termux:API for best results", C.DIM + C.CYAN))
    print(c("     pkg install termux-api", C.DIM + C.GREY))
    print()

# ─────────────────────────────────────────────
#  RUN SCAN
# ─────────────────────────────────────────────
def run_scan():
    spinner = Spinner("Scanning networks")
    spinner.start()
    networks, method = None, None

    for fn, name in [(scan_termux, "Termux:API"), (scan_nmcli, "nmcli"), (scan_iwlist, "iwlist")]:
        try:
            networks = fn()
            if networks:
                method = name
                break
        except:
            continue

    spinner.stop()

    if not networks:
        print(c("\n  ✖  No networks found or scanner not available.\n", C.RED))
        print(c("  Install Termux:API and grant location permission:\n", C.YELLOW))
        print(c("    pkg install termux-api", C.GREY))
        print(c("    termux-location  ← accept permission popup\n", C.GREY))
        return

    print(c(f"\n  ✔  Scan complete via {method}\n", C.GREEN))
    display_networks(networks)

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    print_banner()
    print(c("  Type /scan to start · /help for commands\n", C.DIM + C.WHITE))

    while True:
        try:
            user = input(c("  WIFI-X › ", C.NEON, C.BOLD)).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(c("\n\n  👋  Goodbye!\n", C.NEON, C.BOLD))
            break

        if not user: continue

        if   user in ("/scan",  "s", "scan"):  run_scan()
        elif user in ("/clear", "c", "clear"): print_banner()
        elif user in ("/help",  "h", "help"):  print_help()
        elif user in ("/exit",  "q", "exit","quit"):
            print(c("\n  👋  Goodbye!\n", C.NEON, C.BOLD)); break
        else:
            print(c(f"\n  Unknown command. Type /help\n", C.RED))

if __name__ == "__main__":
    main()
