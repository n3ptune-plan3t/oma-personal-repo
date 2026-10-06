%global astal_commit cbcd9f49dd6b9638dc5623b56cc6e1e0a60b593e
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global bumpver 4
%global pkgname astal
%global _vpath_srcdir lib/astal/gtk4

%define libname %mklibname astal-gtk4
%define devname %mklibname astal-gtk4 -d

Name:       astal-4
Version:    1~%{bumpver}.git%{astal_shortcommit}
Release:    1
Source0:    https://github.com/aylur/astal/archive/%{astal_commit}/%{pkgname}-%{astal_shortcommit}.tar.gz
Summary:    GTK4 component of Astal
URL:        https://github.com/aylur/astal
License:    LGPL-2.1-only
Group:      System/Libraries

BuildRequires:  meson
BuildRequires:  pkgconfig(astal-io-0.1)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(gtk4-layer-shell-0)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  gobject-introspection
BuildRequires:  pkgconfig(gobject-introspection-1.0)
BuildRequires:  girepository-devel
BuildRequires:  vala
BuildRequires:  valadoc

%if %{without bootstrap}
Requires:       astal-libs%{?_isa}
%endif


%description
%summary

%package -n %{libname}
Summary:    GTK4 related files
Group:      System/Libraries
Provides:   %{libname} = %{EVRD}
Provides: astal4

%description -n %{libname}
%summary



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
%{_libdir}/girepository-1.0/Astal-4.0.typelib
%{_libdir}/libastal-4.so.4
%{_libdir}/libastal-4.so.4.0.0
%{_datadir}/vala/vapi/astal-4-4.0.vapi

%files -n %{devname}
%{_includedir}/astal-4.h
%{_libdir}/libastal-4.so
%{_libdir}/pkgconfig/astal-4-4.0.pc
%{_datadir}/gir-1.0/Astal-4.0.gir
