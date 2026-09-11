%define major   1
%define libname %mklibname tracefs %{major}
%define devname %mklibname tracefs -d

Summary:	Linux kernel tracefs access library
Name:		libtracefs
Version:	1.8.3
Release:	1
License:	LGPLv2.1
Group:		System/Libraries
Url:		https://git.kernel.org/pub/scm/libs/libtrace/libtracefs.git/
Source0:	https://git.kernel.org/pub/scm/libs/libtrace/libtracefs.git/snapshot/%{name}-%{version}.tar.gz

BuildSystem:	meson
BuildOption:	-Ddefault_library=shared
BuildOption:	-Ddoc=false
BuildOption:	-Dsamples=false
BuildOption:	-Dutest=false

BuildRequires:	meson
BuildRequires:	flex
BuildRequires:	bison
BuildRequires:	pkgconfig(libtraceevent) >= 1.8.1

%description
libtracefs provides APIs for accessing the Linux kernel's tracefs
filesystem (ftrace). It's the tracing library that powertop's meson
build (2.16+) and trace-cmd link against.

%package -n %{libname}
Summary:	Linux kernel tracefs access library
Group:		System/Libraries

%description -n %{libname}
libtracefs provides APIs for accessing the Linux kernel's tracefs
filesystem (ftrace).

%package -n %{devname}
Summary:	Development files for libtracefs
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Requires:	pkgconfig(libtraceevent)
Provides:	libtracefs-devel = %{version}-%{release}

%description -n %{devname}
Headers, pkgconfig file, and unversioned .so symlink needed to build
software against libtracefs.

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%files -n %{libname}
%{_libdir}/%{name}.so.%{major}*
%{_datadir}/bash-completion/completions/tracefs_sql.bash

%files -n %{devname}
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/libtracefs/
