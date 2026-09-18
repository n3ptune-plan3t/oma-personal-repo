%define debug_package %nil

Name:           i3status-rust
Version:        0.36.1
Release:        1
Summary:        Feature-rich and resource-friendly replacement for i3status, written in Rust

License:        GPL-3.0-or-later
URL:            https://github.com/greshake/i3status-rust
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.xz
# Switches reqwest (and, transitively, oauth2) from default-tls
# (openssl-sys) to rustls-tls, since the vendored openssl-sys does
# not yet support OpenSSL 4.x. See patch header for details.
Patch0:         0001-reqwest-use-rustls-tls.patch

BuildRequires:  cargo
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  lm_sensors-devel

%description
i3status-rs is a feature-rich and resource-friendly replacement for i3status,
written in pure Rust. It provides a way to display "blocks" of system
information (time, battery status, volume, etc) on the i3 bar. It is also
compatible with sway.

%prep
%autosetup -p1 -a1
mkdir -p .cargo
cat > .cargo/config.toml <<'EOF'
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

%build
rm -rf target
cargo clean
cargo build --release --offline

%install
install -Dm0755 target/release/i3status-rs %{buildroot}%{_bindir}/i3status-rs
install -m 0644 -Dp example_config.toml %{buildroot}%{_sysconfdir}/xdg/i3/status.toml

%files
%license LICENSE
%doc README.md NEWS.md CONTRIBUTING.md blocks.md example_config.toml example_icon.toml example_theme.toml themes.md
%{_bindir}/i3status-rs
%{_sysconfdir}/xdg/i3/status.toml
