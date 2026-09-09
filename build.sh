#!/bin/sh
set -e

if [ -z "$PKG" ]; then
    echo "PKG is not set — pass the package name to build" >&2
    exit 1
fi

SPEC="specs/$PKG/$PKG.spec"

if [ ! -f "$SPEC" ]; then
    echo "No spec found at $SPEC" >&2
    exit 1
fi

echo "==> OpenMandriva build environment"
cat /etc/os-release

echo "==> Repository configuration"
dnf repolist

echo "==> Installing packaging tools"

dnf install -y \
    packaging-tools \
    rpmlint \
    git \
    sudo \
    createrepo_c \
    github-cli \
    hostname

id builder >/dev/null 2>&1 || useradd -m builder

echo "builder ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/builder
chmod 440 /etc/sudoers.d/builder

# ------------------------------------------------------------
# Prepare ABF build directory
# ------------------------------------------------------------

su builder -c "mkdir -p /home/builder/abf/$PKG"

cp "specs/$PKG"/* \
    "/home/builder/abf/$PKG/"

chown -R builder:builder /home/builder/abf

# ------------------------------------------------------------
# Personal RPM repository
# ------------------------------------------------------------

mkdir -p /home/builder/localrepo

gh release download repo-rpm \
    --repo "$REPO" \
    --dir /home/builder/localrepo \
    --pattern '*.rpm' \
    --clobber 2>/dev/null \
    || echo "No repo-rpm release yet — building from a clean local repo."

chown -R builder:builder /home/builder/localrepo

if find /home/builder/localrepo -maxdepth 1 -name '*.rpm' -print -quit \
    | grep -q .; then

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
fi

# ------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------

echo "==> Build architecture"
rpm --eval '%{_target_cpu}'

echo "==> Distro"
rpm --eval '%{distribution}'

echo "==> DNF repositories"
dnf repolist

echo "==> Checking required tools"
command -v hostname
command -v abb
command -v rpmbuild

# ------------------------------------------------------------
# Lint
# ------------------------------------------------------------

echo "==> Linting spec"

su builder -c \
    "rpmlint /home/builder/abf/$PKG/$PKG.spec" \
    || echo "==> rpmlint reported issues (non-fatal)"

# ------------------------------------------------------------
# Build dependencies
# ------------------------------------------------------------

echo "==> Installing BuildRequires"

dnf builddep -y \
    "/home/builder/abf/$PKG/$PKG.spec"

# ------------------------------------------------------------
# Build
# ------------------------------------------------------------

echo "==> Running abb build"

su builder -c \
    "cd /home/builder/abf/$PKG && abb build"

# ------------------------------------------------------------
# Collect RPMs
# ------------------------------------------------------------

mkdir -p "$OLDPWD/out" "$OLDPWD/merged"

find "/home/builder/abf/$PKG/RPMS" \
    -name '*.rpm' \
    -exec cp {} "$OLDPWD/out/" \;

cp /home/builder/localrepo/*.rpm \
    "$OLDPWD/merged/" 2>/dev/null || true

find "/home/builder/abf/$PKG/RPMS" \
    -name '*.rpm' \
    -exec cp {} "$OLDPWD/merged/" \;

# ------------------------------------------------------------
# RPM lint
# ------------------------------------------------------------

echo "==> Linting built RPMs"

rpmlint "$OLDPWD"/out/*.rpm \
    || echo "==> rpmlint reported issues on built RPMs (non-fatal)"

# ------------------------------------------------------------
# De-duplicate repository
# ------------------------------------------------------------

echo "==> De-duplicating merged/"

(
    cd "$OLDPWD/merged"

    ls *.rpm 2>/dev/null \
        | sed -E 's/-[^-]+-[^-]+\.[a-zA-Z0-9_]+\.rpm$//' \
        | sort -u \
        | while read -r base; do

            matches=$(ls -- "$base"-*.rpm 2>/dev/null)
            newest=$(printf '%s\n' "$matches" | sort -V | tail -n1)

            printf '%s\n' "$matches" |
                while read -r f; do
                    [ "$f" = "$newest" ] && continue

                    echo "==> Removing stale $f"
                    rm -f -- "$f"
                done
        done
)

# ------------------------------------------------------------
# Repository metadata
# ------------------------------------------------------------

createrepo_c "$OLDPWD/merged"

echo "==> Build complete"

echo "==> Packages:"
find "$OLDPWD/out" -name '*.rpm'
