%define module validators

Name:		python-validators
Version:	0.35.0
Release:	1
Summary:	Python Data Validation for Humans
Group:		Development/Python
License:	MIT
URL:		https://python-validators.github.io/validators
Source0:	https://files.pythonhosted.org/packages/source/v/%{module}/%{module}-%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildSystem:	python
BuildArch:	noarch
BuildRequires:	pkgconfig(python)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(wheel)

%description
validators is a Python library for data validation. It ships single-purpose
validator functions for common inputs such as email addresses, URLs, IP
addresses, domains, credit card numbers, and more.

%files
%license LICENSE.txt
%doc README.md CHANGES.md
%{py_puresitedir}/%{module}
%{py_puresitedir}/%{module}-%{version}.dist-info
