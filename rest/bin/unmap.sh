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
etcdctl="$base_dir/etcdctl"
log_file="${log_dir}/unmap.log"


$etcdctl --peers $etcd_server ls /vulcand/hosts/$router/apps/$app >> $log_file 2>&1
if [ $? -eq 0 ]; then
  $etcdctl --peers $etcd_server rmdir /vulcand/hosts/$router/apps/$app >> $log_file 2>&1
  if [ $? -eq 0 ]; then
    succeed "succeed to unbind app $app to host $host"
  exit 0
  else
    error "fail to unbind app $app to host $host"
    exit 1
  fi
else
  error "app $app has not been bind to host $host"
  exit 1
fi
