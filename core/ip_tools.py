import ipaddress

import dns.exception
import dns.reversename
import dns.resolver


def inspect_ip(value):
    try:
        ip = ipaddress.ip_address((value or "").strip())
    except ValueError as exc:
        raise ValueError("Endereço IPv4 ou IPv6 inválido.") from exc

    result = {
        "ip": str(ip),
        "version": ip.version,
        "global": ip.is_global,
        "private": ip.is_private,
        "reserved": ip.is_reserved,
        "loopback": ip.is_loopback,
        "multicast": ip.is_multicast,
        "reverse_dns": None,
        "note": "Sem geolocalização. Nenhuma consulta de identidade é realizada.",
    }

    if ip.is_global:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 2
        resolver.lifetime = 3
        try:
            answer = resolver.resolve(dns.reversename.from_address(str(ip)), "PTR")
            result["reverse_dns"] = [item.to_text().rstrip(".") for item in list(answer)[:5]]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            result["reverse_dns"] = "PTR não disponível"
        except dns.exception.Timeout:
            result["reverse_dns"] = "Consulta PTR expirou"

    return result
