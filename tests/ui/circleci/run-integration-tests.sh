#!/bin/bash

cd addons-server
npm install
yarn amo &
STATIC_SERVER_PID=$!
