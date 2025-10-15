FROM debian:stable-slim

RUN apt-get update && apt-get install -y \
    sudo dovecot-core dovecot-imapd dovecot-pop3d \
    python3 python3-venv gettext-base \
    && rm -rf /var/lib/apt/lists/*


RUN echo 'ALL ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /etc/dovecot

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir imapclient

COPY dovecot.conf.template users.template ./
COPY fetch-email.py /usr/local/bin/fetch-email.py
COPY entrypoint.sh /

VOLUME ["/mail"]
EXPOSE 143 110

CMD ["/entrypoint.sh"]
