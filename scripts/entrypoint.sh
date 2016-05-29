#!/bin/bash

. /kb/deployment/user-env.sh

python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Initialize module"
  cd /data
  curl -s http://bioseed.mcs.anl.gov/~fangfang/kb/interproscan-5.18-57.0-data.tgz |tar xzf -
  ln -s /data/interproscan-5.18-57.0-data /kb/deployment/interproscan/data
  touch __READY__
  echo "Run Tests"
  make test
elif [ "${1}" = "async" ] ; then
  sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
  cd /data
  curl -s http://bioseed.mcs.anl.gov/~fangfang/kb/interproscan-5.18-57.0-data.tgz |tar xzf -
  ln -s /data/interproscan-5.18-57.0-data /kb/deployment/interproscan/data
  touch __READY__
elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
