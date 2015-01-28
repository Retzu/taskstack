#!/bin/bash

docker=$(which docker)

if [[ $EUID -ne 0 ]]; then
    echo "Must be run as root (to start the docker container)"
    exit 1
fi

if [[ -z $docker ]]; then
    echo "You must have Docker installed!" >&2
    exit 1
fi

mkdir -p ./db

#docker rm taskstack-postgres 2>/dev/null
$docker run --name taskstack-postgres -v $(pwd)/db:/var/lib/postgresql/data -e POSTGRES_PASSWORD=taskstacktestdb -e POSTGRES_USER=postgres -d postgres

chmod a+rwx ./db
