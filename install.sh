#!/usr/bin/env bash
set -euo pipefail

if ! command -v apt-get >/dev/null 2>&1; then
  echo "[!] Execute este instalador dentro do Kali NetHunter/Debian."
  exit 1
fi

echo "[+] Instalando dependências Python do Shadow Tools..."
if [ "$(id -u)" -ne 0 ]; then
  echo "[!] Este instalador precisa de permissões de administrador dentro do Kali."
  echo "    Em um NetHunter PRoot, entre com nethunter -r se disponível."
  exit 1
fi

apt-get update
apt-get install -y python3 python3-venv python3-pip git

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo
echo "[+] Instalação concluída."
echo "Online: gunicorn app:app"
echo "Offline: python3 offline.py"
