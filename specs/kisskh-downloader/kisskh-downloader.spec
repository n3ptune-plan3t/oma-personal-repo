%define module kisskh_downloader

Name:		kisskh-downloader
Version:	0.2.4
Release:	1
Summary:	Command-line downloader for shows on kisskh.is
Group:		Development/Python
License:	Custom
URL:		https://pypi.org/project/kisskh-downloader
Source0:	https://files.pythonhosted.org/packages/source/k/%{module}/%{module}-%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildSystem:	python
BuildArch:	noarch
BuildRequires:	pkgconfig(python)
BuildRequires:	python%{pyver}dist(uv-build)
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(wheel)
BuildRequires:	python%{pyver}dist(validators)
BuildRequires:	python%{pyver}dist(pysrt)

%description
kisskh-downloader is a simple command-line tool ("kisskh") for downloading
dramas/shows from kisskh.is, with support for selecting episode ranges,
video quality, and subtitle languages, plus optional subtitle decryption.

%files
%doc README.md
%{py_puresitedir}/%{module}
%{py_puresitedir}/%{module}-%{version}.dist-info
%{_bindir}/kisskh
