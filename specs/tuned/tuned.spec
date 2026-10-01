%global __requires_exclude /usr/bin/stap

# Modern layout used by upstream 2.23+
%global system_profiles_dir %{_prefix}/lib/tuned/profiles
%global user_profiles_dir   %{_sysconfdir}/tuned/profiles

Summary:	A dynamic adaptive system tuning daemon
Name:		tuned
Version:	2.28.0
Release:	1
License:	GPLv2+
URL:		https://github.com/redhat-performance/tuned
Group:		System/Kernel and hardware
Source0:	https://github.com/redhat-performance/tuned/archive/v%{version}/%{name}-%{version}.tar.gz
Patch0:		0002-get-CPE-string-from-etc-os-release-rather-than-the-m.patch
BuildArch:	noarch
Requires(post):	virt-what
BuildRequires:	make
BuildRequires:	systemd-rpm-macros
BuildRequires:	pkgconfig(python)
BuildRequires:	python%{pyver}dist(six)
Requires:	python%{pyver}dist(decorator)
Requires:	python%{pyver}dist(configobj)
Requires:	python%{pyver}dist(pyudev)
Requires:	python%{pyver}dist(six)
Requires:	python%{pyver}dist(python-linux-procfs)
Requires:	python3-dbus
Requires:	python-gi
Requires:	virt-what
Requires:	hdparm
Requires:	ethtool
Requires:	typelib(GObject)
Requires:	dbus
Requires:	polkit
%if "%{_host_cpu}" != "aarch64"
Requires:	cpupower
Requires:	x86_energy_perf_policy
%endif
%if %{mdvver} > 3000000
%rename		laptop-mode-tools
%endif

%description
The tuned package contains a daemon that tunes system settings dynamically.
It does so by monitoring the usage of several system components periodically.
Based on that information components will then be put into lower or higher
power saving modes to adapt to the current usage.

%package gtk
Summary:	GTK GUI for tuned
Requires:	%{name} = %{version}-%{release}
Requires:	powertop
Requires:	polkit
Requires:	python-gi
Requires:	python-gobject3

%description gtk
GTK GUI that can control tuned and provide simple profile editor.

%package utils
Requires:	%{name} = %{version}-%{release}
Summary:	Various tuned utilities
Group:		System/Kernel and hardware
Requires:	powertop

%description utils
This package contains utilities that can help you to fine tune and
debug your system and manage tuned profiles.

%package utils-systemtap
Summary:	Disk and net statistic monitoring systemtap scripts
Requires:	%{name} = %{version}-%{release}
Group:		System/Kernel and hardware
Requires:	systemtap

%description utils-systemtap
This package contains several systemtap scripts to allow detailed
manual monitoring of the system.

%package profiles
Summary:	Additional tuned profiles (compat, SAP, MSSQL, Oracle, Atomic, realtime, NFV, CPU partitioning, Spectrum Scale, PostgreSQL, OpenShift)
Requires:	%{name} = %{version}-%{release}
%global old_profiles compat sap sap-hana mssql oracle atomic realtime nfv-guest nfv-host nfv cpu-partitioning spectrumscale postgresql openshift
%{lua:
for p in string.gmatch(rpm.expand("%{old_profiles}"), "%S+") do
  print(rpm.expand("Obsoletes:\t%{name}-profiles-" .. p .. " < %{version}-%{release}\n"))
  print(rpm.expand("Provides:\t%{name}-profiles-" .. p .. " = %{version}-%{release}\n"))
end
}

%description profiles
Additional tuned profiles in a single package: backward-compatible tuned 1.0
profiles, SAP NetWeaver/HANA, MS SQL Server, Oracle, Atomic, realtime, NFV
(guest/host), CPU partitioning, IBM Spectrum Scale, PostgreSQL and OpenShift.

%package ppd
Summary:	PPD compatibility daemon
Requires:	%{name} = %{version}-%{release}
Provides:	ppd-service
Conflicts:	ppd-service

%description ppd
An API translation daemon that allows applications to easily transition
to TuneD from power-profiles-daemon (PPD).

%prep
%autosetup -p1 -n %{name}-%{version}

sed -i -e 's#/usr/sbin#%{_sbindir}#g' Makefile tuned-gui.desktop tuned-gui.py tuned.service

%build
# nothing to build (noarch)

%install
%make_install \
  BINDIR="%{_bindir}" \
  SBINDIR="%{_sbindir}" \
  TUNED_SYSTEM_PROFILES_DIR="%{system_profiles_dir}" \
  TUNED_USER_PROFILES_DIR="%{user_profiles_dir}"

