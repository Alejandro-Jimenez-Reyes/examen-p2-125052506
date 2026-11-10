#!/bin/bash
set -e
mkdir -p /run/sshd /root/.ssh /keys

# Genera el par de llaves una sola vez; queda en el volumen compartido "sshkeys"
if [ ! -f /keys/id_rsa ]; then
  ssh-keygen -t rsa -b 4096 -N "" -f /keys/id_rsa -q
fi

cp /keys/id_rsa     /root/.ssh/id_rsa
cp /keys/id_rsa.pub /root/.ssh/id_rsa.pub
cp /keys/id_rsa.pub /root/.ssh/authorized_keys
chmod 700 /root/.ssh
chmod 600 /root/.ssh/id_rsa /root/.ssh/authorized_keys

exec /usr/sbin/sshd -D