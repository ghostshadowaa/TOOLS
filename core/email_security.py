import dns.exception
import dns.resolver

from core.security import normalize_domain


def _query(resolver, name, record_type):
    try:
        answer = resolver.resolve(name, record_type, raise_on_no_answer=False)
        if not answer.rrset:
            return []
        return [item.to_text().strip('"')[:512] for item in list(answer)[:20]]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return []
    except dns.exception.Timeout:
        return ["Consulta DNS expirou"]


def inspect_email_domain(value):
    domain = normalize_domain(value)
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 5

    mx_records = _query(resolver, domain, "MX")
    txt_records = _query(resolver, domain, "TXT")
    dmarc_records = _query(resolver, f"_dmarc.{domain}", "TXT")

    spf = [record for record in txt_records if record.lower().startswith("v=spf1")]
    dmarc = [record for record in dmarc_records if record.lower().startswith("v=dmarc1")]

    return {
        "domain": domain,
        "mx_records": mx_records,
        "spf": {
            "found": bool(spf),
            "records": spf,
            "multiple_records_warning": len(spf) > 1,
        },
        "dmarc": {
            "found": bool(dmarc),
            "records": dmarc,
        },
        "notes": [
            "Verifica somente a configuração pública do domínio.",
            "Não consulta endereços de e-mail, caixas postais ou contas de pessoas.",
            "DKIM depende do seletor configurado pelo administrador e não é adivinhado.",
        ],
    }
