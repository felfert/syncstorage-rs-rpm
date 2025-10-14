Name:           syncstorage-rs
Version:        0.21.1
Release:        1%{?dist}
Summary:        Mozilla Sync Storage built with Rust
License:        MPL-2.0+
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%{?systemd_requires}

BuildRequires:  rust-packaging
BuildRequires:  systemd-rpm-macros
BuildRequires:  llvm-devel
BuildRequires:  clang-devel
BuildRequires:  mariadb-devel

Suggests:       mariadb-server

%global forgeurl        https://github.com/mozilla-services/syncstorage-rs
%global tag             %{version}
%global saccount        ffsync

%forgemeta -a -i

Source0:        %{forgesource0}
URL:            %{forgeurl0}

# Remove callbacks to Sentry API in order to disable sending metrics to mozilla foundation.
# See: https://www.kyzer.me.uk/syncserver/#Code_patch:_remove_the_callbacks_to_Sentry_API
Patch0:         syncstorage-rs-nosentry.patch

# Populate DB for tokenserver DB
Patch1:         syncstorage-rs-populate-tokendb.patch

# Dynamically initialize node url and max permitted users in nodes table.
Patch2:         syncstorage-rs-updatenodes.patch

%description
%{name} is Mozilla's new firefox sync server written in Rust.

%prep
%forgesetup -a
%patch 0 -p1 -b .nosentry
%patch 1 -p1 -b .populatedb
%patch 2 -p1 -b .updatenodes

%build
cargo install --path ./syncserver --no-default-features --features=syncstorage-db/mysql --locked
cat > syncserver.service << EOF
[Unit]
Description=Mozilla Firefox Sync
Wants=mariadb.service
After=network.target mariadb.service

[Service]
Type=simple
User=%{saccount}
EnvironmentFile=-/etc/sysconfig/syncserver
ExecStart=/usr/libexec/syncserver --config /etc/syncserver.toml

[Install]
WantedBy=multi-user.target
EOF
cat > syncserver.toml << EOF
master_secret = "CHANGE_ME!!!"

# removing this line will default to moz_json formatted logs (which is preferred for production envs)
human_logs = 1

# MySQL DSN:
#syncstorage.database_url = "mysql://ffsync:**topsecret**@localhost/ffsync?unix_socket=/var/lib/mysql/mysql.sock"

# disable quota limits
syncstorage.enable_quota = 0
# set the quota limit to 2GB.
# max_quota_limit = 200000000
syncstorage.enabled = true
syncstorage.limits.max_total_records = 1666 # See issues #298/#333

# Tokenserver settings:
# MySQL DSN (same as above, as table names are distinct
#tokenserver.database_url = "mysql://ffsync:**topsecret**@localhost/ffsync?unix_socket=/var/lib/mysql/mysql.sock"

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
EOF

cat > syncserver.env << EOF
# Define environment variables for syncserver here

# Global lof level
RUST_LOG=info

# The public URL to set in the node record of the nodes table
PUBLIC_URL=https://publicurl.tld

# The maximum number of sync client users for that node
MAX_CLIENTS=5
EOF

%install
%{__install} -D -m 0755 -t %{buildroot}%{_libexecdir} target/release/syncserver
%{__install} -D -m 0644 -t %{buildroot}%{_unitdir} syncserver.service
%{__install} -D -m 0640 -t %{buildroot}%{_sysconfdir}/syncserver syncserver.toml
%{__install} -D -m 0644 syncserver.env %{buildroot}%{_sysconfdir}/sysconfig/syncserver

%clean
rm -rf %{buildroot}

%pre
getent group %{saccount} >/dev/null || groupadd -r %{saccount}
getent passwd %{saccount} >/dev/null || \
    useradd -r -g %{saccount} -d %{_sysconfdir}/syncserver -s /sbin/nologin \
    -c "Mozilla Syncserver" %{saccount}
exit 0

%post
%systemd_post syncserver.service

%preun
%systemd_preun syncserver.service

%postun
%systemd_postun_with_restart syncserver.service

%files
%defattr(-,root,root,-)
%{_libexecdir}/*
%{_unitdir}/*
%config(noreplace) %{_sysconfdir}/sysconfig/syncserver
%attr(0640,root,%{saccount}) %config(noreplace) %{_sysconfdir}/syncserver/*

%changelog
* Mon Oct  6 2025 Fritz Elfert <fritz@fritz-elfert.de>
- Initial packaging
