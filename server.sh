#!/bin/bash

NAME="test platform server"
APP_NAME=test-platform
APP_LOG_NAME=test-platform.log
UWSGI_LOG_NAME=/log/$APP_NAME/uwsgi.log
APP_DIR=/data/$APP_NAME
APP_PATH=$APP_DIR/uwsgi.ini
print_succ()
{
    echo "$(tput setaf 2)$(tput bold)DONE$(tput sgr0)"
}
print_fail()
{
    echo "$(tput setaf 1)$(tput bold)FAILED$(tput sgr0)"
}
stop_service()
{
    echo "stoping $NAME..."
    if pgrep -f $APP_PATH > /dev/null 2>&1; then
        pgrep -f $APP_PATH|xargs kill -9
    fi
    print_succ
}
start_service()
{
    if pgrep -f $APP_PATH > /dev/null 2>&1; then
        echo "$NAME service is already running."
        return
    else
        export APP_NAME=$APP_NAME
        export APP_DIR=$APP_DIR
        export APP_LOG_NAME=$APP_LOG_NAME
        chmod +x $APP_DIR/venv/bin/python3
        chmod +x $APP_DIR/venv/bin/uwsgi
        echo "starting $NAME service..."
        $APP_DIR/venv/bin/uwsgi  --chdir $APP_DIR --daemonize $UWSGI_LOG_NAME --ini $APP_DIR/uwsgi.ini
    fi
    sleep 5
    if pgrep -f $APP_PATH > /dev/null 2>&1; then
        print_succ
    else
        print_fail
    fi
}

check_status()
{
   if pgrep -f $APP_PATH > /dev/null 2>&1; then
       echo "$NAME is running"
   else
       echo "$NAME is not running"
   fi
}
#set -e
#. /lib/lsb/init-functions
case "$1" in
    start)
        echo "Starting $DESC..."
        start_service
        ;;
    stop)
        echo "Stopping $DESC..."
        stop_service
        ;;
    restart)
        echo "Restarting $DESC..."
        stop_service
        sleep 3
        start_service
        echo "Checking..."
        check_status
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $NAME {start|stop|restart|status}" >&2
        exit 1
        ;;
esac
exit 0
