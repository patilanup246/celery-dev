#!/usr/bin/env bash

celery worker -A xde.app:app -c 1 -Q celery,chain -Ofair --without-gossip -l INFO
