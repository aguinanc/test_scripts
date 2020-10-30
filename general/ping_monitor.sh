#!/usr/bin/env bash

while true;
do
  ping -c1 10.0.18.39 &>/dev/null
  if [ $? -ne 0 ]
  then
    echo "Ping failed - `date`"
  fi
  sleep 0.1
done
