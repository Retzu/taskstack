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

mkdir -p ./data

$docker build -t taskstack-database .
$docker run --name taskstack-database --rm -p 5432:5432 \
    -e USER=taskstack \
    -e PASSWORD=taskstack \
    -e SCHEMA=taskstack \
    taskstack-database


#$docker run --rm --name taskstack-postgres -v $(pwd)/db:/var/lib/postgresql/data -e POSTGRES_PASSWORD=taskstacktestdb -e POSTGRES_USER=postgres -p 127.0.0.1:5432:5432 postgres
