#! /bin/bash

if [ "$#" -lt 2 ]; then
  echo "$0 host app"
  exit 1
fi
base_dir=$(cd "$(dirname "$0")"; pwd)
source "${base_dir}/de.properties"
source "${base_dir}/utils.sh"
# make some init work
init

host="$1"
app="$2"
router="${host}.${domain}"
etcd_server="$etcd_peers"
marathon_api="$marathon_api"
etcdctl="$base_dir/etcdctl"
log_file="${log_dir}/map.log"

if curl -s -X GET -H 'Content-Type: application/json' $marathon_api/v2/apps/$app | grep -q "does not exist"
then
  error "haven't created app $app yet!"
  exit 1
fi
$etcdctl --peers $etcd_server ls /apps/$app/ >> $log_file 2>&1
if [ $? -eq 0 ]; then
  $etcdctl --peers $etcd_server setdir /apps/$app/routers/$router >> $log_file 2>&1
  if [ $? -eq 0 ]; then
    succeed "succeed to bind app $app to host $host"
    exit 0
  else
    error "failed to bind app $app to host $host"
    exit 1
  fi
else
  error "host $host doesn't exist!"
  exit 1
fi
