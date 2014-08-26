
function init(){
  if [ ! -d "$logfile" ]; then
    mkdir -p "$log_dir"
    if [ "$?" != "0" ]; then
      exit 1
    fi
  fi
}

function error(){
  echo -e "\033[31m$1\033[0m"
}

function warning(){
  echo -e "\033[33m$1\033[0m"
}

function info(){
  echo "$1"
}

function succeed(){
  echo -e "\033[42;37m$1\033[0m"
}
