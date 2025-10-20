FROM debian:stable-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    acl tzdata less curl swaks \
    dovecot-core dovecot-imapd dovecot-pop3d dovecot-sqlite \
    stunnel4 nginx libnginx-mod-mail \
    python3 python3-venv gettext-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /mailservice

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY certs/dovefetch.crt /etc/ssl/certs/dovefetch.crt
COPY certs/dovefetch.key  /etc/ssl/private/dovefetch.key

COPY dovecot/dovecot.conf /etc/dovecot/dovecot.conf
COPY stunnel/stunnel.conf /etc/stunnel/stunnel.conf
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY src/ /src/

RUN rm -f /etc/nginx/sites-enabled/default || true

EXPOSE 143 993 25 465

VOLUME ["/mail"]

CMD ["python3", "/src/main.py"]
