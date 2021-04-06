#!/bin/bash

#catch signal from docker
trap '/etc/init.d/mail_exposer stop && /etc/init.d/nginx stop' HUP SIGINT QUIT TERM KILL EXIT

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

count=60
while sleep 1; do
  if [ $count -eq 0 ]; then
    /etc/init.d/mail_exposer status
    mail_exposer_status=$?
    /etc/init.d/nginx status
    nginx_status=$?
    count=$((60))
    if [ $mail_exposer_status -ne 0 -o $nginx_status -ne 0 ]; then
      echo "One of the processes has already exited."
      exit 1
    fi
  fi
  count=$((count-1))
done
