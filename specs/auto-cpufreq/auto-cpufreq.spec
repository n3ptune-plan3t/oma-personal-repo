%define module auto_cpufreq

Name:           auto-cpufreq
Summary:        Automatic CPU speed & power optimizer for Linux
Version:        3.1.0
Release:        1
License:        GPL-3.0-or-later
Group:          System/Configuration/Hardware
URL:            https://github.com/AdnanHodzic/auto-cpufreq
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildSystem:    python
BuildArch:      noarch

BuildRequires:  pkgconfig(python3)
BuildRequires:  python%{pyver}dist(pip)
BuildRequires:  python%{pyver}dist(wheel)
BuildRequires:  python%{pyver}dist(poetry-core)
BuildRequires:  python%{pyver}dist(poetry-dynamic-versioning)
BuildRequires:  systemd-rpm-macros

Requires:       python%{pyver}dist(click)
Requires:       python%{pyver}dist(distro)
Requires:       python%{pyver}dist(psutil)
Requires:       python%{pyver}dist(pyinotify)
Requires:       python%{pyver}dist(pyasyncore)
Requires:       python%{pyver}dist(requests)
Requires:       python%{pyver}dist(urwid)
# GUI (auto-cpufreq-gtk)
Requires:       python-gobject
Requires:       typelib(Gtk) = 3.0
Requires:       polkit
%systemd_requires

%description
auto-cpufreq is an automatic CPU speed and power optimizer for Linux, based
on active monitoring of the laptop's battery state, CPU usage, CPU
temperature and system load. It ships a CLI, a daemon and a GTK GUI.

%prep
%autosetup -p1

# Build from a release tarball, not a git checkout
sed -i 's|^enable = true|enable = false|' pyproject.toml

# Packaged install lives in /usr, not /usr/local or /opt
sed -i \
	-e 's|/usr/local|/usr|g' \
	auto_cpufreq/core.py \
	auto_cpufreq/bin/auto_cpufreq.py \
	auto_cpufreq/gui/app.py \
	auto_cpufreq/gui/objects.py \
	scripts/auto-cpufreq-install.sh \
	scripts/auto-cpufreq-remove.sh
# Mutable state (override pickles) belongs in /var/lib
sed -i 's|/opt/auto-cpufreq/\(turbo-\)\?override.pickle|/var/lib/auto-cpufreq/\1override.pickle|' \
	auto_cpufreq/core.py
sed -i 's|/opt/auto-cpufreq/current/venv/bin/auto-cpufreq|%{_bindir}/auto-cpufreq|' \
	scripts/org.auto-cpufreq.pkexec.policy

%install -a
# Data used by the CLI/GUI (SCRIPTS_DIR, CSS_FILE, ICON_FILE)
install -dm755 %{buildroot}%{_datadir}/%{name}
cp -a scripts images %{buildroot}%{_datadir}/%{name}/
# Drop init-system files for other distros from the data dir
rm -f %{buildroot}%{_datadir}/%{name}/scripts/auto-cpufreq-{dinit,openrc,runit,s6,venv-wrapper}
rm -f %{buildroot}%{_datadir}/%{name}/scripts/{snapdaemon.sh,start_app}

# Helper expected on $PATH by the daemon
install -Dm755 scripts/cpufreqctl.sh %{buildroot}%{_bindir}/cpufreqctl.auto-cpufreq

# Desktop entry + icon
install -Dm644 scripts/auto-cpufreq-gtk.desktop -t %{buildroot}%{_datadir}/applications/
install -Dm644 images/icon.png %{buildroot}%{_datadir}/pixmaps/auto-cpufreq.png

# polkit policy for pkexec from the GUI
install -Dm644 scripts/org.auto-cpufreq.pkexec.policy -t %{buildroot}%{_datadir}/polkit-1/actions/

# systemd unit (upstream's points at an /opt venv)
install -dm755 %{buildroot}%{_unitdir}
cat > %{buildroot}%{_unitdir}/auto-cpufreq.service << 'EOF'
[Unit]
Description=auto-cpufreq - Automatic CPU speed & power optimizer for Linux
After=network.target network-online.target

[Service]
Type=simple
User=root
ExecStart=%{_bindir}/auto-cpufreq --daemon
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Runtime state directory
install -dm755 %{buildroot}%{_sharedstatedir}/%{name}

%post
%systemd_post auto-cpufreq.service

%preun
%systemd_preun auto-cpufreq.service

%postun
%systemd_postun_with_restart auto-cpufreq.service

%files
%license LICENSE
%doc README.md auto-cpufreq.conf-example
%{_bindir}/auto-cpufreq
%{_bindir}/auto-cpufreq-gtk
%{_bindir}/cpufreqctl.auto-cpufreq
%{_unitdir}/auto-cpufreq.service
%{_datadir}/%{name}
%{_datadir}/applications/auto-cpufreq-gtk.desktop
%{_datadir}/pixmaps/auto-cpufreq.png
%{_datadir}/polkit-1/actions/org.auto-cpufreq.pkexec.policy
%dir %{_sharedstatedir}/%{name}
%{python_sitelib}/%{module}
%{python_sitelib}/%{module}-%{version}.dist-info
