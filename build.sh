#!/bin/sh
set -eu

# ============================================================
# Configuration
# ============================================================

if [ -z "${PKG:-}" ]; then
    echo "PKG is not set — pass the package name to build" >&2
    exit 1
fi

if [ -z "${REPO:-}" ]; then
    echo "REPO is not set" >&2
    exit 1
fi

SPEC="specs/$PKG/$PKG.spec"

if [ ! -f "$SPEC" ]; then
    echo "No spec found at $SPEC" >&2
    exit 1
fi

ROOT="$PWD"
ABF="/home/builder/abf/$PKG"
LOCALREPO="/home/builder/localrepo"

echo "============================================================"
echo " OpenMandriva package build"
echo "============================================================"
echo
echo "Package : $PKG"
echo "Spec    : $SPEC"
echo "Repo    : $REPO"
echo

# ============================================================
# Synchronize OpenMandriva Rolling / ROME
# ============================================================

echo "==> OpenMandriva system"
cat /etc/os-release

echo
echo "==> Initial repositories"
dnf repolist

echo
echo "==> Synchronizing Rolling system"

dnf clean all
dnf makecache
dnf distro-sync -y

echo
echo "==> Repositories after synchronization"
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

echo
echo "==> Preparing builder user"

if ! id builder >/dev/null 2>&1; then
    useradd -m builder
fi

echo "builder ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/builder
chmod 440 /etc/sudoers.d/builder

# ============================================================
# Verify RPM / architecture environment
# ============================================================

echo
echo "============================================================"
echo " RPM environment"
echo "============================================================"

echo
echo "==> RPM target CPU"
rpm --eval '%{_target_cpu}'

echo
echo "==> RPM target platform"
rpm --eval '%{_target_platform}'

echo
echo "==> RPM distribution"
rpm --eval '%{distribution}'

echo
echo "==> RPM database"
rpm --eval '%{_dbpath}'

if [ ! -d /var/lib/rpm ]; then
    echo "ERROR: /var/lib/rpm does not exist" >&2
    exit 1
fi

echo
echo "==> RPM packages"
rpm -q rpm || true
rpm -q rpm-libs || true
rpm -q python3-rpm || true
rpm -q rpmlint || true

echo
echo "==> Python RPM module"

python3 -c '
import rpm
print("python-rpm version:", rpm.__version__)
print("python-rpm module:", rpm.__file__)
'

echo
echo "==> rpmlint"
rpmlint --version

echo
echo "==> DNF"
dnf --version

# ============================================================
# Verify required commands
# ============================================================

echo
echo "==> Required commands"

command -v hostname
command -v abb
command -v rpmbuild
command -v dnf
command -v rpmlint
command -v createrepo_c
command -v gh

# ============================================================
# Prepare ABF directory
# ============================================================

echo
echo "==> Preparing ABF build directory"

rm -rf "$ABF"
su builder -c "mkdir -p '$ABF'"

