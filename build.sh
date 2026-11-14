#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt
python EsyConnect_Haiti_AM/manage.py collectstatic --noinput
python EsyConnect_Haiti_AM/manage.py migrate

