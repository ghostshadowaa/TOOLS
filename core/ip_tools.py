import ipaddress
import socket

def inspect_ip(value):
    try:
        ip = ipaddress.ip_address((value or "").strip())
    except ValueError as exc:
        raise ValueError("Endereço IPv4 ou IPv6 inválido.") from exc
    result = {
        "ip": str(ip), "version": ip.version, "global": ip.is_global,
        "private": ip.is_private, "reserved": ip.is_reserved,
        "loopback": ip.is_loopback, "multicast": ip.is_multicast,
        "reverse_dns": None,
        "note": "Sem geolocalização. Nenhuma consulta de identidade é realizada."
    }
    if ip.is_global:
        try:
            result["reverse_dns"] = socket.gethostbyaddr(str(ip))[0]
        except (socket.herror, socket.gaierror, TimeoutError):
            result["reverse_dns"] = "PTR não disponível"
    return result
