%define major   1
%define libname %mklibname traceevent %{major}
%define devname %mklibname traceevent -d

Summary:	Linux kernel trace event parsing library
Name:		libtraceevent
Version:	1.8.4
Release:	1
License:	LGPLv2.1
Group:		System/Libraries
Url:		https://git.kernel.org/pub/scm/libs/libtrace/libtraceevent.git/
Source0:	https://git.kernel.org/pub/scm/libs/libtrace/libtraceevent.git/snapshot/%{name}-%{version}.tar.gz

BuildSystem:	meson
BuildOption:	-Ddefault_library=shared
BuildOption:	-Ddoc=false

BuildRequires:	meson

%description
libtraceevent parses the raw Linux kernel trace event formats used by
ftrace and perf. It was originally embedded in trace-cmd and later
split out into its own library; libtracefs and powertop's tracing
support link against it.

%package -n %{libname}
Summary:	Linux kernel trace event parsing library
Group:		System/Libraries

%description -n %{libname}
libtraceevent parses the raw Linux kernel trace event formats used by
ftrace and perf.

%package -n %{devname}
Summary:	Development files for libtraceevent
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	libtraceevent-devel = %{version}-%{release}

%description -n %{devname}
Headers, pkgconfig file, and unversioned .so symlink needed to build
software against libtraceevent.

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%files -n %{libname}
%{_libdir}/%{name}.so.%{major}*
%dir %{_libdir}/traceevent
%{_libdir}/traceevent/plugins/

%files -n %{devname}
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/traceevent/
