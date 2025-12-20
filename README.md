# syncstorage-rs-rpm

This is the source for packaging [Mozilla's syncstorage-rs syncserver](https://github.com/mozilla-services/syncstorage-rs) on [COPR](https://copr.fedorainfracloud.org/coprs/felfert/syncstorage-rs/) for Fedora and RHEL, on [Launchpad](https://launchpad.net/~felfert/+archive/ubuntu/syncstorage-rs) for Ubuntu and as docker images [here](https://github.com/felfert?tab=packages&repo_name=syncstorage-rs-rpm).

### The differences compared to upstream

#### Features
* Removed callbacks to Sentry API in order to disable sending metrics to mozilla foundation.
* Pre-populate tokenserver DB to simplify installation (This is partially in upstream master now).
* Update node and capacity in tokenserver nodes table during startup using env variables.
* Use native journal logging if running under systemd (In upstream master now)

#### Bugfixes (for 0.21.1)
* Restore MariaDB compatibility (Is in upstream master now)
* Fixed inconsistency in MySQL socket parameters parameters (syncserver DB used old syntax `unix_socket=...` tokenserver DB used new syntax `socket=...`) Not needed for upstream master.

### Build status
[![Copr build status](https://copr.fedorainfracloud.org/coprs/felfert/syncstorage-rs/package/syncstorage-rs/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/felfert/syncstorage-rs/)
[![Static Badge](https://img.shields.io/badge/launchpad-package-green?logo=launchpad)](https://launchpad.net/~felfert/+archive/ubuntu/syncstorage-rs/+packages)
[![Docker images](https://github.com/felfert/syncstorage-rs-rpm/actions/workflows/docker.yml/badge.svg)](https://github.com/felfert/syncstorage-rs-rpm/actions/workflows/docker.yml)

### Documentation

[Post-install setup for RPMs and DEBs](README-POSTINSTALL.md) Partially applies to docker images as well (reverse proxy, mariadb)
[Docker-specific instructions](README-DOCKER.md)
