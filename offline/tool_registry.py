import shutil

TOOLS = {
    "nmap": ("Rede", "Inventário e diagnóstico de rede"),
    "msfconsole": ("Framework", "Metasploit instalado; detecção apenas"),
    "sqlmap": ("Web", "SQLMap instalado; detecção apenas"),
    "whois": ("OSINT técnico", "Consulta de registro de domínio"),
    "dig": ("DNS", "Consultas DNS"),
    "curl": ("Web", "Cliente HTTP"),
    "wget": ("Web", "Download HTTP/HTTPS"),
    "tcpdump": ("Rede", "Analisador de tráfego; pode exigir privilégios"),
    "traceroute": ("Rede", "Diagnóstico de rota"),
    "ip": ("Sistema", "Configuração de rede"),
    "ss": ("Sistema", "Sockets locais"),
    "git": ("Desenvolvimento", "Controle de versão"),
    "python3": ("Desenvolvimento", "Interpretador Python"),
}

def inventory():
    rows = []
    for executable, (category, description) in TOOLS.items():
        path = shutil.which(executable)
        rows.append({"executable": executable, "path": path,
                     "installed": path is not None, "category": category,
                     "description": description})
    return rows
