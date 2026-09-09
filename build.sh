#!/bin/sh
set -eu

# ============================================================
# Configuration / validation
# ============================================================

if [ -z "${PKG:-}" ]; then
    echo "PKG is not set — pass the package name to build" >&2
    exit 1
fi

SPEC="specs/$PKG/$PKG.spec"

if [ ! -f "$SPEC" ]; then
    echo "No spec found at $SPEC" >&2
    exit 1
fi

echo "==> Building package: $PKG"
echo "==> Spec: $SPEC"

# ============================================================
# Synchronize OpenMandriva ROME
# ============================================================

echo
echo "==> OpenMandriva system"
cat /etc/os-release

echo
echo "==> Initial repository configuration"
dnf repolist

echo
echo "==> Synchronizing OpenMandriva Rolling"

dnf clean all
dnf makecache
dnf distro-sync -y

echo
echo "==> Repository configuration after synchronization"
dnf repolist

# ============================================================
# Install build infrastructure
# ============================================================

echo
echo "==> Installing packaging tools"

dnf install -y \
    packaging-tools \
    rpmlint \
    git \
    sudo \
    createrepo_c \
    github-cli \
    hostname

# ============================================================
# Create builder user
# ============================================================

if ! id builder >/dev/null 2>&1; then
    useradd -m builder
fi

echo "builder ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/builder
chmod 440 /etc/sudoers.d/builder

# ============================================================
# Prepare ABF build directory
# ============================================================

echo
echo "==> Preparing ABF build directory"

su builder -c "mkdir -p /home/builder/abf/$PKG"

