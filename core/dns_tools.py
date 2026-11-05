import dns.exception
import dns.resolver

from core.security import normalize_domain


def lookup_dns(value):
    domain = normalize_domain(value)
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 5
    result = {
        "domain": domain,
        "resolver": "resolvedor configurado no servidor",
        "records": {},
        "note": "Somente registros DNS públicos; valores limitados para evitar respostas excessivas.",
    }
    for kind in ("A", "AAAA", "MX", "NS", "TXT", "CAA"):
        values = []
        try:
            answer = resolver.resolve(domain, kind, raise_on_no_answer=False)
            if answer.rrset:
                values = [item.to_text()[:512] for item in list(answer)[:20]]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            pass
        except dns.resolver.NoNameservers:
            values = ["Nenhum nameserver respondeu."]
        except dns.exception.Timeout:
            values = ["Tempo limite da consulta."]
        result["records"][kind] = values
    return result
