"""
Custom Google OAuth handler using a local HTTP callback server.
Bypasses Flet's broken built-in OAuth popup entirely.
"""
import os
import threading
import urllib.parse
import urllib.request
import json
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler

# Load .env file from project root
from pathlib import Path
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _key, _val = _line.split("=", 1)
                os.environ.setdefault(_key.strip(), _val.strip())

# Google OAuth Configuration Parameters
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = "http://localhost:8551/callback"
SCOPES = "openid email profile"

AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v3/userinfo"

# State Management
_auth_result = {}   # Authenticated user metadata cache
_auth_lock = threading.Lock()
_valid_states = set()  # Cross-Site Request Forgery (CSRF) protection tokens


def get_auth_url(mode="signup"):
    """Generate Google OAuth consent dialog URL."""
    state_token = secrets.token_urlsafe(16)
    _valid_states.add(state_token)

    # Keep only the last 20 states to prevent memory leak
    if len(_valid_states) > 20:
        _valid_states.clear()
        _valid_states.add(state_token)

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "select_account",
        "state": f"{mode}:{state_token}",
    }
    return f"{AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"


def get_auth_result():
    """Retrieve the most recent authentication payload."""
    with _auth_lock:
        return _auth_result.copy() if _auth_result else None


def clear_auth_result():
    """Purge stored authentication payload from memory."""
    global _auth_result
    with _auth_lock:
        _auth_result.clear()


# Token Exchange and Profile Retrieval

def _exchange_code_for_tokens(code):
    """Exchange OAuth authorization code for authentication tokens."""
    data = urllib.parse.urlencode({
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()

    req = urllib.request.Request(TOKEN_ENDPOINT, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def _fetch_user_info(access_token):
    """Retrieve user profile metadata from Google."""
    req = urllib.request.Request(USERINFO_ENDPOINT)
    req.add_header("Authorization", f"Bearer {access_token}")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


# HTTP Redirect Callback Handler

SUCCESS_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>PharmaOps - Authentication Successful</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh;
            background: #f0fdfa;
            color: #0d9488;
        }
        .card {
            background: white;
            border-radius: 24px;
            padding: 56px 64px;
            text-align: center;
            max-width: 460px;
            box-shadow: 0 20px 40px rgba(13, 148, 136, 0.1);
            animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .icon-container {
            width: 88px; height: 88px;
            border-radius: 50%;
            background: #ccfbf1;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 24px;
            animation: scaleIn 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s both;
        }
        @keyframes scaleIn {
            from { transform: scale(0); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        .icon-container svg {
            width: 44px; height: 44px;
            stroke: #0f766e; stroke-width: 3;
            fill: none; stroke-linecap: round; stroke-linejoin: round;
        }
        h2 { font-size: 28px; font-weight: 700; color: #115e59; margin-bottom: 12px; letter-spacing: -0.5px; }
        p { font-size: 16px; color: #475569; line-height: 1.6; }
        .hint {
            margin-top: 32px; font-size: 13px; color: #94a3b8; font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="icon-container">
            <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>
        </div>
        <h2>Success!</h2>
        <p>Your authentication is complete.<br>You can safely close this window to return to PharmaOps.</p>
        <p class="hint">Attempting to close window automatically...</p>
    </div>
    <script>
        setTimeout(function(){ window.close(); }, 3000);
    </script>
</body>
</html>"""

ERROR_HTML = """<!DOCTYPE html>
<html>
<head><title>PharmaOps - Auth Error</title>
<style>
    body {{ font-family: 'Inter', system-ui, sans-serif;
           display:flex; justify-content:center; align-items:center;
           min-height:100vh; margin:0; background:#fef2f2; color:#b91c1c; }}
    .card {{ background:white; border-radius:24px; padding:48px; 
             text-align:center; max-width:440px; box-shadow:0 20px 40px rgba(185,28,28,0.1); }}
    h2 {{ margin:0 0 12px; font-size:24px; color:#991b1b; }} 
    p {{ opacity:0.85; line-height:1.6; color:#7f1d1d; }}
</style></head>
<body><div class="card"><h2>Authentication Failed</h2><p>{error}</p></div></body>
</html>"""


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Processes the OAuth /callback routing."""

    def do_GET(self):
        global _auth_result, _valid_states

        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/callback":
            self.send_response(404)
            self.end_headers()
            return

        params = urllib.parse.parse_qs(parsed.query)

        # Validate OAuth response payload
        if "error" in params:
            self._send_html(400, ERROR_HTML.format(error=params["error"][0]))
            return

        code = params.get("code", [None])[0]
        state = params.get("state", [""])[0]

        # Validate CSRF anti-forgery token
        parts = state.split(":", 1)
        mode = parts[0] if parts else "login"
        token = parts[1] if len(parts) > 1 else ""

        if token not in _valid_states:
            self._send_html(400, ERROR_HTML.format(error="Invalid state parameter. Please try again."))
            return
            
        _valid_states.discard(token)

        try:
            # Redeem authorization code
            tokens = _exchange_code_for_tokens(code)
            access_token = tokens.get("access_token")
            if not access_token:
                raise Exception("No access token in response")

            # Retrieve user metadata
            user_info = _fetch_user_info(access_token)

            # Cache authentication payload for client retrieval
            with _auth_lock:
                _auth_result.clear()
                _auth_result.update({
                    "email": user_info.get("email", ""),
                    "name": user_info.get("name", "Google User"),
                    "given_name": user_info.get("given_name", ""),
                    "family_name": user_info.get("family_name", ""),
                    "picture": user_info.get("picture", ""),
                    "mode": mode,
                })

            self._send_html(200, SUCCESS_HTML)

        except Exception as ex:
            self._send_html(500, ERROR_HTML.format(error=str(ex)))

    def _send_html(self, status, html):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        # Suppress default HTTP request logging
        pass


# Local Server Initialization

_server_started = False

def start_callback_server(port=8551):
    """Initialize the OAuth callback listener daemon."""
    global _server_started
    if _server_started:
        return
    _server_started = True

    def _run():
        try:
            server = HTTPServer(("localhost", port), OAuthCallbackHandler)
            server.serve_forever()
        except OSError as e:
            pass

    t = threading.Thread(target=_run, daemon=True)
    t.START()


