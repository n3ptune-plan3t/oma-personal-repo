%define module pysrt

# PyPI's license field reads plain "GPLv3" with no "only"/"or-later"
# qualifier, and upstream (github.com/byroot/pysrt) doesn't ship a full
# license text file clarifying it either -- worth confirming with upstream
# before this goes any further than a local build.
#
# This is an older, pre-pyproject.toml package (setup.py + setup.cfg only);
# BuildSystem: python still handles it via pip/setuptools, same as the
# modern packages.

Name:		python-pysrt
Version:	1.1.2
Release:	1
Summary:	SubRip (.srt) subtitle parser and writer
Group:		Development/Python
License:	GPLv3
URL:		https://github.com/byroot/pysrt
Source0:	https://files.pythonhosted.org/packages/source/p/%{module}/%{module}-%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildSystem:	python
BuildArch:	noarch
BuildRequires:	pkgconfig(python)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(wheel)

%description
pysrt is a Python library for parsing, manipulating, and writing SubRip
(.srt) subtitle files. It also installs a small "srt" command-line tool
for basic subtitle file manipulation.

%files
%doc README.rst
%{py_puresitedir}/%{module}
# Legacy setup.py-only builds don't reliably produce a *.dist-info dir
# with a predictable name (sometimes it's *.egg-info instead); glob it,
# matching OpenMandriva's own python-chardet.spec, which hits the same
# no-pyproject.toml situation.
%{py_puresitedir}/*.*-info
%{_bindir}/srt
