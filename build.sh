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

dnf install -y packaging-tools rpmlint git sudo createrepo_c github-cli

id builder >/dev/null 2>&1 || useradd -m builder
echo "builder ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/builder

# abb build expects to run from ~/abf/<package name>/ containing just the
# spec plus any patches sitting next to it.
su builder -c "mkdir -p /home/builder/abf/$PKG"
cp "specs/$PKG"/* "/home/builder/abf/$PKG/"
chown -R builder /home/builder/abf

# Seed a local repo with previously released packages, so BuildRequires
# on our own packages (e.g. one package needing another we maintain)
# resolve locally instead of failing or pulling Cooker's stock version.
mkdir -p /home/builder/localrepo
gh release download repo-rpm --repo "$REPO" \
  --dir /home/builder/localrepo \
  --pattern '*.rpm' --clobber 2>/dev/null \
  || echo "No repo-rpm release yet — building from a clean local repo."
chown -R builder /home/builder/localrepo

if [ -n "$(find /home/builder/localrepo -maxdepth 1 -name '*.rpm' 2>/dev/null)" ]; then
  su builder -c 'createrepo_c /home/builder/localrepo'
  cat > /etc/yum.repos.d/local-personal.repo <<'EOF'
[local-personal]
name=Personal OpenMandriva repo
baseurl=file:///home/builder/localrepo
enabled=1
gpgcheck=0
priority=1
EOF
  dnf makecache
fi

# rpmlint the spec before spending time on a build
echo "==> Linting spec"
su builder -c "rpmlint /home/builder/abf/$PKG/$PKG.spec" \
  || echo "==> rpmlint reported issues on the spec (non-fatal, see above)"

echo "==> Running abb build"
su builder -c "cd /home/builder/abf/$PKG && abb build"

mkdir -p "$OLDPWD/out" "$OLDPWD/merged"
find "/home/builder/abf/$PKG/RPMS" -name '*.rpm' -exec cp {} "$OLDPWD/out/" \;
cp /home/builder/localrepo/*.rpm "$OLDPWD/merged/" 2>/dev/null || true
find "/home/builder/abf/$PKG/RPMS" -name '*.rpm' -exec cp {} "$OLDPWD/merged/" \;

echo "==> Linting built RPMs"
rpmlint "$OLDPWD"/out/*.rpm \
  || echo "==> rpmlint reported issues on the built RPMs (non-fatal, see above)"

# De-duplicate merged/, keeping only the newest release of each package.
# NVRA parsing is approximate (name-version-release.dist.arch.rpm) —
# tighten the sed pattern if any of your package names contain digits
# right before a dash, the same caveat the xbps de-dup step has.
echo "==> De-duplicating merged/"
(
  cd "$OLDPWD/merged"
  ls *.rpm 2>/dev/null \
    | sed -E 's/-[^-]+-[^-]+\.[a-zA-Z0-9_]+\.rpm$//' \
    | sort -u \
    | while read -r base; do
        matches=$(ls -- "$base"-*.rpm 2>/dev/null)
        newest=$(printf '%s\n' "$matches" | sort -V | tail -n1)
        printf '%s\n' "$matches" | while read -r f; do
          [ "$f" = "$newest" ] && continue
          echo "==> Removing stale $f (superseded by $newest)"
          rm -f -- "$f"
        done
      done
)

createrepo_c "$OLDPWD/merged"

echo "==> Build complete. This run's packages in out/, full repo in merged/"
find "$OLDPWD/out" -name '*.rpm'
