#!/bin/bash

cd addons-frontend
npm install
yarn amo &
STATIC_SERVER_PID=$!
