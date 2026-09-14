%global commit 8c980c24289cb08e03f72915970ce1bd6767e45a

Name:           ttf-wps-fonts
Version:        0.1
Release:        1
Summary:        Linux office suite with similar appearance to MS Office - font files
Group:          Graphics
# See wps-office.spec for the license background; this repo ships no
# separate license file of its own.
License:        EULA
URL:            https://www.wps.com/
Source0:        https://github.com/dv-anomaly/ttf-wps-fonts/archive/%{commit}.zip#/%{name}-%{commit}.zip

BuildArch:      noarch
BuildRequires:  unzip

%description
Font files for WPS Office, an office suite whose interface closely mirrors
Microsoft Office.

%prep
%setup -q -n ttf-wps-fonts-%{commit}
rm -f *.sh *.md

%build
# Nothing to build; these are prebuilt font files.

%install
mkdir -p %{buildroot}%{_datadir}/fonts/wps-fonts
install -m 644 *.ttf %{buildroot}%{_datadir}/fonts/wps-fonts/

%files
%{_datadir}/fonts/wps-fonts/*.ttf
