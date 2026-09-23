%bcond_with test
Name:           xidlehook
Version:        0.10.0
Release:        1
Summary:        Xautolock rewrite in Rust, with a few extra features
License:        MIT
URL:            https://github.com/jD91mZM2/xidlehook
Source0:        %{url}/archive/refs/tags/%{version}/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendored-dependencies.tar.xz
Source2:        cargo_config

BuildRequires:  rust-packaging
BuildRequires:  rust >= 1.39.0
BuildRequires:  python3
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-screensaver)
BuildRequires:  pkgconfig(libpulse)

%description
xidlehook is a general-purpose replacement for xautolock. It executes
a command when the computer has been idle for a specified amount of
time.

Improvements over xautolock include unlimited timers, "cancellers"
that can undo a timer action once new activity is detected, support
for multiple simultaneous instances, and options to skip locking when
an application is fullscreen or playing audio.

This package provides both the xidlehook daemon and the
xidlehook-client tool used to query and control it over its socket
API.

%prep
%autosetup -a1 -p1
%cargo_prep
sed -i -e 's,source.crates-io,sources.unused,g' .cargo/config.toml
cat %{SOURCE2} >>.cargo/config.toml

%build
%cargo_build

%install
install -Dm0755 -t %{buildroot}%{_bindir} target/release/xidlehook
install -Dm0755 -t %{buildroot}%{_bindir} target/release/xidlehook-client

%check
%if %{with test}
%cargo_test
%endif

%files
%license LICENSE
%doc README.md
%{_bindir}/xidlehook
%{_bindir}/xidlehook-client
