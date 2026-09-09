%define debug_package %nil

Name:           i3status-rust
Version:        0.36.1
Release:        1
Summary:        Feature-rich and resource-friendly replacement for i3status, written in Rust

License:        GPLv3+
URL:            https://github.com/greshake/i3status-rust
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cargo
BuildRequires:  rust-packaging
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(libsensors)

%description
i3status-rs is a feature-rich and resource-friendly replacement for i3status,
written in pure Rust. It provides a way to display "blocks" of system
information (time, battery status, volume, etc) on the i3 bar. It is also
compatible with sway.

%prep
%autosetup -p1

%build
cargo build --release

%install
mkdir -p %{buildroot}%{_bindir}

install -m 0755 
target/release/i3status-rs 
%{buildroot}%{_bindir}/i3status-rs

install -m 0655 -Dp 
example_config.toml 
%{buildroot}%{_sysconfdir}/xdg/i3/status.toml

%files
%license LICENSE
%doc README.md NEWS.md CONTRIBUTING.md blocks.md example_config.toml example_icon.toml example_theme.toml themes.md
%{_bindir}/i3status-rs
%{_sysconfdir}/xdg/i3/status.toml
