#!/bin/bash

cd addons-frontend
yarn
yarn amo &
STATIC_SERVER_PID=$!
