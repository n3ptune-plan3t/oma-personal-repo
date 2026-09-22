Name:           deadd-notification-center
Version:        2.1.1
Release:        1
Summary:        Customizable notification-daemon with notification center

License:        BSD
URL:            https://github.com/phuhl/linux_notification_center
Source0:        https://codeload.github.com/phuhl/linux_notification_center/tar.gz/refs/tags/%{version}#/%{name}-%{version}.tar.gz

BuildRequires: stack
BuildRequires: pkgconfig(cairo)
BuildRequires: pkgconfig(pango)
BuildRequires: pkgconfig(gobject-introspection-1.0)
BuildRequires: pkgconfig(gtk+-3.0)

%description
Customizable notification-daemon with notification center.

%prep
%autosetup -n linux_notification_center-%{version}

%build
%make_build

%install
%make_install

%files
%license LICENSE
%{_bindir}/*
%{_datadir}/*
