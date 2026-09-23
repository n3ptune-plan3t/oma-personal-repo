Name:           deadd-notification-center
Version:        2.1.1
Release:        1
Summary:        Customizable notification-daemon with notification center

License:        BSD
URL:            https://github.com/phuhl/linux_notification_center
Source0:        https://codeload.github.com/phuhl/linux_notification_center/tar.gz/refs/tags/%{version}#/%{name}-%{version}.tar.gz

# NOTE ON THE BUILD PATH:
# This is a Haskell/Stack project (stack.yaml + .cabal file), not a plain
# Makefile project, so `%make_build`/`%make_install` below won't actually
# invoke Stack correctly on their own - see the %build/%install comments.
#
# More importantly: `stack build` normally resolves its package snapshot
# and fetches dependencies from Stackage/Hackage over the network. ABF's
# build sandbox is network-isolated during the build step, so this will
# fail there even once `stack` and `ghc` exist as packages. Every other
# distro that ships this package (Fedora/Debian-style Haskell packaging,
# nixpkgs) builds it with `cabal` against individually-packaged Haskell
# libraries instead of stack, precisely to avoid needing network access
# at build time. Direct deps, per upstream's .cabal file / Gentoo's
# ebuild: aeson, configfile, dbus, env-locale, gi-cairo, gi-gdk,
# gi-gdkpixbuf, gi-gio, gi-glib, gi-gobject, gi-gtk, hslogger, safe,
# split, timezone-olson, timezone-series, yaml - each of which would need
# to exist as a ghc-*-devel package here first.
#
# The BuildRequires/%build below are left as a stack-based build, per
# what was asked for, but treat this as a local/dev-sandbox spec until
# the cabal-based path above is worked out for a real ABF submission.
BuildRequires:  stack
BuildRequires:  ghc
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(gobject-introspection-1.0)
BuildRequires:  pkgconfig(gtk+-3.0)

%description
Customizable notification-daemon with notification center.

%prep
%autosetup -n linux_notification_center-%{version}

%build
# --system-ghc tells Stack to use the distro-packaged GHC above instead
# of downloading its own; --no-install-ghc/--no-install-cabal stop it
# from trying to fetch a toolchain. This still needs network access to
# resolve the Stackage snapshot and Hackage deps unless a local package
# index is set up - see the NOTE above.
stack build --system-ghc --no-install-ghc --no-install-cabal --local-bin-path=%{_builddir}/bin

%install
install -Dm0755 %{_builddir}/bin/deadd-notification-center %{buildroot}%{_bindir}/deadd-notification-center

%files
%license LICENSE
%{_bindir}/deadd-notification-center
%{_datadir}/*
