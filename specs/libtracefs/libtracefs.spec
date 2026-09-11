Summary:	Linux kernel tracefs access library
Name:		libtracefs
Version:	1.8.3
Release:	1
License:	LGPLv2.1
Group:		System/Libraries
Url:		https://git.kernel.org/pub/scm/libs/libtrace/libtracefs.git/
Source0:	https://git.kernel.org/pub/scm/libs/libtrace/libtracefs.git/snapshot/%{name}-%{version}.tar.gz

# Same note as libtraceevent: real source is kernel.org, not the
# tag-less GitHub mirror.
BuildSystem:	meson
BuildOption:	-Ddefault_library=shared
BuildOption:	-Ddoc=false
BuildOption:	-Dsamples=false
BuildOption:	-Dutest=false

BuildRequires:	meson
# sqlhist.l/sqlhist.y grammar files are generated at build time
BuildRequires:	flex
BuildRequires:	bison
BuildRequires:	pkgconfig(libtraceevent) >= 1.8.1

%description
libtracefs provides APIs for accessing the Linux kernel's tracefs
filesystem (ftrace). It's the tracing library that powertop's meson
build (2.16+) and trace-cmd link against.

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%{_libdir}/%{name}.so*
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/libtracefs/
%{_datadir}/bash-completion/completions/tracefs_sql.bash
