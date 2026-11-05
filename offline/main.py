#!/usr/bin/env python3
import os
import platform
from tool_registry import inventory

def pause():
    input("\\nEnter para voltar...")

def show_inventory():
    os.system("clear")
    print("SHADOW TOOLS | NETHUNTER OFFLINE")
    print("=" * 48)
    grouped = {}
    for item in inventory():
        grouped.setdefault(item["category"], []).append(item)
    for category, tools in grouped.items():
        print(f"\\n[{category}]")
        for item in tools:
            state = "OK" if item["installed"] else "NÃO INSTALADO"
            print(f"  [{state}] {item['executable']:<14} {item['description']}")
            if item["path"]:
                print(f"       {item['path']}")
    pause()

def system_info():
    os.system("clear")
    print("SISTEMA")
    print("=" * 48)
    print("Sistema:", platform.system())
    print("Versão:", platform.release())
    print("Arquitetura:", platform.machine())
    print("Python:", platform.python_version())
    uid = os.geteuid() if hasattr(os, "geteuid") else "indisponível"
    print("UID efetivo:", uid)
    print("Root neste ambiente:", "sim" if uid == 0 else "não")
    print("\\nRoot em PRoot não equivale a root real do Android.")
    pause()

def main():
    while True:
        os.system("clear")
        print("========================================")
        print("             SHADOW TOOLS")
        print("          NETHUNTER OFFLINE")
        print("========================================")
        print("\\n1 - Inventário de ferramentas")
        print("2 - Informações do sistema")
        print("3 - Sobre o projeto")
        print("0 - Sair")
        choice = input("\\nEscolha: ").strip()
        if choice == "1":
            show_inventory()
        elif choice == "2":
            system_info()
        elif choice == "3":
            os.system("clear")
            print("O modo offline lista ferramentas instaladas.")
            print("Metasploit e SQLMap são detectados, mas não iniciados")
            print("automaticamente pelo painel.")
            pause()
        elif choice == "0":
            break
        else:
            input("Opção inválida. Enter...")

if __name__ == "__main__":
    main()
