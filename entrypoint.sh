#!/bin/bash
set -e

envsubst < dovecot.conf.template | sudo tee /etc/dovecot/dovecot.conf > /dev/null
envsubst < users.template | sudo tee /etc/dovecot/users > /dev/null

touch /mail/dovecot.log

python /usr/local/bin/fetch-email.py &
sudo dovecot -F -c /etc/dovecot/dovecot.conf
