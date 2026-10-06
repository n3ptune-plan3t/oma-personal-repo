Name:       wl-vapi-gen
Version:    1.1.0
Release:    1
Summary:    Generate Vala bindings for Wayland protocols
URL:        https://github.com/kotontrion/wl-vapi-gen
Source0:    https://github.com/kotontrion/wl-vapi-gen/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
License:    LGPL-2.1-only
Group:      Development/Other

BuildArch:      noarch

BuildRequires:  meson
BuildRequires:  python
Requires:       python

%description
Generates Vala bindings (vapi) from Wayland protocol XML files.
Used to build Astal's Wayland libraries.

%prep
%autosetup -p1

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%{_bindir}/wl-vapi-gen
%{_datadir}/pkgconfig/wl-vapi-gen.pc
