"""Read-only lookups for public network infrastructure."""
from __future__ import annotations

import http.client
import ipaddress
import json
import socket
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone

import dns.resolver

from .validation import normalize_domain, normalize_public_ip, ValidationError

USER_AGENT = "ShadowTools/0.2 (+https://github.com/ghostshadowaa/TOOLS)"
MAX_RDAP_BYTES = 512_000


def _resolve_public_addresses(domain: str) -> list[str]:
    addresses: list[str] = []
    for record_type in ("A", "AAAA"):
        try:
            answers = dns.resolver.resolve(domain, record_type, lifetime=5)
            for answer in answers:
                ip = ipaddress.ip_address(answer.to_text())
                if not ip.is_global:
                    raise ValidationError("O domínio resolve para endereço não público; consulta bloqueada.")
                addresses.append(str(ip))
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            continue
        except dns.exception.Timeout as exc:
            raise ValidationError("Tempo esgotado ao consultar DNS.") from exc
    if not addresses:
        raise ValidationError("Não foi encontrado endereço A ou AAAA público para esse domínio.")
    return list(dict.fromkeys(addresses))


def domain_dns(value: str) -> dict:
    domain = normalize_domain(value)
    result = {"domain": domain, "records": {}, "resolved_addresses": []}
    for record_type in ("A", "AAAA", "MX", "NS", "TXT", "CAA"):
        try:
            answers = dns.resolver.resolve(domain, record_type, lifetime=5)
            values = [answer.to_text().strip('"') for answer in answers]
            result["records"][record_type] = values[:20]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            result["records"][record_type] = []
        except dns.exception.Timeout:
            result["records"][record_type] = ["Consulta DNS expirou"]
    try:
        result["resolved_addresses"] = _resolve_public_addresses(domain)
    except ValidationError as exc:
        result["warning"] = str(exc)
    return result


def ip_rdap(value: str) -> dict:
    address = normalize_public_ip(value)
    request = urllib.request.Request(
        f"https://rdap.org/ip/{address}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/rdap+json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            raw = response.read(MAX_RDAP_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ValidationError("Não foi possível consultar o serviço RDAP agora.") from exc
    if len(raw) > MAX_RDAP_BYTES:
        raise ValidationError("Resposta RDAP excedeu o limite permitido.")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValidationError("O serviço RDAP retornou uma resposta inválida.") from exc
    # Deliberately omit entity/contact data to avoid exposing personal contact details.
    return {
        "ip": address,
        "name": data.get("name"),
        "handle": data.get("handle"),
        "type": data.get("type"),
        "startAddress": data.get("startAddress"),
        "endAddress": data.get("endAddress"),
        "country": data.get("country"),
        "port43": data.get("port43"),
        "events": [
            {"eventAction": item.get("eventAction"), "eventDate": item.get("eventDate")}
            for item in data.get("events", [])[:8]
            if isinstance(item, dict)
        ],
        "source": "RDAP (rdap.org)",
        "note": "Dados técnicos de alocação; contatos e dados pessoais foram omitidos.",
    }


def website_security(value: str) -> dict:
    domain = normalize_domain(value)
    addresses = _resolve_public_addresses(domain)
    # Connect to a validated resolved IP directly, avoiding a second hostname lookup.
    address = next((item for item in addresses if ipaddress.ip_address(item).version == 4), addresses[0])
    raw_socket = socket.create_connection((address, 443), timeout=7)
    context = ssl.create_default_context()
    try:
        tls_socket = context.wrap_socket(raw_socket, server_hostname=domain)
        cert = tls_socket.getpeercert()
        request = (
            f"GET / HTTP/1.1\r\nHost: {domain}\r\n"
            f"User-Agent: {USER_AGENT}\r\nConnection: close\r\n\r\n"
        ).encode("ascii")
        tls_socket.sendall(request)
        response = http.client.HTTPResponse(tls_socket)
        response.begin()
        headers = {key.lower(): value for key, value in response.getheaders()}
        status = response.status
        response.close()
        not_after = cert.get("notAfter")
        expiry = None
        if not_after:
            parsed = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            expiry = parsed.isoformat()
        wanted = (
            "strict-transport-security",
            "content-security-policy",
            "x-content-type-options",
            "x-frame-options",
            "referrer-policy",
            "permissions-policy",
        )
        security_headers = {name: headers.get(name) for name in wanted}
        return {
            "domain": domain,
            "address_used": address,
            "https_status": status,
            "server_header": headers.get("server"),
            "security_headers": security_headers,
            "missing_security_headers": [name for name, value in security_headers.items() if not value],
            "tls": {
                "verified": True,
                "subject": cert.get("subject"),
                "issuer": cert.get("issuer"),
                "expires_at": expiry,
            },
            "note": "Consulta somente HTTPS na porta 443; redirecionamentos não são seguidos.",
        }
    except (ssl.SSLError, socket.timeout, OSError, http.client.HTTPException) as exc:
        raise ValidationError("Falha ao conectar ou validar TLS para esse domínio.") from exc
    finally:
        try:
            raw_socket.close()
        except OSError:
            pass
