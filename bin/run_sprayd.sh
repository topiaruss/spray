#!/bin/bash
(
 flock -n 9 || exit 1
  echo 'starting bin/sprayd'
  cd /home/sponsorcraft/spray
  source bin/activate
  cd spray
  bin/sprayd >> /tmp/cron_sprayd.log
  echo 'ending bin/sprayd'
) 9>/var/lock/cron_sprayd
