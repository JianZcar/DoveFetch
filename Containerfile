FROM debian:stable-slim

RUN apt-get update && apt-get install -y \
    sudo dovecot-core dovecot-imapd dovecot-pop3d dovecot-sqlite \
    python3 python3-venv gettext-base less \
    && rm -rf /var/lib/apt/lists/*


RUN echo 'ALL ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

WORKDIR /mailservice

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dovecot/dovecot.conf.template ./

COPY src/ /src/

VOLUME ["/mail"]
EXPOSE 143 110

CMD ["python3", "/src/main.py"]
