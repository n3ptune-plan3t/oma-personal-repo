%define debug_package %nil

Name:		xwayland-satellite
Version:	0.8.3
Release:	1
Summary:	Rootless Xwayland integration for any Wayland compositor
Group:		Graphical desktop/Other
License:	MPL-2.0
URL:		https://github.com/Supreeeme/xwayland-satellite
Source0:	%{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:	vendor.tar.xz

BuildRequires:	rust-packaging
BuildRequires:	clang
BuildRequires:	lib64xcb-devel
BuildRequires:	lib64xcb-cursor-devel

Requires:	xwayland
Requires:	lib64xcb1
Requires:	lib64xcb-cursor0

%description
xwayland-satellite grants rootless Xwayland integration to any Wayland
compositor implementing xdg_wm_base and viewporter. This is particularly
useful for compositors such as niri that do not implement rootless
Xwayland support themselves.

%prep
%autosetup -a1
rm -f rust-toolchain.toml
%cargo_prep -v vendor

%build
# No .git in the source tarball, so make vergen emit its idempotent
# sentinel instead of trying (and failing) to run git. The code
# explicitly handles VERGEN_IDEMPOTENT_OUTPUT in src/lib.rs.
export VERGEN_IDEMPOTENT=true
%cargo_build

%install
install -m 0755 -Dp target/release/%{name} %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md ARCHITECTURE.md
%{_bindir}/%{name}
