%define _empty_manifest_terminate_build 0
Name:           dunst
Version:        1.13.2
Release:        1
Summary:        Customizable and lightweight notification-daemon
License:        BSD
Group:          Graphical desktop/Other
URL:            https://dunst-project.org/
Source0:        https://github.com/dunst-project/dunst/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:	make
BuildRequires:  pkgconfig(libxdg-basedir)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(xscrnsaver)
BuildRequires:  pkgconfig(xinerama)
BuildRequires:  pkgconfig(gdk-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(libnotify)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(wayland-client)

%description
Dunst is a lightweight replacement for the notification-daemons provided
by most desktop environments. It's very customizable, doesn't depend on
any toolkits and therefore fits in those windowmanager centric setups
we all love to customize to perfection.

%prep
%setup -q

%build
%make_build

%install
%make_install PREFIX=%{_prefix}

%files
%doc RELEASE_NOTES README.md CHANGELOG.md AUTHORS
%license LICENSE
%dir %{_sysconfdir}/%{name}
%config %{_sysconfdir}/%{name}/dunstrc
%{_bindir}/%{name}
%{_bindir}/dunstctl
%{_bindir}/dunstify
%{_datadir}/dbus-1/services/org.knopwob.dunst.service
%{_userunitdir}/%{name}.service
%{_mandir}/man1/%{name}.1.*
%{_mandir}/man1/dunstctl.1.*
%{_mandir}/man5/%{name}.5.*
