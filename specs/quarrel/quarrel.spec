%global astal_commit cbcd9f49dd6b9638dc5623b56cc6e1e0a60b593e
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global bumpver 4
%global pkgname astal

%global _vpath_srcdir lib/quarrel

%define libname %mklibname quarrel
%define devname %mklibname quarrel -d

Name:       quarrel
Version:    1~%{bumpver}.git%{astal_shortcommit}
Release:    1
Source0:    https://github.com/aylur/astal/archive/%{astal_commit}/%{pkgname}-%{astal_shortcommit}.tar.gz
Summary:    Command line argument parsing library (used by Astal CLIs)
URL:        https://github.com/aylur/astal
License:    LGPL-2.1-only
Group:      System/Libraries

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  python3
BuildRequires:  vala
BuildRequires:  valadoc
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(gobject-introspection-1.0)

%description
%summary

%package -n %{libname}
Summary:    %{summary}
Group:      System/Libraries
Provides:   %{libname} = %{EVRD}

%description -n %{libname}
%summary

%package -n %{devname}
Summary:  Development files for %{name}
Group:    Development/C
Requires: %{libname} = %{EVRD}

%description -n %{devname}
Development files (Headers etc.) for %{name}.

%prep
%autosetup -n astal-%{astal_commit} -p1

%build
%meson
%meson_build

%install
%meson_install

%files -n %{libname}
%license LICENSE
%{_libdir}/girepository-1.0/Quarrel-0.1.typelib
%{_libdir}/libquarrel.so.0{,.*}

%files -n %{devname}
%{_datadir}/gir-1.0/Quarrel-0.1.gir
%{_datadir}/vala/vapi/quarrel-0.1.vapi
%{_includedir}/quarrel.h
%{_libdir}/libquarrel.so
%{_libdir}/pkgconfig/quarrel-0.1.pc
