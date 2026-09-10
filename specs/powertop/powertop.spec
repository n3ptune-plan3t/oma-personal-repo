Summary:	Power saving diagnostic tool
Name:		powertop
Version:	2.16
Release:	1
License:	GPLv2+
Group:		System/Kernel and hardware
Url:		https://github.com/fenrus75/powertop
Source0:	https://github.com/fenrus75/powertop/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

# Upstream switched to the meson build system as of 2.16
# (autotools files are still shipped but are stale/unmaintained).
BuildSystem:	meson
BuildOption:	-Dbindir=%{_sbindir}

BuildRequires:	meson
BuildRequires:	pkgconfig(ncursesw)
BuildRequires:	pkgconfig(libpci)
BuildRequires:	pkgconfig(libnl-3.0)
BuildRequires:	pkgconfig(libtracefs)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	gettext-devel

%description
PowerTOP tool is a program that collects the various pieces of
information from a system and presents an overview of how well a
laptop is doing in terms of power savings. In addition, PowerTOP will
provide an indication of which tunables and software components are
the biggest offenders in slurping up battery time. PowerTOP will
update it's display frequently so that the impact of any changes can
be seen directly.

%find_lang %{name}

%files -f %{name}.lang
%doc README.md TODO
%{_sbindir}/%{name}
%{_mandir}/*/*.*
%{_datadir}/bash-completion/completions/%{name}
