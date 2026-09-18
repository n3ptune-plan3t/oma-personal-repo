Name:           qt6gtk2
Version:        0.7
Release:        1
Summary:        GTK+2.0 integration plugins for Qt6
License:        GPL-2.0-or-later
Group:          System/Libraries
URL:            https://www.opencode.net/trialuser/qt6gtk2
Source0:        https://www.opencode.net/trialuser/qt6gtk2/-/archive/%{version}/qt6gtk2-%{version}.tar.bz2

BuildRequires:  make
BuildRequires:  qmake-qt6
BuildRequires:  pkgconfig(gtk+-2.0)
BuildRequires:  pkgconfig(x11)
BuildRequires:  cmake(Qt6Core)
BuildRequires:  cmake(Qt6Gui)
BuildRequires:  cmake(Qt6Widgets)

# qmake-qt6 does not propagate %{optflags} into the build, so the resulting
# plugin binaries carry no usable DWARF source info. RPM's automatic
# debuginfo generation then tries to build a qt6gtk2-debugsource subpackage
# from an empty source list and fails with:
#   error: Empty %files file .../debugsourcefiles.list
# Disable debugsource subpackage generation for this package.
%undefine _debugsource_packages

%description
Qt6Gtk2 provides GTK+2.0 platform theme and style plugins for Qt 6.
This allows Qt6 applications to better integrate with GTK-based
desktop environments (fonts, icons, colours, etc.).

After installation set:

  export QT_QPA_PLATFORMTHEME=gtk2

(or qt6gtk2 / qt5gtk2). You can also put the line in
/etc/X11/Xsession.d/100-qt6gtk2.

Note: remove QT_STYLE_OVERRIDE if it is set.

%prep
%autosetup -p1

%build
qmake-qt6 PREFIX=%{_prefix}
%make_build

%install
%make_install INSTALL_ROOT=%{buildroot}

%files
%license COPYING
%doc AUTHORS ChangeLog README.md
%dir %{_libdir}/qt6/plugins/platformthemes/
%{_libdir}/qt6/plugins/platformthemes/libqt6gtk2.so
%dir %{_libdir}/qt6/plugins/styles/
%{_libdir}/qt6/plugins/styles/libqt6gtk2-style.so
