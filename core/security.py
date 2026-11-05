import ipaddress
import re

import dns.exception
import dns.resolver


def normalize_domain(value):
    if not isinstance(value, str):
        raise ValueError("Informe um domínio válido.")
    value = value.strip().rstrip(".")
    if not value or len(value) > 253 or any(c in value for c in "/\\@:#?"):
        raise ValueError("Informe um domínio válido, sem protocolo ou caminho.")
    try:
        name = value.encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise ValueError("Domínio inválido.") from exc

    if name == "localhost" or name.endswith(
        (".local", ".internal", ".test", ".invalid", ".example", ".onion")
    ):
        raise ValueError("Domínios locais ou especiais não são aceitos.")

    try:
        ipaddress.ip_address(name)
    except ValueError:
        pass
    else:
        raise ValueError("Informe um domínio, não um endereço IP.")

    labels = name.split(".")
    if len(labels) < 2 or any(
        not label
        or len(label) > 63
        or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label)
        for label in labels
    ):
        raise ValueError("Informe um domínio público válido, como example.com.")
    return name


def resolve_public_addresses(domain):
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 4
    addresses = []

    for record_type in ("A", "AAAA"):
        try:
            answer = resolver.resolve(domain, record_type)
            for item in list(answer)[:8]:
                parsed = ipaddress.ip_address(item.to_text())
                if not parsed.is_global:
                    raise ValueError(
                        "Consulta bloqueada: o domínio resolve para IP privado ou reservado."
                    )
                addresses.append(parsed)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            continue
        except dns.exception.Timeout as exc:
            raise ValueError("Tempo esgotado ao resolver o domínio.") from exc

    unique = {str(address): address for address in addresses}
    if not unique:
        raise ValueError("O domínio não resolveu para um endereço IP público.")
    return [unique[key] for key in sorted(unique)]
