"""Input validation helpers for public infrastructure lookups."""
from __future__ import annotations

import ipaddress
import re


class ValidationError(ValueError):
    """Raised when user input is not an acceptable public target."""


_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def normalize_domain(value: str) -> str:
    if not isinstance(value, str):
        raise ValidationError("Informe um domínio válido.")
    value = value.strip().rstrip(".")
    if not value or len(value) > 253 or "://" in value or "/" in value:
        raise ValidationError("Informe somente o domínio, sem URL ou caminho.")
    try:
        value = value.encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise ValidationError("Domínio inválido.") from exc
    if value in {"localhost"} or value.endswith((".local", ".internal", ".test", ".invalid", ".example", ".onion")):
        raise ValidationError("Domínios locais ou especiais não são aceitos.")
    try:
        ipaddress.ip_address(value)
    except ValueError:
        pass
    else:
        raise ValidationError("Informe um domínio, não um endereço IP.")
    labels = value.split(".")
    if len(labels) < 2 or any(not _LABEL.fullmatch(label) for label in labels):
        raise ValidationError("Formato de domínio inválido.")
    return value


def normalize_public_ip(value: str) -> str:
    if not isinstance(value, str):
        raise ValidationError("Informe um endereço IP válido.")
    try:
        address = ipaddress.ip_address(value.strip())
    except ValueError as exc:
        raise ValidationError("Endereço IP inválido.") from exc
    if not address.is_global:
        raise ValidationError("Somente endereços IP públicos são aceitos.")
    return str(address)
