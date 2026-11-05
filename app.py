import hmac
import os
import secrets
from functools import wraps

from flask import Flask, jsonify, render_template, request, session

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


def authenticated(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"ok": False, "error": "Faça login no painel primeiro."}), 401
        return view(*args, **kwargs)
    return wrapped


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
    return render_template("index.html", logged_in=bool(session.get("authenticated")),
                           login_configured=bool(os.environ.get("DASHBOARD_TOKEN")))


@app.get("/health")
def health():
    return jsonify({"status": "ok", "app": "Shadow Tools", "version": "0.2.0"})


@app.post("/login")
def login():
    expected = os.environ.get("DASHBOARD_TOKEN")
    supplied = request.form.get("token", "")
    if not expected:
        return render_template("index.html", logged_in=False, login_configured=False,
                               login_error="Configure DASHBOARD_TOKEN nas variáveis do Render.")
    if hmac.compare_digest(supplied, expected):
        session.clear()
        session["authenticated"] = True
        return render_template("index.html", logged_in=True, login_configured=True)
    return render_template("index.html", logged_in=False, login_configured=True,
                           login_error="Token incorreto."), 401


@app.post("/logout")
def logout():
    session.clear()
    return render_template("index.html", logged_in=False,
                           login_configured=bool(os.environ.get("DASHBOARD_TOKEN")))


@app.post("/api/dns")
@authenticated
def api_dns():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify({"ok": True, "result": lookup_dns(data.get("domain", ""))})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception:
        app.logger.exception("DNS lookup failed")
        return jsonify({"ok": False, "error": "Não foi possível concluir a consulta DNS."}), 502


@app.post("/api/ip")
@authenticated
def api_ip():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify({"ok": True, "result": inspect_ip(data.get("ip", ""))})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/web-check")
@authenticated
def api_web_check():
    data = request.get_json(silent=True) or {}
    try:
        return jsonify({"ok": True, "result": inspect_web(data.get("domain", ""))})
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except Exception:
        app.logger.exception("Web check failed")
        return jsonify({"ok": False, "error": "Falha na verificação. Confira o domínio e tente novamente."}), 502


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"ok": False, "error": "Requisição muito grande."}), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
