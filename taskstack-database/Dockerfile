FROM debian:jessie
MAINTAINER James Brink, brink.james@gmail.com

RUN apt-get update
RUN apt-get install -y postgresql-9.4 postgresql-contrib-9.4 postgresql-9.4-postgis-2.1 postgresql-client-9.4 inotify-tools
RUN rm -rf /var/lib/apt/lists/*

ADD ./scripts/postgres.sh /postgres.sh
RUN chown postgres:postgres /postgres.sh
RUN chmod +x /postgres.sh

USER postgres

# Initial default user/pass and schema
ENV USER postgres
ENV PASSWORD postgres
ENV SCHEMA postgres
ENV POSTGIS false

RUN echo "listen_addresses='*'" >> /etc/postgresql/9.4/main/postgresql.conf
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.4/main/pg_hba.conf

RUN touch /var/tmp/firstrun

EXPOSE 5432
CMD ["/postgres.sh"]
