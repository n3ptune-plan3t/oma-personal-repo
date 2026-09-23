Name:           stack
Version:        3.9.1
Release:        1
Summary:        A cross-platform build tool for Haskell

License:        BSD-3-Clause
URL:            https://haskellstack.org

# NOTE: This repackages upstream's official pre-built, statically-linked
# executable rather than compiling from source. Building Stack from source
# requires GHC plus on the order of 75 individual Haskell libraries
# (see Arch's `stack` package for the full list), none of which are
# currently packaged for OpenMandriva. Every other distro without a full
# Haskell library set (Gentoo's stack-bin, Isabelle's bundled copy, etc.)
# does the same thing. The binary is fully static (verified: `file` reports
# "statically linked", `ldd` reports "not a dynamic executable"), so this
# package has no runtime library Requires.
Source0:        https://github.com/commercialhaskell/stack/releases/download/v%{version}/stack-%{version}-linux-x86_64.tar.gz

%description
Stack is a cross-platform program for developing Haskell projects. It is
intended for Haskellers both new and experienced.

This package installs upstream's official pre-built static executable,
since OpenMandriva does not currently package the GHC toolchain and
Haskell library set that a from-source build of Stack would require.

%prep
%autosetup -n %{name}-%{version}-linux-x86_64

%build
# Nothing to build - this is a pre-built, statically-linked release binary.

%install
install -Dm0755 stack %{buildroot}%{_bindir}/stack

%files
%license LICENSE
%doc README.md ChangeLog.md doc
%{_bindir}/stack
