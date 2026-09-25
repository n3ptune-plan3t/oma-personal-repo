%define debug_package %nil
%define _disable_lto 1

Name:           i3status-rust
Version:        0.36.1
Release:        1
Summary:        Feature-rich and resource-friendly replacement for i3status, written in Rust

License:        GPL-3.0-or-later
URL:            https://github.com/greshake/i3status-rust
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.xz
Source2:        cargo_config

# Switches reqwest (and, transitively, oauth2) from openssl-sys to rustls-tls;
# the vendored openssl-sys does not yet support OpenSSL 4.x. All crates this
# pulls in (rustls, ring, tokio-rustls, hyper-rustls...) are already present
# in the upstream Cargo.lock via other dependencies, so this does not change
# the vendored dependency set.
Patch0:         0001-reqwest-use-rustls-tls.patch

# Cargo.toml declares `edition = "2024"` with `resolver = "3"` (added
# upstream for the 0.36 series). Parsing edition2024 requires cargo/rustc
# >= 1.85 (where it was stabilized) -- an older cargo fails at the manifest
# stage with "feature `edition2024` is required", before rustc is even
# invoked. Pin the floor explicitly instead of relying on whatever the
# builder happens to have, since niri (edition 2021) builds fine on this
# same repo's runners without it and can mask the gap.
BuildRequires:  rust-packaging
BuildRequires:  rust >= 1.85.0
BuildRequires:  cargo >= 1.85.0
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
%cargo_prep
sed -i -e 's,source.crates-io,sources.rust-sucks,g' .cargo/config.toml
cat %{SOURCE2} >>.cargo/config.toml

%build
export CARGO_PROFILE_RELEASE_LTO=off
%cargo_build

%install
install -Dm0755 -t %{buildroot}%{_bindir} target/release/i3status-rs

%files
%license LICENSE
%doc README.md NEWS.md CONTRIBUTING.md blocks.md example_config.toml example_icon.toml example_theme.toml themes.md
%{_bindir}/i3status-rs
