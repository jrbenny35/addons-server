#!/bin/bash

cd addons-frontend
yarn
yarn amo &
sleep 30
STATIC_SERVER_PID=$!
