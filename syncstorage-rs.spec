Name:           syncstorage-rs
Version:        0.21.1
Release:        5%{?dist}
Summary:        Mozilla Sync Storage built with Rust
License:        MPL-2.0+
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%{?systemd_requires}

BuildRequires:  rust-packaging
BuildRequires:  systemd-rpm-macros
BuildRequires:  llvm-devel
BuildRequires:  clang-devel
BuildRequires:  mariadb-devel

# Default DB
Suggests:       mariadb-server
# Used to generate passwords in setup instructions
Suggests:       openssl
# Used as reverse proxy in setup instructions
Suggests:       httpd

%global forgeurl        https://github.com/mozilla-services/syncstorage-rs
%global tag             %{version}
%global saccount        ffsync

%forgemeta -a -i

Source0:        %{forgesource0}
URL:            %{forgeurl0}

Source1:        README-FEDORA.md
Source2:        syncserver.service
Source3:        syncserver.toml
Source4:        syncserver.env

# Remove callbacks to Sentry API in order to disable sending metrics to mozilla foundation.
# See: https://www.kyzer.me.uk/syncserver/#Code_patch:_remove_the_callbacks_to_Sentry_API
Patch0:         syncstorage-rs-nosentry.patch

# Populate DB for tokenserver DB
Patch1:         syncstorage-rs-populate-tokendb.patch

# Dynamically initialize node url and max permitted users in nodes table.
Patch2:         syncstorage-rs-updatenodes.patch

# Fix mariadb compatibility
Patch3:         syncstorage-rs-mariadb-compat.patch

%description
%{name} is Mozilla's new firefox sync server written in Rust.

%prep
%forgesetup -a
%patch 0 -p1 -b .nosentry
%patch 1 -p1 -b .populatedb
%patch 2 -p1 -b .updatenodes
%patch 3 -p1 -b .mariadb
cp %{SOURCE1} .

%build
cargo install --debug --path ./syncserver --no-default-features --features=syncstorage-db/mysql --locked

%install
%{__install} -D -m 0755 -t %{buildroot}%{_libexecdir} target/debug/syncserver
%{__install} -D -m 0644 -t %{buildroot}%{_unitdir} %{SOURCE2}
%{__install} -D -m 0640 -t %{buildroot}%{_sysconfdir}/syncserver %{SOURCE3}
%{__install} -D -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/syncserver

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
%doc README-FEDORA.md

%changelog
* Tue Oct 14 2025 Fritz Elfert <fritz@fritz-elfert.de>
- Package debug build for now
* Tue Oct 14 2025 Fritz Elfert <fritz@fritz-elfert.de>
- Fixed mariadb compatibility
* Tue Oct 14 2025 Fritz Elfert <fritz@fritz-elfert.de>
- Fixed config file path
* Tue Oct 14 2025 Fritz Elfert <fritz@fritz-elfert.de>
- Tweaked default config
* Mon Oct  6 2025 Fritz Elfert <fritz@fritz-elfert.de>
- Initial packaging
