%global __requires_exclude /usr/bin/stap

# Modern layout used by upstream 2.23+
%global system_profiles_dir %{_prefix}/lib/tuned/profiles
%global user_profiles_dir   %{_sysconfdir}/tuned/profiles

Summary:	A dynamic adaptive system tuning daemon
Name:		tuned
Version:	2.27.0
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

%package profiles-compat
Summary:	Additional tuned profiles mainly for backward compatibility with tuned 1.0
Group:		System/Kernel and hardware
Requires:	%{name} = %{version}-%{release}

%description profiles-compat
Additional tuned profiles mainly for backward compatibility with tuned 1.0.

%package profiles-sap
Summary:	Additional tuned profile(s) targeted to SAP NetWeaver loads
Requires:	%{name} = %{version}-%{release}

%description profiles-sap
Additional tuned profile(s) targeted to SAP NetWeaver loads.

%package profiles-sap-hana
Summary:	Additional tuned profile(s) targeted to SAP HANA loads
Requires:	%{name} = %{version}-%{release}

%description profiles-sap-hana
Additional tuned profile(s) targeted to SAP HANA loads.

%package profiles-mssql
Summary:	Additional tuned profile(s) for MS SQL Server
Requires:	%{name} = %{version}-%{release}

%description profiles-mssql
Additional tuned profile(s) for MS SQL Server.

%package profiles-oracle
Summary:	Additional tuned profile(s) targeted to Oracle loads
Requires:	%{name} = %{version}-%{release}

%description profiles-oracle
Additional tuned profile(s) targeted to Oracle loads.

%package profiles-atomic
Summary:	Additional tuned profile(s) targeted to Atomic
Requires:	%{name} = %{version}-%{release}

%description profiles-atomic
Additional tuned profile(s) targeted to Atomic host and guest.

%package profiles-realtime
Summary:	Additional tuned profile(s) targeted to realtime
Requires:	%{name} = %{version}-%{release}

%description profiles-realtime
Additional tuned profile(s) targeted to realtime.

%package profiles-nfv-guest
Summary:	Additional tuned profile(s) targeted to Network Function Virtualization (NFV) guest
Requires:	%{name} = %{version}-%{release}
Requires:	%{name}-profiles-realtime = %{version}-%{release}

%description profiles-nfv-guest
Additional tuned profile(s) targeted to Network Function Virtualization (NFV) guest.

%package profiles-nfv-host
Summary:	Additional tuned profile(s) targeted to Network Function Virtualization (NFV) host
Requires:	%{name} = %{version}-%{release}
Requires:	%{name}-profiles-realtime = %{version}-%{release}

%description profiles-nfv-host
Additional tuned profile(s) targeted to Network Function Virtualization (NFV) host.

%package profiles-nfv
Summary:	Additional tuned profile(s) targeted to Network Function Virtualization (NFV)
Requires:	%{name} = %{version}-%{release}
Requires:	%{name}-profiles-nfv-guest = %{version}-%{release}
Requires:	%{name}-profiles-nfv-host = %{version}-%{release}

%description profiles-nfv
Additional tuned profile(s) targeted to Network Function Virtualization (NFV).

%package profiles-cpu-partitioning
Summary:	Additional tuned profile(s) optimized for CPU partitioning
Requires:	%{name} = %{version}-%{release}

%description profiles-cpu-partitioning
Additional tuned profile(s) optimized for CPU partitioning.

%package profiles-spectrumscale
Summary:	Additional tuned profile(s) optimized for IBM Spectrum Scale
Requires:	%{name} = %{version}-%{release}

%description profiles-spectrumscale
Additional tuned profile(s) optimized for IBM Spectrum Scale.

%package profiles-postgresql
Summary:	Additional tuned profile(s) targeted to PostgreSQL server loads
Requires:	%{name} = %{version}-%{release}

%description profiles-postgresql
Additional tuned profile(s) targeted to PostgreSQL server loads.

%package profiles-openshift
Summary:	Additional TuneD profile(s) optimized for OpenShift
Requires:	%{name} = %{version}-%{release}

%description profiles-openshift
Additional TuneD profile(s) optimized for OpenShift.

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

%files profiles-compat
%{system_profiles_dir}/default
%{system_profiles_dir}/desktop-powersave
%{system_profiles_dir}/laptop-ac-powersave
%{system_profiles_dir}/server-powersave
%{system_profiles_dir}/laptop-battery-powersave
%{system_profiles_dir}/enterprise-storage
%{system_profiles_dir}/spindown-disk
%{_mandir}/man7/tuned-profiles-compat.7*

%files profiles-sap
%{system_profiles_dir}/sap-netweaver
%{_mandir}/man7/tuned-profiles-sap.7*

%files profiles-sap-hana
%{system_profiles_dir}/sap-hana
%{system_profiles_dir}/sap-hana-kvm-guest
%{_mandir}/man7/tuned-profiles-sap-hana.7*

%files profiles-mssql
%{system_profiles_dir}/mssql
%{_mandir}/man7/tuned-profiles-mssql.7*

%files profiles-oracle
%{system_profiles_dir}/oracle
%{_mandir}/man7/tuned-profiles-oracle.7*

%files profiles-atomic
%{system_profiles_dir}/atomic-host
%{system_profiles_dir}/atomic-guest
%{_mandir}/man7/tuned-profiles-atomic.7*

%files profiles-realtime
%config(noreplace) %{_sysconfdir}/tuned/realtime-variables.conf
%{system_profiles_dir}/realtime
%{_mandir}/man7/tuned-profiles-realtime.7*

%files profiles-nfv-guest
%config(noreplace) %{_sysconfdir}/tuned/realtime-virtual-guest-variables.conf
%{system_profiles_dir}/realtime-virtual-guest
%{_mandir}/man7/tuned-profiles-nfv-guest.7*

%files profiles-nfv-host
%config(noreplace) %{_sysconfdir}/tuned/realtime-virtual-host-variables.conf
%{system_profiles_dir}/realtime-virtual-host
%{_mandir}/man7/tuned-profiles-nfv-host.7*

%files profiles-nfv
# meta package only

%files profiles-cpu-partitioning
%config(noreplace) %{_sysconfdir}/tuned/cpu-partitioning-variables.conf
%config(noreplace) %{_sysconfdir}/tuned/cpu-partitioning-powersave-variables.conf
%{system_profiles_dir}/cpu-partitioning
%{system_profiles_dir}/cpu-partitioning-powersave
%{_mandir}/man7/tuned-profiles-cpu-partitioning.7*

%files profiles-spectrumscale
%{system_profiles_dir}/spectrumscale-ece
%{_mandir}/man7/tuned-profiles-spectrumscale-ece.7*

%files profiles-postgresql
%{system_profiles_dir}/postgresql
%{_mandir}/man7/tuned-profiles-postgresql.7*

%files profiles-openshift
%{system_profiles_dir}/openshift
%{system_profiles_dir}/openshift-control-plane
%{system_profiles_dir}/openshift-node
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