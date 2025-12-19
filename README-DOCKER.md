# Docker images of syncstorage-rs for self hosting.

Currently, there are 5 images published on ghcr.io

1. Upstream master, pristine build (without any patches) for MySQL
2. Upstream master, pristine build (without any patches) for Postgres
3. Upstream master, patched build, implementing self-initialization of tokenserver DB
4. Release 0.21.1, pristine (slightly patched - bugfixes only)
5. Release 0.21.1, fully patched (like RPM and DEB packages)

I recommend using (5) or (3).

### Differences compared to upstream images

Most importantly, my images do **NOT** include any python support scripts. Therefore, if using pristine image variants,
you are on your own regarding initialization of the tokenserver DB.

Self-initialization introduces 2 new environment variables:

* `PUBLIC_URL` is used to set the `node` field of the `nodes` table.
* `MAX_CLIENTS` is used to set the `capacity` field of the `nodes` table.

### Generic startup of patched variants

I recommend using a config file instead of many environment variables.
Example config file:
```
master_secret = "CHANGE_ME!!!"

host = "localhost" # default
port = 8000        # default

# removing this line will default to moz_json formatted logs (which is preferred for production envs)
human_logs = 1

# MySQL DSN:
syncstorage.database_url = "mysql://ffsync:**topsecret**@localhost/ffsync?socket=/app/mysql.sock"

# disable quota limits
syncstorage.enable_quota = 0
# set the quota limit to 2GB.
# max_quota_limit = 200000000
syncstorage.enabled = true
syncstorage.limits.max_total_records = 1666 # See issues #298/#333

# MySQL DSN (same as above, as table names are distinct
tokenserver.database_url = "mysql://ffsync:**topsecret**@localhost/ffsync?socket=/app/mysql.sock"

tokenserver.enabled = true
tokenserver.run_migrations = true
tokenserver.fxa_email_domain = "api.accounts.firefox.com"
tokenserver.fxa_oauth_server_url = "https://oauth.accounts.firefox.com"
tokenserver.fxa_browserid_audience = "https://token.services.mozilla.comn"
tokenserver.fxa_browserid_issuer = "https://api.accounts.firefox.com"
tokenserver.fxa_browserid_server_url = "https://verifier.accounts.firefox.com"

# cors settings
# cors_allowed_origin = "localhost"
# cors_max_age = 86400
```
For the database setup, refer to [this doc](https://github.com/felfert/syncstorage-rs-rpm/blob/main/README-POSTINSTALL.md#1-create-a-mariadb-user-and-database)
Startup using this configfile (both the config file and the mariadb socket, get mapped into the /app directory of the image):
```
IMG="ghcr.io/felfert/syncstorage-rs-rpm/syncserver-0.21.1:mysql-patched"

podman run --name syncserver -v ./syncserver.toml:/app/syncserver.toml -v /var/lib/mysql/mysql.sock:/app/mysql.sock \
    -p 8000:8000 -e RUST_LOG=info -e MAX_CLIENTS=1 -e PUBLIC_URL=https://fritz.fe.think -e SYNC_CONFIG=/app/syncserver.toml \
    --rm -it $IMG
```
For apache reverse-proxy setup refer to [this doc](https://github.com/felfert/syncstorage-rs-rpm/blob/main/README-POSTINSTALL.md#4-setup-reverse-proxy-apache-virtual-host)
