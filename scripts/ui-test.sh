#!/bin/sh
echo 127.0.0.1 olympia.dev | tee -a /etc/hosts
export DISPLAY=:99
docker-compose exec web pip install tox
docker-compose exec web tox -e ui-tests-1
