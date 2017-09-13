#!/bin/sh
echo 127.0.0.1 olympia.dev | tee -a /etc/hosts
export DISPLAY=:99
docker-compose exec web pip install tox
docker-compose exec web yum -y install curl
curl https://raw.githubusercontent.com/creationix/nvm/v0.30.2/install.sh > install-nvm.sh
docker-compose exec web bash /code/install-nvm.sh
docker-compose exec web nvm install node_modules
docker-compose exec web EXEC $SHELL
docker-compose exec web tox -e ui-tests-1
