%global astal_commit cbcd9f49dd6b9638dc5623b56cc6e1e0a60b593e
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global bumpver 4

%global _vpath_srcdir lib/astal/io

%define libname %mklibname astal-io
%define devname %mklibname astal-io -d
%global pkgname astal

Name:       astal-io
Version:    1~%{bumpver}.git%{astal_shortcommit}
Release:    1
Source0:    https://github.com/aylur/astal/archive/%{astal_commit}/%{pkgname}-%{astal_shortcommit}.tar.gz
Summary:    Building blocks for creating custom desktop shells
URL:        https://github.com/aylur/astal
License:    LGPL-2.1-only
Group:      System/Libraries

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  python3
BuildRequires:  vala-devel
BuildRequires:  valadoc
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  gobject-introspection
BuildRequires:  pkgconfig(gobject-introspection-1.0)

%description
%summary

%package -n %{libname}
Summary:    %{summary}
Group:      System/Libraries
Provides:   %{libname} = %{EVRD}

%description -n %{libname}
Building blocks for creating custom desktop shells

%package -n %{devname}
Summary:  Development files for %{name}
Group:    Development/C
Requires: %{libname} = %{EVRD}

%global __requires_exclude ^%{_libdir}/lib%{name}\\.so*
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
%{_bindir}/astal
%{_libdir}/girepository-1.0/AstalIO-0.1.typelib
%{_libdir}/libastal-io.so.0{,.*}

%files -n %{devname}
%{_datadir}/gir-1.0/AstalIO-0.1.gir
%{_datadir}/vala/vapi/astal-io-0.1.vapi
%{_includedir}/astal-io.h
%{_libdir}/pkgconfig/astal-io-0.1.pc
%{_libdir}/libastal-io.so
