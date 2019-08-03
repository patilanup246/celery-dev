#!/usr/bin/env bash

celery worker -A xde.app:app -c 1 -Ofair --without-gossip -l INFO