cp "specs/$PKG"/* "$ABF/"

chown -R builder:builder "/home/builder/abf"

# ============================================================
# Download previous personal repository
# ============================================================

echo
echo "============================================================"
echo " Personal RPM repository"
echo "============================================================"

rm -rf "$LOCALREPO"
mkdir -p "$LOCALREPO"

if gh release download repo-rpm \
    --repo "$REPO" \
    --dir "$LOCALREPO" \
    --pattern '*.rpm' \
    --clobber 2>/dev/null
then
    echo "==> Previous repo-rpm release downloaded"
else
    echo "==> No repo-rpm release yet — building from a clean local repo"
fi

chown -R builder:builder "$LOCALREPO"

if find "$LOCALREPO" \
    -maxdepth 1 \
    -name '*.rpm' \
    -print -quit 2>/dev/null |
    grep -q .
then

    echo "==> Creating local repository metadata"

    su builder -c \
        "createrepo_c '$LOCALREPO'"

    cat > /etc/yum.repos.d/local-personal.repo <<EOF
[local-personal]
name=Personal OpenMandriva repository
baseurl=file://$LOCALREPO
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
# Show final repositories
# ============================================================

echo
echo "============================================================"
echo " Final repositories"
echo "============================================================"

dnf repolist

# ============================================================
# Verify BuildRequires providers
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
echo "==> pkgconfig(openssl)"
dnf provides 'pkgconfig(openssl)' || true

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

if ! su builder -c "rpmlint '$ABF/$PKG.spec'"; then
    echo "==> rpmlint reported issues (non-fatal)"
fi

# ============================================================
# Install BuildRequires
# ============================================================

echo
echo "============================================================"
echo " Installing BuildRequires"
echo "============================================================"

dnf builddep -y "$ABF/$PKG.spec"

# ============================================================
# Verify Cargo / Rust environment
# ============================================================

echo
echo "============================================================"
echo " Rust environment"
echo "============================================================"

command -v cargo
cargo --version
rustc --version

echo
echo "==> Cargo target"
rustc -vV

# ============================================================
# Verify OpenSSL
# ============================================================

echo
echo "============================================================"
echo " OpenSSL development environment"
echo "============================================================"

if command -v pkg-config >/dev/null 2>&1; then
    pkg-config --modversion openssl || true
    pkg-config --cflags openssl || true
    pkg-config --libs openssl || true
fi

# ============================================================
# Build
# ============================================================

echo
echo "============================================================"
echo " Running abb build"
echo "============================================================"

su builder -c "
    cd '$ABF'
    abb build
"

# ============================================================
# Locate RPMs
# ============================================================

echo
echo "============================================================"
echo " Built RPMs"
echo "============================================================"

RPMDIR="$ABF/RPMS"

if [ ! -d "$RPMDIR" ]; then
    echo "ERROR: RPM output directory does not exist: $RPMDIR" >&2
    exit 1
fi

if ! find "$RPMDIR" -name '*.rpm' -print -quit |
    grep -q .
then
    echo "ERROR: No RPMs were produced" >&2
    exit 1
fi

find "$RPMDIR" -name '*.rpm' -print

# ============================================================
# Verify RPM architecture
# ============================================================

echo
echo "============================================================"
echo " Verifying RPM architecture"
echo "============================================================"

BAD_ARCH=0

for rpm_file in "$RPMDIR"/*.rpm; do
    [ -f "$rpm_file" ] || continue

    arch=$(rpm -qp --qf '%{ARCH}' "$rpm_file")
    nvra=$(rpm -qp --qf '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}' "$rpm_file")

    echo "$nvra"

    case "$arch" in
        znver1)
            echo "  OK: znver1"
            ;;
        noarch)
            echo "  OK: noarch"
            ;;
        *)
            echo "  ERROR: unexpected architecture: $arch" >&2
            BAD_ARCH=1
            ;;
    esac
done

if [ "$BAD_ARCH" -ne 0 ]; then
    echo
    echo "ERROR: One or more RPMs are not znver1/noarch." >&2
    exit 1
fi

# ============================================================
# Prepare output directories
# ============================================================

echo
echo "==> Preparing output directories"

rm -rf "$ROOT/out" "$ROOT/merged"

mkdir -p "$ROOT/out"
mkdir -p "$ROOT/merged"

# Current build
find "$RPMDIR" \
    -name '*.rpm' \
    -exec cp {} "$ROOT/out/" \;

# Previous personal repository
cp "$LOCALREPO"/*.rpm \
    "$ROOT/merged/" 2>/dev/null || true

# Current build
find "$RPMDIR" \
    -name '*.rpm' \
    -exec cp {} "$ROOT/merged/" \;

# ============================================================
# Lint built RPMs
# ============================================================

echo
echo "============================================================"
echo " Linting built RPMs"
echo "============================================================"

if ! rpmlint "$ROOT"/out/*.rpm; then
    echo "==> rpmlint reported issues on built RPMs (non-fatal)"
fi

# ============================================================
# De-duplicate repository
# ============================================================

echo
echo "============================================================"
echo " De-duplicating merged/"
echo "============================================================"

(
    cd "$ROOT/merged"

    for rpm_file in *.rpm; do
        [ -f "$rpm_file" ] || continue

        # Extract package name using RPM itself.
        pkg_name=$(rpm -qp --qf '%{NAME}' "$rpm_file")

        # Collect all RPMs belonging to this package.
        matches=""

        for candidate in *.rpm; do
            [ -f "$candidate" ] || continue

            candidate_name=$(rpm -qp --qf '%{NAME}' "$candidate")

            if [ "$candidate_name" = "$pkg_name" ]; then
                matches="$matches
$candidate"
            fi
        done

        # Find newest version-release.
        newest=$(
            printf '%s\n' "$matches" |
            sed '/^$/d' |
            while read -r f; do
                rpm -qp --qf '%{EPOCHNUM}:%{VERSION}-%{RELEASE} %{NAME} %{ARCH} %{FILENAMES}\n' "$f"
            done |
            sort -V |
            tail -n1 |
            sed 's/.* \([^ ]*\.rpm\)$/\1/'
        )

        if [ -z "$newest" ]; then
            continue
        fi

        printf '%s\n' "$matches" |
        sed '/^$/d' |
        while read -r f; do
            if [ "$f" != "$newest" ]; then
                echo "==> Removing stale $f"
                echo "    superseded by $newest"
                rm -f -- "$f"
            fi
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

createrepo_c "$ROOT/merged"

# ============================================================
# Final verification
# ============================================================

echo
echo "============================================================"
echo " Final package list"
echo "============================================================"

for rpm_file in "$ROOT"/out/*.rpm; do
    [ -f "$rpm_file" ] || continue

    rpm -qp \
        --qf '%{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}.rpm\n' \
        "$rpm_file"
done

echo
echo "============================================================"
echo " Build complete"
echo "============================================================"

echo
echo "Current build:"
find "$ROOT/out" -name '*.rpm' -print

echo
echo "Personal repository:"
find "$ROOT/merged" -maxdepth 1 -name '*.rpm' -print

echo
echo "Target RPM architecture:"
rpm --eval '%{_target_cpu}'

echo
echo "Repository:"
dnf repolist

echo
echo "Build successful."
