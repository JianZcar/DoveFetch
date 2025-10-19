from flask import Flask, request, Response

authproxy = Flask(__name__)

UPSTREAM_PORTS = {
    "disroot.org": 10025,
}


@authproxy.route("/mail/auth", methods=["GET", "POST"])
def mail_auth():
    userid = request.headers.get("Auth-User")
    password = request.headers.get("Auth-Pass")

    if not userid or "@" not in userid:
        resp = Response(status=200)
        resp.headers["Auth-Status"] = "Invalid user"
        return resp

    domain = userid.split("@", 1)[1]

    local_port = UPSTREAM_PORTS.get(domain)
    if not local_port:
        resp = Response(status=200)
        resp.headers["Auth-Status"] = "Unknown domain"
        return resp

    resp = Response(status=200)
    resp.headers["Auth-Status"] = "OK"
    resp.headers["Auth-Server"] = "127.0.0.1"
    resp.headers["Auth-Port"] = str(local_port)
    resp.headers["Auth-User"] = userid
    resp.headers["Auth-Pass"] = password
    return resp


def run_authproxy():
    authproxy.run(host="0.0.0.0", port=8080, use_reloader=False)
