import hmac
import os
import secrets
from functools import wraps

from flask import Flask, jsonify, render_template, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from core.dns_tools import lookup_dns
from core.ip_tools import inspect_ip
from core.web_checks import inspect_web

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("APP_SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "1") == "1",
    MAX_CONTENT_LENGTH=16 * 1024,
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["120 per hour"],
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
)


def csrf_value():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


@app.before_request
def protect_post_requests():
    if request.method != "POST":
        return None
    expected = session.get("csrf_token", "")
    supplied = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
    if not expected or not supplied or not hmac.compare_digest(expected, supplied):
        return jsonify({"ok": False, "error": "Token de segurança inválido. Atualize a página."}), 400
    return None


def authenticated(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"ok": False, "error": "Faça login no painel primeiro."}), 401
        return view(*args, **kwargs)
    return wrapped


def read_string(data, key, label):
    value = data.get(key) if isinstance(data, dict) else None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Informe {label}.")
    value = value.strip()
    if len(value) > 253:
        raise ValueError("Entrada muito longa.")
    return value


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'; "
        "img-src 'self' data:; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
    )
    return response


@app.get("/")
def index():
    return render_template(
        "index.html",
        logged_in=bool(session.get("authenticated")),
        login_configured=bool(os.environ.get("DASHBOARD_TOKEN")),
        csrf_token=csrf_value(),
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok", "app": "Shadow Tools", "version": "0.3.0"})


@app.post("/login")
@limiter.limit("5 per minute")
def login():
    expected = os.environ.get("DASHBOARD_TOKEN")
    supplied = request.form.get("token", "")
    if not expected:
        return render_template(
            "index.html", logged_in=False, login_configured=False,
            login_error="Configure DASHBOARD_TOKEN nas variáveis do Render.",
            csrf_token=csrf_value(),
        ), 503
    if hmac.compare_digest(supplied, expected):
        session.clear()
        session["authenticated"] = True
        token = csrf_value()
        return render_template(
            "index.html", logged_in=True, login_configured=True, csrf_token=token
        )
    return render_template(
        "index.html", logged_in=False, login_configured=True,
        login_error="Token incorreto.", csrf_token=csrf_value(),
    ), 401


@app.post("/logout")
@authenticated
def logout():
    session.clear()
    return render_template(
        "index.html", logged_in=False,
        login_configured=bool(os.environ.get("DASHBOARD_TOKEN")),
        csrf_token=csrf_value(),
    )


@app.post("/api/dns")
@limiter.limit("12 per minute")
@authenticated
def api_dns():
    data = request.get_json(silent=True) or {}
    try:
        domain = read_string(data, "domain", "um domínio")
        return jsonify({"ok": True, "result": lookup_dns(domain)})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception:
        app.logger.exception("DNS lookup failed")
        return jsonify({"ok": False, "error": "Não foi possível concluir a consulta DNS."}), 502


@app.post("/api/ip")
@limiter.limit("12 per minute")
@authenticated
def api_ip():
    data = request.get_json(silent=True) or {}
    try:
        address = read_string(data, "ip", "um endereço IP")
        return jsonify({"ok": True, "result": inspect_ip(address)})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception:
        app.logger.exception("IP inspection failed")
        return jsonify({"ok": False, "error": "Não foi possível inspecionar esse IP."}), 502


@app.post("/api/web-check")
@limiter.limit("5 per minute")
@authenticated
def api_web_check():
    data = request.get_json(silent=True) or {}
    try:
        domain = read_string(data, "domain", "um domínio")
        return jsonify({"ok": True, "result": inspect_web(domain)})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception:
        app.logger.exception("Web check failed")
        return jsonify({"ok": False, "error": "Falha na verificação. Confira o domínio e tente novamente."}), 502


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"ok": False, "error": "Requisição muito grande."}), 413


@app.errorhandler(429)
def rate_limited(_error):
    return jsonify({"ok": False, "error": "Limite de consultas atingido. Aguarde antes de tentar novamente."}), 429


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
