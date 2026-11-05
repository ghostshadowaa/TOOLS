#!/usr/bin/env python3
"""Offline inventory and environment checks for Kali NetHunter."""
import os
import platform
import shutil
import subprocess

TOOLS = {
    "Nmap": "nmap",
    "Metasploit": "msfconsole",
    "SQLMap": "sqlmap",
    "Whois": "whois",
    "DNS utilities": "dig",
    "cURL": "curl",
    "Wget": "wget",
    "Git": "git",
    "OpenSSL": "openssl",
    "Traceroute": "traceroute",
    "TCPDump": "tcpdump",
    "Netcat": "nc",
    "Python": "python3",
    "JQ": "jq",
}


def inventory():
    print("\n=== FERRAMENTAS DETECTADAS ===")
    for label, executable in TOOLS.items():
        path = shutil.which(executable)
        status = f"[OK] {path}" if path else "[--] não encontrada"
        print(f"{label:18} {status}")


def system_info():
    print("\n=== AMBIENTE ===")
    print("Sistema:", platform.platform())
    print("Arquitetura:", platform.machine())
    print("Usuário:", os.getenv("USER", "desconhecido"))
    print("UID:", os.getuid() if hasattr(os, "getuid") else "indisponível")
    print("Root do ambiente:", "sim" if hasattr(os, "geteuid") and os.geteuid() == 0 else "não")
    print("Observação: root dentro do PRoot não equivale a root real do Android.")


def install_allowlist():
    packages = [
        "nmap", "whois", "dnsutils", "curl", "wget", "git",
        "openssl", "traceroute", "tcpdump", "netcat-openbsd",
        "python3", "python3-pip", "jq",
    ]
    print("\nEste instalador usa apt e instala apenas ferramentas de diagnóstico.")
    print("Metasploit e SQLMap serão apenas detectados se já estiverem instalados.")
    answer = input("Deseja instalar/atualizar a lista permitida? [s/N]: ").strip().lower()
    if answer != "s":
        print("Instalação cancelada.")
        return
    if not shutil.which("apt-get"):
        print("apt-get não encontrado. Execute este script dentro do Kali NetHunter.")
        return
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        print("Permissão insuficiente. Entre como root do container NetHunter e tente novamente.")
        print("Isso não concede root real ao Android.")
        return
    subprocess.run(["apt-get", "update"], check=False)
    subprocess.run(["apt-get", "install", "-y", *packages], check=False)


def main():
    while True:
        print("""
===============================
       SHADOW TOOLS OFFLINE
         KALI NETHUNTER
===============================
1 - Detectar ferramentas
2 - Informações do ambiente
3 - Instalar ferramentas permitidas
0 - Sair
""")
        option = input("Escolha: ").strip()
        if option == "1":
            inventory()
        elif option == "2":
            system_info()
        elif option == "3":
            install_allowlist()
        elif option == "0":
            break
        else:
            print("Opção inválida.")
        input("\nEnter para continuar...")


if __name__ == "__main__":
    main()
