import dns.resolver
import dns.exception
from core.security import normalize_domain

def lookup_dns(value):
    domain = normalize_domain(value)
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 5
    result = {"domain": domain, "resolver": "resolvedor configurado no servidor", "records": {}}
    for kind in ("A", "AAAA", "MX", "NS", "TXT"):
        values = []
        try:
            answer = resolver.resolve(domain, kind, raise_on_no_answer=False)
            if answer.rrset:
                values = [item.to_text() for item in answer]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            pass
        except dns.resolver.NoNameservers:
            values = ["Nenhum nameserver respondeu."]
        except dns.exception.Timeout:
            values = ["Tempo limite da consulta."]
        result["records"][kind] = values
    return result
