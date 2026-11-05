import re
import socket
import ipaddress

def normalize_domain(value):
    value = (value or "").strip().rstrip(".")
    if not value or len(value) > 253 or any(c in value for c in "/\\@:#?"):
        raise ValueError("Informe um domínio válido, sem protocolo ou caminho.")
    try:
        name = value.encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise ValueError("Domínio inválido.") from exc
    labels = name.split(".")
    if len(labels) < 2 or any(not label or len(label) > 63 or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label) for label in labels):
        raise ValueError("Informe um domínio público válido, como example.com.")
    return name

def resolve_public_addresses(domain):
    try:
        rows = socket.getaddrinfo(domain, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError("O domínio não resolveu para um endereço IP.") from exc
    addresses = sorted({row[4][0] for row in rows})
    if not addresses:
        raise ValueError("Nenhum endereço IP encontrado.")
    parsed = [ipaddress.ip_address(address) for address in addresses]
    if any(not ip.is_global for ip in parsed):
        raise ValueError("Consulta bloqueada: o domínio resolve para IP privado ou reservado.")
    return parsed
