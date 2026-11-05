import socket
import ssl
from core.security import normalize_domain, resolve_public_addresses

SECURITY_HEADERS = ("strict-transport-security", "content-security-policy",
                    "x-content-type-options", "x-frame-options",
                    "referrer-policy", "permissions-policy")

def inspect_web(value):
    domain = normalize_domain(value)
    addresses = resolve_public_addresses(domain)
    context = ssl.create_default_context()
    last_error = None
    for ip in addresses:
        raw = wrapped = None
        try:
            raw = socket.create_connection((str(ip), 443), timeout=5)
            wrapped = context.wrap_socket(raw, server_hostname=domain)
            cert = wrapped.getpeercert()
            request = (f"HEAD / HTTP/1.1\r\nHost: {domain}\r\n"
                       "User-Agent: ShadowTools-DefensiveCheck/0.2\r\n"
                       "Connection: close\r\n\r\n")
            wrapped.sendall(request.encode("ascii"))
            response = b""
            while b"\r\n\r\n" not in response and len(response) < 16384:
                chunk = wrapped.recv(2048)
                if not chunk:
                    break
                response += chunk
            block = response.split(b"\r\n\r\n", 1)[0].decode("iso-8859-1", "replace")
            lines = block.split("\r\n")
            headers = {}
            for line in lines[1:]:
                if ":" in line:
                    key, val = line.split(":", 1)
                    headers[key.strip().lower()] = val.strip()
            return {
                "domain": domain, "connected_ip": str(ip), "https": True,
                "tls_version": wrapped.version(),
                "certificate_subject": dict(x[0] for x in cert.get("subject", [])),
                "certificate_issuer": dict(x[0] for x in cert.get("issuer", [])),
                "certificate_not_after": cert.get("notAfter"),
                "http_status_line": lines[0] if lines else "Resposta HTTP não reconhecida.",
                "security_headers": {key: headers.get(key) for key in SECURITY_HEADERS},
                "missing_security_headers": [key for key in SECURITY_HEADERS if key not in headers],
                "redirects_followed": False,
                "note": "Somente HEAD na porta 443; não segue redirecionamentos nem executa conteúdo."
            }
        except (OSError, ssl.SSLError) as exc:
            last_error = str(exc)
        finally:
            if wrapped:
                wrapped.close()
            elif raw:
                raw.close()
    raise ValueError("Não foi possível conectar: " + (last_error or "erro desconhecido"))
