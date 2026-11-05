#!/usr/bin/env python3
"""Offline inventory and environment checks for Kali NetHunter."""
import ipaddress
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


def discover_private_lan(service_scan=False):
    executable = shutil.which("nmap")
    if not executable:
        print("Nmap não está instalado. Use a opção de instalação primeiro.")
        return

    value = input("Rede IPv4 privada em CIDR (ex.: 192.168.1.0/24): ").strip()
    try:
        network = ipaddress.ip_network(value, strict=False)
    except ValueError:
        print("CIDR inválido.")
        return

    if (
        network.version != 4
        or not network.is_private
        or network.is_loopback
        or network.is_link_local
        or network.is_multicast
        or network.is_reserved
        or network.num_addresses > 256
    ):
        print("Por segurança, informe uma rede IPv4 privada válida com até 256 endereços.")
        return

    confirm = input(
        f"Confirma que a rede {network} é sua ou você tem autorização para verificá-la? [s/N]: "
    ).strip().lower()
    if confirm != "s":
        print("Verificação cancelada.")
        return

    if service_scan:
        args = [executable, "-sT", "-sV", "--top-ports", "100", "-T3", str(network)]
        description = "inventário TCP dos 100 principais serviços (-sT -sV)"
        timeout = 180
    else:
        args = [executable, "-sn", str(network)]
        description = "descoberta de hosts (-sn)"
        timeout = 90

    print(f"\n[+] Nmap: {description} em {network}...")
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        print((result.stdout or result.stderr or "Nmap não retornou saída.")[:16000])
        print("Código de saída:", result.returncode)
    except subprocess.TimeoutExpired:
        print(f"A verificação excedeu o limite de {timeout} segundos.")
    except OSError as exc:
        print("Não foi possível iniciar o Nmap:", exc)


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
4 - Descobrir hosts (Nmap, rede privada)
5 - Inventariar serviços (Nmap, TCP)
0 - Sair
""")
        option = input("Escolha: ").strip()
        if option == "1":
            inventory()
        elif option == "2":
            system_info()
        elif option == "3":
            install_allowlist()
        elif option == "4":
            discover_private_lan()
        elif option == "5":
            discover_private_lan(service_scan=True)
        elif option == "0":
            break
        else:
            print("Opção inválida.")
        input("\nEnter para continuar...")


if __name__ == "__main__":
    main()
