#!/bin/bash

cd addons-frontend
yarn install
yarn amo &
STATIC_SERVER_PID=$!
