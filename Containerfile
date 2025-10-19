FROM debian:stable-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    sudo less curl swaks \
    dovecot-core dovecot-imapd dovecot-pop3d dovecot-sqlite \
    stunnel4 nginx libnginx-mod-mail \
    python3 python3-venv gettext-base \
    && rm -rf /var/lib/apt/lists/*


RUN echo 'ALL ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /mailservice

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dovecot/dovecot.conf.template ./
COPY stunnel/stunnel.conf /etc/stunnel/stunnel.conf
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY src/ /src/

RUN rm -f /etc/nginx/sites-enabled/default || true

EXPOSE 143 110 8080

VOLUME ["/mail"]

CMD ["python3", "/src/main.py"]
