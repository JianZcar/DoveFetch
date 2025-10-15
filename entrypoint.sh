#!/bin/bash
set -e

mkdir -p /mail/config

envsubst < dovecot.conf.template > /mail/config/dovecot.conf
envsubst < users.template > /mail/config/users

python /usr/local/bin/fetch-email.py &
sudo dovecot -F -c /mail/config/dovecot.conf
