#!/bin/bash
(
 flock -n 9 || exit 1
  echo 'starting bin/sprayd'
  bin/sprayd >> /tmp/cron_sprayd.log
) 9>/var/lock/cron_sprayd