cp "specs/$PKG"/* \
    "/home/builder/abf/$PKG/"

chown -R builder:builder /home/builder/abf

# ============================================================
# Personal RPM repository
# ============================================================

echo
echo "==> Preparing personal RPM repository"

mkdir -p /home/builder/localrepo

if gh release download repo-rpm \
    --repo "$REPO" \
    --dir /home/builder/localrepo \
    --pattern '*.rpm' \
    --clobber 2>/dev/null; then

    echo "==> Previous personal RPM repository downloaded"
else
    echo "==> No repo-rpm release yet — building from a clean local repo"
fi

chown -R builder:builder /home/builder/localrepo

if find /home/builder/localrepo \
    -maxdepth 1 \
    -name '*.rpm' \
    -print -quit 2>/dev/null |
    grep -q .; then

    echo "==> Creating personal RPM repository"

    su builder -c \
        'createrepo_c /home/builder/localrepo'

    cat > /etc/yum.repos.d/local-personal.repo <<'EOF'
[local-personal]
name=Personal OpenMandriva repository
baseurl=file:///home/builder/localrepo
enabled=1
gpgcheck=0
priority=1
EOF

    dnf clean metadata
    dnf makecache
else
    echo "==> Personal repository is empty"
fi

# ============================================================
# Build environment diagnostics
# ============================================================

echo
echo "============================================================"
echo " Build environment"
echo "============================================================"

echo
echo "==> Architecture"
rpm --eval '%{_target_cpu}'

echo
echo "==> RPM platform"
rpm --eval '%{_target_platform}'

echo
echo "==> RPM distribution"
rpm --eval '%{distribution}'

echo
echo "==> DNF repositories"
dnf repolist

echo
echo "==> Required commands"

command -v hostname
command -v abb
command -v rpmbuild
command -v dnf

# ============================================================
# Verify RPM stack
# ============================================================

echo
echo "==> RPM package versions"

rpm -q rpm || true
rpm -q rpm-libs || true
rpm -q python3-rpm || true
rpm -q rpmlint || true

echo
echo "==> RPM database"

rpm --eval '%{_dbpath}'

if [ -d /var/lib/rpm ]; then
    echo "/var/lib/rpm exists"
else
    echo "ERROR: /var/lib/rpm does not exist" >&2
    exit 1
fi

echo
echo "==> Python RPM module"

python3 -c '
import rpm
print("python-rpm:", rpm.__version__)
print("module:", rpm.__file__)
'

echo
echo "==> rpmlint"

rpmlint --version

echo
echo "==> DNF"

dnf --version

# ============================================================
# Check required BuildRequires
# ============================================================

echo
echo "============================================================"
echo " Build dependency providers"
echo "============================================================"

echo
echo "==> pkgconfig(dbus-1)"
dnf provides 'pkgconfig(dbus-1)' || true

echo
echo "==> pkgconfig(libpulse)"
dnf provides 'pkgconfig(libpulse)' || true

echo
echo "==> rust-packaging"
dnf provides 'rust-packaging' || true

# ============================================================
# Lint spec
# ============================================================

echo
echo "============================================================"
echo " Linting spec"
echo "============================================================"

su builder -c \
    "rpmlint /home/builder/abf/$PKG/$PKG.spec" \
    || echo "==> rpmlint reported issues on the spec (non-fatal)"

# ============================================================
# Install BuildRequires
# ============================================================

echo
echo "============================================================"
echo " Installing BuildRequires"
echo "============================================================"

dnf builddep -y \
    "/home/builder/abf/$PKG/$PKG.spec"

# ============================================================
# Verify BuildRequires
# ============================================================

echo
echo "==> Build dependencies installed"

# ============================================================
# Build with ABB
# ============================================================

echo
echo "============================================================"
echo " Running abb build"
echo "============================================================"

su builder -c \
    "cd /home/builder/abf/$PKG && abb build"

# ============================================================
# Collect built RPMs
# ============================================================

echo
echo "============================================================"
echo " Collecting RPMs"
echo "============================================================"

mkdir -p "$OLDPWD/out"
mkdir -p "$OLDPWD/merged"

find "/home/builder/abf/$PKG/RPMS" \
    -name '*.rpm' \
    -exec cp {} "$OLDPWD/out/" \;

# Copy previously released packages
cp /home/builder/localrepo/*.rpm \
    "$OLDPWD/merged/" 2>/dev/null || true

# Copy newly built packages
find "/home/builder/abf/$PKG/RPMS" \
    -name '*.rpm' \
    -exec cp {} "$OLDPWD/merged/" \;

echo
echo "==> Packages produced by this build:"
find "$OLDPWD/out" -name '*.rpm' -print

# ============================================================
# Lint built RPMs
# ============================================================

echo
echo "============================================================"
echo " Linting built RPMs"
echo "============================================================"

if find "$OLDPWD/out" -name '*.rpm' -print -quit |
    grep -q .; then

    rpmlint "$OLDPWD"/out/*.rpm \
        || echo "==> rpmlint reported issues on built RPMs (non-fatal)"
else
    echo "ERROR: No RPMs were produced" >&2
    exit 1
fi

# ============================================================
# De-duplicate merged repository
# ============================================================

echo
echo "============================================================"
echo " De-duplicating merged/"
echo "============================================================"

(
    cd "$OLDPWD/merged"

    ls *.rpm 2>/dev/null |
        sed -E 's/-[^-]+-[^-]+\.[a-zA-Z0-9_]+\.rpm$//' |
        sort -u |
        while read -r base; do

            matches=$(ls -- "$base"-*.rpm 2>/dev/null || true)

            if [ -z "$matches" ]; then
                continue
            fi

            newest=$(printf '%s\n' "$matches" |
                sort -V |
                tail -n1)

            printf '%s\n' "$matches" |
                while read -r f; do

                    [ "$f" = "$newest" ] && continue

                    echo "==> Removing stale $f"
                    echo "    superseded by $newest"

                    rm -f -- "$f"
                done
        done
)

# ============================================================
# Create repository metadata
# ============================================================

echo
echo "============================================================"
echo " Creating repository metadata"
echo "============================================================"

createrepo_c "$OLDPWD/merged"

# ============================================================
# Final summary
# ============================================================

echo
echo "============================================================"
echo " Build complete"
echo "============================================================"

echo
echo "==> This run's packages:"
find "$OLDPWD/out" -name '*.rpm' -print

echo
echo "==> Complete personal repository:"
find "$OLDPWD/merged" -maxdepth 1 -name '*.rpm' -print

echo
echo "==> Target architecture:"
rpm --eval '%{_target_cpu}'

echo
echo "==> Repository:"
dnf repolist

echo
echo "Build successful."