# PPD support
make install-ppd DESTDIR="%{buildroot}" \
  BINDIR="%{_bindir}" \
  SBINDIR="%{_sbindir}" \
  DOCDIR="%{_docdir}/%{name}" || :

rm -rf %{buildroot}%{_docdir}/%{name}

# OpenMandriva default profile
printf '%s\n' 'latency-performance' > %{buildroot}%{_sysconfdir}/tuned/active_profile

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-tuned.preset << EOF
enable tuned.service
EOF

# Ensure required directories exist
install -d %{buildroot}%{user_profiles_dir}
install -d %{buildroot}%{_sysconfdir}/tuned/recommend.d
install -d %{buildroot}%{_localstatedir}/log/tuned
install -d %{buildroot}/run/tuned
install -d %{buildroot}%{_var}/lib/tuned
%post
%systemd_post tuned.service

# convert active_profile from full path to name (if needed)
sed -i 's|.*/\([^/]\+\)/[^\.]\+\.conf|\1|' /etc/tuned/active_profile 2>/dev/null || :

if [ ! -f %{_sysconfdir}/tuned/active_profile ] || [ -z "$(cat %{_sysconfdir}/tuned/active_profile 2>/dev/null)" ]; then
    PROFILE="$(%{_sbindir}/tuned-adm recommend 2>/dev/null)"
    [ "$PROFILE" ] || PROFILE=balanced
    %{_sbindir}/tuned-adm profile "$PROFILE" 2>/dev/null || printf '%s\n' "$PROFILE" > %{_sysconfdir}/tuned/active_profile
fi

%preun
%systemd_preun tuned.service

%postun
%systemd_postun_with_restart tuned.service

%post ppd
%systemd_post tuned-ppd.service 2>/dev/null || :

%preun ppd
%systemd_preun tuned-ppd.service 2>/dev/null || :

%postun ppd
%systemd_postun_with_restart tuned-ppd.service 2>/dev/null || :

%files
%doc AUTHORS README* doc/TIPS.txt
%{_datadir}/bash-completion/completions/tuned-adm
%exclude %{python3_sitelib}/tuned/gtk
%{python3_sitelib}/tuned
%{_sbindir}/tuned
%{_sbindir}/tuned-adm


# Exclude profiles that go into subpackages
%exclude %{system_profiles_dir}/default
%exclude %{system_profiles_dir}/desktop-powersave
%exclude %{system_profiles_dir}/laptop-ac-powersave
%exclude %{system_profiles_dir}/server-powersave
%exclude %{system_profiles_dir}/laptop-battery-powersave
%exclude %{system_profiles_dir}/enterprise-storage
%exclude %{system_profiles_dir}/spindown-disk
%exclude %{system_profiles_dir}/sap-netweaver
%exclude %{system_profiles_dir}/sap-hana
%exclude %{system_profiles_dir}/sap-hana-kvm-guest
%exclude %{system_profiles_dir}/mssql
%exclude %{system_profiles_dir}/oracle
%exclude %{system_profiles_dir}/atomic-host
%exclude %{system_profiles_dir}/atomic-guest
%exclude %{system_profiles_dir}/realtime
%exclude %{system_profiles_dir}/realtime-virtual-guest
%exclude %{system_profiles_dir}/realtime-virtual-host
%exclude %{system_profiles_dir}/cpu-partitioning
%exclude %{system_profiles_dir}/cpu-partitioning-powersave
%exclude %{system_profiles_dir}/spectrumscale-ece
%exclude %{system_profiles_dir}/postgresql
%exclude %{system_profiles_dir}/openshift
%exclude %{system_profiles_dir}/openshift-control-plane
%exclude %{system_profiles_dir}/openshift-node

