Docker container
================

To start Taskstack in a Docker container you need to build it first
```
$ docker build -t taskstack .
```

Then you need to start a PostgreSQL container. The taskstack container is
tailored towards the official container
```
$ docker run --name postgres -e POSTGRES_PASSWORD=postgres -d postgres
```

Then run the Taskstack container and link the PostgreSQL to it (alias has to be `db`)
```
$ docker run --name taskstack -p 8000:8000 --link postgres:db taskstack
```
