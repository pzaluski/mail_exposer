#!/bin/bash

/etc/init.d/mail_exposer start
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start mail_exposer: $status"
  exit $status
fi

/etc/init.d/nginx start
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start nginx: $status"
  exit $status
fi

while sleep 60; do
  /etc/init.d/mail_exposer status
  mail_exposer_status=$?
  /etc/init.d/nginx status
  nginx_status=$?
  
  if [ $mail_exposer_status -ne 0 -o $nginx_status -ne 0 ]; then
    echo "One of the processes has already exited."
    exit 1
  fi
done