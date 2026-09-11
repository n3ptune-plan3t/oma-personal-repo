Summary:	Linux kernel trace event parsing library
Name:		libtraceevent
Version:	1.8.4
Release:	1
License:	LGPLv2.1
Group:		System/Libraries
Url:		https://git.kernel.org/pub/scm/libs/libtrace/libtraceevent.git/
Source0:	https://git.kernel.org/pub/scm/libs/libtrace/libtraceevent.git/snapshot/%{name}-%{version}.tar.gz

# Not built from a GitHub source: the GitHub mirror (rostedt/libtraceevent)
# carries no release tags, only a rolling branch. kernel.org is the real
# upstream and what Fedora/SUSE build from.
BuildSystem:	meson
# Personal-repo package: skip building the optional asciidoc/xmlto docs
# to avoid pulling in a doc toolchain nobody here will read.
BuildOption:	-Ddefault_library=shared
BuildOption:	-Ddoc=false

BuildRequires:	meson

%description
libtraceevent parses the raw Linux kernel trace event formats used by
ftrace and perf. It was originally embedded in trace-cmd and later
split out into its own library; libtracefs and powertop's tracing
support link against it.

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%{_libdir}/%{name}.so*
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/traceevent/
%dir %{_libdir}/traceevent
%{_libdir}/traceevent/plugins/
