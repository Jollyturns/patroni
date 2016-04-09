#!/bin/bash

echo Current user: `whoami`

# echo Changing ownership
# chown -R postgres:postgres /var/lib/postgresql

nslookup etcd0

nslookup patroni-postgres

# echo Password is: $POSTGRES_PASSWORD

echo Contents of /var/lib/postgresql/:
ls -alF /var/lib/postgresql/

echo Contents of /var/lib/postgresql/data:
ls -alF /var/lib/postgresql/data

echo Contents of /usr/lib/postgresql/9.5/bin/:
ls -alF /usr/lib/postgresql/9.5/bin/

echo Contents of /var/lib/postgresql/data/global:
ls -alF /var/lib/postgresql/data/global

exec python -u /patroni.py
