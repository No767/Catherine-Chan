#!/usr/bin/env bash

CATHERINE_FIRST_START_CHECK="CATHERINE_FIRST_START"

if [ ! -f $CATHERINE_FIRST_START_CHECK ]; then
    touch $CATHERINE_FIRST_START_CHECK
    echo 'DO NOT EDIT THIS FILE! THIS IS USED WHEN YOU FIRST RUN CATHERINE USING DOCKER!' >> $CATHERINE_FIRST_START_CHECK
    python3 /catherine/bot/migrations.py init
fi

exec python3 /catherine/bot/catherinebot.py