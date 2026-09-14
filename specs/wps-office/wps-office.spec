%global wpsver 11.1.0.11733
%global wpsrel %(echo %{wpsver} | awk -F. '{print $NF}')

Name:           wps-office
Version:        %{wpsver}
Release:        2
Summary:        Linux office suite with similar appearance to MS Office
Group:          Office
# The old Kingsoft WPS Community License has disappeared from the site.
# There is an EULA in the archive that we ship as the package license file,
# plus a non-downloadable EULA only reachable from inside the program:
# https://www.wps.com/eula?distsrc=2021help&lang=en_US&version=11.1.0.10920
License:        EULA
URL:            https://www.wps.com/

# Upstream only distributes this as a prebuilt vendor RPM, so we just
# repack it rather than compiling anything ourselves.
Source0:        http://wdl1.pcfg.cache.wpscdn.com/wpsdl/wpsoffice/download/linux/%{wpsrel}/%{name}-%{version}.XA-1.x86_64.rpm
Source1:        wps-office.rpmlintrc

ExclusiveArch:  %{x86_64}
BuildRequires:  cpio
BuildRequires:  hardlink

# Vendor package ships prebuilt, unusual/bundled sonames -- don't try to
# scan them for auto Requires/Provides
AutoReqProv:    no

# this is untouched vendor binary, skip
# find-debuginfo and stripping entirely.
%global debug_package %{nil}
%global __os_install_post %{nil}

Conflicts:      EternalTerminal

%description
WPS Office is an office suite whose interface closely mirrors Microsoft
Office, providing word processing, spreadsheet, and presentation
applications.

%prep
# There's no tarball to unpack -- just create an empty build dir and
# extract the vendor RPM's payload into it ourselves.
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -idmv

%build
# Nothing to build; this is a prebuilt vendor binary package.

%install
mkdir -p %{buildroot}
cp -a ./opt %{buildroot}/

# Disable background services
chmod -x %{buildroot}/opt/kingsoft/wps-office/office6/wpsd
chmod -x %{buildroot}/opt/kingsoft/wps-office/office6/wpscloudsvr

# Vendor's cron/logrotate/autostart config and non-working menu category
rm -rf %{buildroot}/etc

# Vendor postinst/prerm scripts we don't want to ship
rm -rf %{buildroot}/opt/kingsoft/wps-office/INSTALL

# Qt4 rpc libs, bundled systemd/libdbus, and bundled libstdc++ -- the
# distro already provides compatible versions of all of these.
rm -f %{buildroot}/opt/kingsoft/wps-office/office6/librpcetapi.so
rm -f %{buildroot}/opt/kingsoft/wps-office/office6/librpcwpsapi.so
rm -f %{buildroot}/opt/kingsoft/wps-office/office6/librpcwppapi.so
rm -f %{buildroot}/opt/kingsoft/wps-office/office6/libdbus-1.so*
rm -f %{buildroot}/opt/kingsoft/wps-office/office6/libstdc++.so.6
rm -f %{buildroot}/opt/kingsoft/wps-office/office6/libstdc++.so.6.0.28

# These two are plain config files but ship with a spurious executable
# bit, which makes rpmlint try (and fail) to parse them as shell scripts.
chmod -x %{buildroot}/opt/kingsoft/wps-office/office6/cfgs/domain_qing.cfg
chmod -x %{buildroot}/opt/kingsoft/wps-office/office6/skins/2019gov/skin.ini

# The vendor payload ships many byte-identical files (per-locale strings,
# repeated icons, duplicated .so files) -- hardlink them to reclaim space.
hardlink -c %{buildroot} || :

%files
/opt/kingsoft/wps-office
%exclude /opt/kingsoft/wps-office/office6/mui/default/EULA_linux.html
%exclude /opt/kingsoft/wps-office/office6/mui/default/Privacy_Linux.html
%exclude /opt/kingsoft/wps-office/office6/thirdpartylegalnotices.txt
%license opt/kingsoft/wps-office/office6/mui/default/EULA_linux.html
%license opt/kingsoft/wps-office/office6/thirdpartylegalnotices.txt
%doc opt/kingsoft/wps-office/office6/mui/default/Privacy_Linux.html
