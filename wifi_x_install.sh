#!/data/data/com.termux/files/usr/bin/bash

CYAN="\e[1;36m"
GREEN="\e[1;32m"
YELLOW="\e[1;33m"
RESET="\e[0m"

clear
echo -e "${CYAN}"
echo "  ██╗    ██╗██╗███████╗██╗      ██╗  ██╗"
echo "  ██║    ██║██║██╔════╝██║      ╚██╗██╔╝"
echo "  ██║ █╗ ██║██║█████╗  ██║       ╚███╔╝ "
echo "  ██║███╗██║██║██╔══╝  ██║       ██╔██╗ "
echo "  ╚███╔███╔╝██║██║     ██║      ██╔╝ ██╗"
echo "   ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝      ╚═╝  ╚═╝"
echo ""
echo "           📡  WIFI-X TERMINAL SCANNER  📡"
echo -e "${RESET}"
echo -e "${CYAN}  ══════════════════════════════════════════════════${RESET}"
echo -e "${YELLOW}  Installing WIFI-X...${RESET}"
echo -e "${CYAN}  ══════════════════════════════════════════════════${RESET}"
echo ""

if ! command -v python3 &>/dev/null; then
    pkg install python -y
fi
echo -e "${GREEN}  ✔ Python: $(python3 --version)${RESET}"

pkg install termux-api -y
echo -e "${GREEN}  ✔ termux-api installed${RESET}"

chmod +x wifi_scanner.py
echo -e "${GREEN}  ✔ Made wifi_scanner.py executable${RESET}"

LAUNCHER="$PREFIX/bin/wifiscan"
cat > "$LAUNCHER" << LAUNCH
#!/data/data/com.termux/files/usr/bin/bash
python3 $(pwd)/wifi_scanner.py
LAUNCH
chmod +x "$LAUNCHER"
echo -e "${GREEN}  ✔ Launcher created: wifiscan${RESET}"

echo ""
echo -e "${CYAN}  ══════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}  ✅  WIFI-X installed successfully!${RESET}"
echo ""
echo -e "${YELLOW}  ⚠  Grant location permission when prompted!${RESET}"
echo ""
echo -e "  Run: ${GREEN}wifiscan${RESET}  (from anywhere)"
echo -e "${CYAN}  ══════════════════════════════════════════════════${RESET}"
