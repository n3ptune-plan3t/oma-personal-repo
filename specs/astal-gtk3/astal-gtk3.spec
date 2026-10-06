%global astal_commit cbcd9f49dd6b9638dc5623b56cc6e1e0a60b593e
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global bumpver 4
%global pkgname astal

%global _vpath_srcdir lib/astal/gtk3

%define libname %mklibname astal-gtk3
%define devname %mklibname astal-gtk3 -d

Name:       astal-gtk3
Version:    1~%{bumpver}.git%{astal_shortcommit}
Release:    1
Source0:    https://github.com/aylur/astal/archive/%{astal_commit}/%{pkgname}-%{astal_shortcommit}.tar.gz
Summary:    GTK3 component of Astal
URL:        https://github.com/aylurs/astal
License:    LGPL-2.1-only
Group:      System/Libraries

BuildRequires:  meson
BuildRequires:  python3
BuildRequires:  vala
BuildRequires:  valadoc
BuildRequires:  pkgconfig(astal-io-0.1)
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(gtk-layer-shell-0)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  girepository-devel

%description
%summary

%package -n %{libname}
Summary:    %{summary}
Group:      System/Libraries
Provides:   %{libname} = %{EVRD}
Provides:  astal3

%description -n %{libname}
%summary

%package -n %{devname}
Summary:  Development files for %{name}
Group:    Development/C
Requires: %{libname} = %{EVRD}

%global __requires_exclude ^%{_libdir}/libastal\\.so*
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
%{_libdir}/girepository-1.0/Astal-3.0.typelib
%{_libdir}/libastal.so.3{,.*}

%files -n %{devname}
%{_datadir}/gir-1.0/Astal-3.0.gir
%{_datadir}/vala/vapi/astal-3.0.vapi
%{_includedir}/astal.h
%{_libdir}/libastal.so
%{_libdir}/pkgconfig/astal-3.0.pc