%{_prefix}/lib/tuned
%{_prefix}/lib/kernel/install.d/*tuned.*
%dir %{_sysconfdir}/tuned
%dir %{user_profiles_dir}
%dir %{_sysconfdir}/tuned/recommend.d
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tuned/active_profile
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tuned/profile_mode
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tuned/post_loaded_profile
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tuned/ppd_base_profile
%config(noreplace) %{_sysconfdir}/tuned/tuned-main.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/tuned/bootcmdline
%{_datadir}/dbus-1/system.d/com.redhat.tuned.conf
%verify(not size mtime md5) %{_sysconfdir}/modprobe.d/tuned.conf
%{_tmpfilesdir}/tuned.conf
%{_unitdir}/tuned.service
%{_presetdir}/86-tuned.preset
%{_libexecdir}/tuned/defirqaffinity.py
%dir %{_localstatedir}/log/tuned
%dir /run/tuned
%dir %{_var}/lib/tuned
%doc %{_mandir}/man5/tuned*
%doc %{_mandir}/man7/tuned-profiles.7*
%doc %{_mandir}/man8/tuned*
%{_sysconfdir}/grub.d/00_tuned
%{_datadir}/polkit-1/actions/com.redhat.tuned.policy

%files gtk
%{_sbindir}/tuned-gui
%{python3_sitelib}/tuned/gtk
%{_datadir}/tuned/ui
%{_iconsdir}/hicolor/scalable/apps/tuned.svg
%{_datadir}/applications/tuned-gui.desktop

%files utils
%{_bindir}/powertop2tuned
%{_libexecdir}/tuned/pmqos-static*

%files utils-systemtap
%doc doc/README.utils
%doc doc/README.scomes
%{_sbindir}/varnetload
%{_sbindir}/netdevstat
%{_sbindir}/diskdevstat
%{_sbindir}/scomes
%doc %{_mandir}/man8/varnetload.*
%doc %{_mandir}/man8/netdevstat.*
%doc %{_mandir}/man8/diskdevstat.*
%doc %{_mandir}/man8/scomes.*

%files profiles
%dir %{_sysconfdir}/systemd/system.conf.d
%config(noreplace) %{_sysconfdir}/systemd/system.conf.d/00-tuned.conf
# compat
%{system_profiles_dir}/default
%{system_profiles_dir}/desktop-powersave
%{system_profiles_dir}/laptop-ac-powersave
%{system_profiles_dir}/server-powersave
%{system_profiles_dir}/laptop-battery-powersave
%{system_profiles_dir}/enterprise-storage
%{system_profiles_dir}/spindown-disk
# sap / sap-hana
%{system_profiles_dir}/sap-netweaver
%{system_profiles_dir}/sap-hana
%{system_profiles_dir}/sap-hana-kvm-guest
# databases
%{system_profiles_dir}/mssql
%{system_profiles_dir}/oracle
%{system_profiles_dir}/postgresql
# atomic
%{system_profiles_dir}/atomic-host
%{system_profiles_dir}/atomic-guest
# realtime / nfv
%config(noreplace) %{_sysconfdir}/tuned/realtime-variables.conf
%config(noreplace) %{_sysconfdir}/tuned/realtime-virtual-guest-variables.conf
%config(noreplace) %{_sysconfdir}/tuned/realtime-virtual-host-variables.conf
%{system_profiles_dir}/realtime
%{system_profiles_dir}/realtime-virtual-guest
%{system_profiles_dir}/realtime-virtual-host
# cpu-partitioning
%config(noreplace) %{_sysconfdir}/tuned/cpu-partitioning-variables.conf
%config(noreplace) %{_sysconfdir}/tuned/cpu-partitioning-powersave-variables.conf
%{system_profiles_dir}/cpu-partitioning
%{system_profiles_dir}/cpu-partitioning-powersave
# spectrum scale / openshift
%{system_profiles_dir}/spectrumscale-ece
%{system_profiles_dir}/openshift
%{system_profiles_dir}/openshift-control-plane
%{system_profiles_dir}/openshift-node
# man pages
%{_mandir}/man7/tuned-profiles-compat.7*
%{_mandir}/man7/tuned-profiles-sap.7*
%{_mandir}/man7/tuned-profiles-sap-hana.7*
%{_mandir}/man7/tuned-profiles-mssql.7*
%{_mandir}/man7/tuned-profiles-oracle.7*
%{_mandir}/man7/tuned-profiles-atomic.7*
%{_mandir}/man7/tuned-profiles-realtime.7*
%{_mandir}/man7/tuned-profiles-nfv-guest.7*
%{_mandir}/man7/tuned-profiles-nfv-host.7*
%{_mandir}/man7/tuned-profiles-cpu-partitioning.7*
%{_mandir}/man7/tuned-profiles-spectrumscale-ece.7*
%{_mandir}/man7/tuned-profiles-postgresql.7*
%{_mandir}/man7/tuned-profiles-openshift.7*

%files ppd
%{_sbindir}/tuned-ppd
%{_unitdir}/tuned-ppd.service
%{_datadir}/dbus-1/system-services/net.hadess.PowerProfiles.service
%{_datadir}/dbus-1/system.d/net.hadess.PowerProfiles.conf
%{_datadir}/polkit-1/actions/net.hadess.PowerProfiles.policy
%{_datadir}/dbus-1/system-services/org.freedesktop.UPower.PowerProfiles.service
%{_datadir}/dbus-1/system.d/org.freedesktop.UPower.PowerProfiles.conf
%{_datadir}/polkit-1/actions/org.freedesktop.UPower.PowerProfiles.policy
%config(noreplace) %{_sysconfdir}/tuned/ppd.conf
