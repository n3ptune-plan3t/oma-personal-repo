%define debug_package %nil
Name:           i3status-rust
Version:	0.36.1
Release:	1
Summary:        Feature-rich and resource-friendly replacement for i3status, written in Rust

# Upstream license specification: GPLv3
License:        GPLv3+
# FIXME: Upstream uses unknown SPDX tag GPLv3!
URL:            https://github.com/greshake/i3status-rust
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  rust-packaging

%description
i3status-rs is a feature-rich and resource-friendly replacement for i3status,
written in pure Rust. It provides a way to display "blocks" of system
information (time, battery status, volume, etc) on the i3 bar. It is also
compatible with sway.

%files
%license LICENSE
%doc README.md NEWS.md CONTRIBUTING.md blocks.md example_config.toml example_icon.toml example_theme.toml themes.md
%{_bindir}/i3status-rs
%{_sysconfdir}/xdg/i3/status.toml

%prep
%autosetup -p1
#% cargo_prep

#% generate_buildrequires
#% cargo_generate_buildrequires

%build
#cargo build --release
%cargo_build

%install
#% cargo_install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 target/release/i3status-rs %{buildroot}%{_bindir}
# Basic configuration file. Mandatory for successful i3status-rust run.
install -m 0655 -Dp example_config.toml %{buildroot}%{_sysconfdir}/xdg/i3/status.toml
