%ifarch x86_64
# Workaround for the _Float32 confusion when using -Os
%global optflags -fomit-frame-pointer -gdwarf-4 -Wstrict-aliasing=2 -pipe -Wformat -Werror=format-security -O3 -m64 -mmmx -msse -mfpmath=sse -fdebug-types-section
%endif

%define _disable_ld_no_undefined 1
# Chromium buildmess uses its own LTO
%global _disable_lto 1

# eol 'fix' corrupts some .bin files
%define dont_fix_eol 1

#define v8_ver 3.12.8
%define crname chromium-browser
%define _crdir %{_libdir}/%{crname}
%define _src %{_topdir}/SOURCES
# For incomplete debug package support
%define _empty_manifest_terminate_build 0

%ifarch %ix86
%define _build_pkgcheck_set %{nil}
%endif

%bcond_without browser
# CEF embedding library (libcef + samples). Built in addition to the browser.
%bcond_without cef
# Use the internal libc++ instead of libstdc++
# This should usually be avoided because of potential symbol
# clashes when using e.g. Qt and Chromium at the same time
# (especially with cef!), but some versions of chromium make
# it necessary
# in 131.x, chromium with libstdc++ mostly works, but gets
# more "Aw, snap" errors than a libc++ build
%bcond_without libcxx

# FIXME As of 97.0.4688.2, Chromium crashes frequently when
# built with fortification enabled.
# [3784233:1:1107/202853.599120:ERROR:socket.cc(93)] sendmsg: Broken pipe (32)
# Received signal 11 <unknown> 03e900000001
#0 0x55af1960e344 (/usr/lib64/chromium-browser-dev/chrome+0x9071343)
#1 0x7fa28e947790 (/lib64/libc.so.6+0x4578f)
#2 0x7fa28e92e4f0 abort
#3 0x7fa28e98edc6 (/lib64/libc.so.6+0x8cdc5)
#4 0x7fa28ea386e2 __fortify_fail
#5 0x7fa28ea386b2 __stack_chk_fail
#6 0x55af1446e459 (/usr/lib64/chromium-browser-dev/chrome+0x3ed1458)
#7 0x7fa28e92fd8c (/lib64/libc.so.6+0x2dd8b)
#8 0x7fa28e92fe39 __libc_start_main
#9 0x55af140ab121 _start
# This should be investigated properly at some point.
%define _fortify_cflags %{nil}
%define _ssp_cflags %{nil}

# Libraries that should be unbundled (and reason why they
# aren't yet):
# openh264: Fails to compile
# icu: Causes crash when loading some websites, e.g.
#      build logs from abf, anti-spiegel.ru
# libvpx: Fails to compile
# re2 jsoncpp snappy: Use C++, therefore won't work while
#                     system uses libstdc++ but chromium
#                     uses use_custom_libcxx=true
# libaom (as of 118.x): Build error caused by GN insisting on in-tree version
# libwebp (as of 124.x): //third_party/libavif:libavif_enc(//build/toolchain/linux/unbundle:default) needs //third_party/libwebp:libwebp_sharpyuv(//build/toolchain/linux/unbundle:default)
# re2 (as of 124.x): //third_party/googletest:gtest_config(//build/toolchain/linux/unbundle:default) needs //third_party/re2:re2_config(//build/toolchain/linux/unbundle:default) (+ libc++/libstdc++ issue)
# zlib: Breaks extracting extensions
%if %{with libcxx}
# ffmpeg: system FFmpeg 9.x via build/linux/unbundle (no private libffmpeg.so).
# Avoids shipping Chromium's vendored fork and symbol clashes with apps that
# already link system libav* (e.g. OBS + obs-browser/CEF in one process).
%global system_libs fontconfig harfbuzz libjpeg libpng libdrm libxml libxslt opus libusb openh264 freetype zstd libwebp ffmpeg
%else
%global system_libs fontconfig harfbuzz libjpeg libpng libdrm libxml libxslt opus libusb openh264 freetype zstd libwebp jsoncpp snappy ffmpeg
# System absl is not quite working yet
# absl_algorithm absl_base absl_cleanup absl_container absl_crc absl_debugging absl_flags absl_functional absl_hash absl_log absl_log_internal absl_memory absl_meta absl_numeric absl_random absl_status absl_strings absl_synchronization absl_time absl_types absl_utility
%endif
%define system() %(if echo %{system_libs} |grep -q -E '(^| )%{1}( |$)'; then echo -n 1; else echo -n 0;  fi)

# Set up Google API keys, see http://www.chromium.org/developers/how-tos/api-keys
# OpenMandriva key, id and secret
# For your own builds, please get your own set of keys.
%define google_api_key AIzaSyAraWnKIFrlXznuwvd3gI-gqTozL-H-8MU
%define google_default_client_id 1089316189405-m0ropn3qa4p1phesfvi2urs7qps1d79o.apps.googleusercontent.com
%define google_default_client_secret RDdr-pHq2gStY4uw0m-zxXeo

Name:		helium
# CEF subpackages set Version: %{chromium} below. On this rpm, the last
# Version: tag becomes %{version} in scriptlets, so keep the Helium version
# in a separate macro and use it everywhere the browser (not CEF) version is meant.
%global helium_version 0.16.2
Version:	%{helium_version}
# https://chromiumdash.appspot.com/releases?platform=Linux
# Tested with helium: `cat chromium_version.txt`
# https://github.com/imputnet/helium/blob/main/chromium_version.txt
%define chromium 152.0.7977.64
%if %{with cef}
# To find the CEF commit matching the Chromium version, look up the
# right branch at
# https://chromiumembedded.github.io/cef/branches_and_building
# (Typically this will match the 3rd component of the version number)
# then check the commit for the branch at the branch download page,
# https://bitbucket.org/chromiumembedded/cef/downloads/?tab=branches
# or https://github.com/chromiumembedded/cef/tree/${BRANCH}
#
# Since we're using system libxml, we're potentially restoring
# https://github.com/chromiumembedded/cef/issues/3616 fixed in cef upstream.
# If we run into this problem, we need to either use custom libxml or build
# system libxml with TLS disabled.
# CEF 7977 branch tip matching Chromium 152.0.7977.x
# (b129680 tracks 152.0.7977.54; Helium is 152.0.7977.64).
%define cef b129680e4084ebea0429a1c289fb7c24ac604b36
%define cefversion %(echo %{chromium} |cut -d. -f3)
# make_distrib expects out/Release_GN_<arch>; CEF is built in out/Release-CEF.
%ifarch %{x86_64}
%define cef_gn_dir Release_GN_x64
%define cef_md_arch --x64-build
%else
%ifarch %{aarch64}
%define cef_gn_dir Release_GN_arm64
%define cef_md_arch --arm64-build
%else
%ifarch %{arm}
%define cef_gn_dir Release_GN_arm
%define cef_md_arch --arm-build
%else
%define cef_gn_dir Release_GN_x86
%define cef_md_arch %{nil}
%endif
%endif
%endif
%endif
Release:	1
Summary:	A fast, privacy friendly, web browser based on Ungoogled Chromium
Group:		Networking/WWW
License:	BSD, LGPL
# From : http://gsdview.appspot.com/chromium-browser-official/
Source0:	https://commondatastorage.googleapis.com/chromium-browser-official/chromium-%{chromium}-lite.tar.xz
Source1:	chromium-wrapper
Source2:	chromium-browser.desktop
Source3:	master_preferences
# https://bugs.freedesktop.org/show_bug.cgi?id=106490
# Workaround from Arch Linux
# https://aur.archlinux.org/cgit/aur.git/tree/chromium-drirc-disable-10bpc-color-configs.conf?h=chromium-vaapi
Source4:	chromium-drirc-disable-10bpc-color-configs.conf
%if 0%{?cef:1}
Source10:	https://github.com/chromiumembedded/cef/archive/refs/heads/%{cefversion}.tar.gz#/cef-%{cefversion}.tar.gz
Source11:	https://chromium-fonts.storage.googleapis.com/336e775eec536b2d785cc80eff6ac39051931286#/test_fonts.tar.gz
# pkg-config template for the system-library view of CEF (OnlyOffice tree stays under %%{_libdir}/cef).
Source12:	cef.pc.in
%endif
Source100:	%{name}.rpmlintrc
Source1000:	https://github.com/imputnet/helium/archive/refs/tags/%{helium_version}.tar.gz
# See deps.ini inside the helium tarball (Source1000) and keep in sync
Source1001:	https://github.com/imputnet/helium-nonfree-assets/releases/download/202607242007/nonfree-search-engines-data-202607242007.tar.gz
Source1002:	https://github.com/imputnet/helium-onboarding/releases/download/202608281912/helium-onboarding-202608281912.tar.gz
Source1003:	https://github.com/imputnet/uBlock/releases/download/1.74.0/uBlock0_1.74.0.chromium.zip

# ============================================================================
# Patches 0 to 1999 are applied in the top level Chromium directory
# after ungoogled-chromium and cef patchsets have been applied.
# ============================================================================
# "Borrowed" from other distros (note we don't copy all their patches,
# just the ones that make sense for OM -- in particular no slew of
# workarounds for prehistoric libraries and compilers):
### 0-99: Fedora
# https://src.fedoraproject.org/rpms/chromium/tree/rawhide
# Use /etc/chromium for master_prefs
Patch1:		https://src.fedoraproject.org/rpms/chromium/raw/rawhide/f/chromium-68.0.3440.106-master-prefs-path.patch
Patch2:		https://src.fedoraproject.org/rpms/chromium/raw/rawhide/f/chromium-67.0.3396.62-gn-system.patch
Patch3:		https://src.fedoraproject.org/rpms/chromium/raw/rawhide/f/chromium-103.0.5060.53-update-rjsmin-to-1.2.0.patch
# Use gn system files
%if %{system zlib}
# Do not mangle zlib
Patch4:		https://src.fedoraproject.org/rpms/chromium/raw/rawhide/f/chromium-77.0.3865.75-no-zlib-mangle.patch
%endif
Patch5:		chromium-147-rust-1.95.patch
# Needs to be submitted..
Patch6:		https://src.fedoraproject.org/rpms/chromium/raw/rawhide/f/chromium-107-proprietary-codecs.patch
# Disable whitelist, allow everything
#Patch7:		https://src.fedoraproject.org/rpms/chromium/raw/rawhide/f/chromium-122-disable-FFmpegAllowLists.patch
Patch8:		helium-fix-default-browser-setting-and-icon.patch

### 100-199: Arch
# https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=chromium-dev
# https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=chromium-wayland-vaapi

### 200-299: Gentoo
Patch200:	https://gitweb.gentoo.org/repo/gentoo.git/plain/www-client/chromium/files/chromium-124-libwebp-shim-sharpyuv.patch

### 300-399: Debian
# https://sources.debian.org/patches/chromium/
# Mostly fixes for libstdc++ related failures
Patch300:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/ps-print.patch
Patch301:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/widevine-locations.patch
# Not needed for OM
###		https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/rust-clanglib.patch
Patch302:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/material-utils.patch
Patch303:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/gentoo-stylesheet.patch
# Not needed for OM
###		https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/bindgen.patch
Patch304:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/memory-allocator-dcheck-assert-fix.patch
Patch305:	https://sources.debian.org/data/main/c/chromium/149.0.7827.102-1/debian/patches/fixes/armhf-icf.patch
Patch306:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/predictor-denial-of-service.patch
Patch307:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/fix-assert-in-vnc-sessions.patch
Patch308:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/armhf-timespec.patch
Patch309:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/updater-test.patch
# FIXME this is needed for libstdc++, but doesn't currently apply
#Patch310:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/font-gc-asan.patch
Patch311:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/libpng-testonly.patch
Patch314:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/headless-gn.patch
#Patch315:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/stdatomic.patch
Patch316:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/fixes/make-pair.patch
Patch324:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/debianization/swiftshader-use-llvm-16.patch
# (Mostly) duplicates from ungoogled patchset
###		https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/disable/tests.patch
Patch325:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/disable/tests-swiftshader.patch
# Already disabled by ungoogled patchset
###		https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/disable/signin.patch
#FIXME#Patch327:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/disable/catapult.patch
Patch328:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/disable/font-tests.patch
# Clashes with ungoogled patchset, probably not needed
###		https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/disable/google-api-warning.patch
# Already disabled in ungoogled patchset
###		https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/disable/third-party-cookies.patch
# MODIFIED by OM to apply on top of ungoogled tree
Patch329:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/disable/driver-chrome-path.patch
Patch330:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/disable/widevine-cdm-cu.patch
Patch331:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/disable/clang-version-check.patch
Patch332:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/disable/screen-ai-blob.patch
Patch333:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/system/icu-shim.patch
Patch334:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/system/jpeg.patch
Patch335:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/system/openjpeg.patch
Patch336:	https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/system/opus.patch
# Duplicate - but not sure where the other version comes from. Ungoogled?
###		https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/system/rapidjson.patch
# Incompatible with OM for now, since we don't have the system package
###		https://sources.debian.org/data/main/c/chromium/148.0.7778.96-1/debian/patches/system/rollup.patch

### 400-999: Patches from 3rd party projects that aren't distro packages
Patch401:	https://codeberg.org/selfisekai/copium/raw/branch/main/cr137-no-exec_script_allowlist.patch
Patch403:	https://codeberg.org/selfisekai/copium/raw/branch/main/cr138-node-version-check.patch
Patch407:	chromium-129-system-absl.patch
#Patch408:	chromium-129-libstdc++-buildfixes.patch
# https://gitlab.com/Matt.Jolly/chromium-patches
# [nothing currently relevant; make sure to check release branches, master branch is abandoned]
# https://github.com/ungoogled-software/ungoogled-chromium-fedora
# Not useful with the -lite tarball
#Patch411:	https://raw.githubusercontent.com/ungoogled-software/ungoogled-chromium-fedora/master/chromium-91.0.4472.77-java-only-allowed-in-android-builds.patch
# From OBS CEF fork
# https://github.com/obsproject/cef/commits/6261-shared-textures
Patch420:	https://github.com/obsproject/cef/commit/27e977332df56c6251f4ee418d6bd51be073767d.patch
Patch421:	https://github.com/obsproject/cef/commit/f88220be4c4c02db5f9f0170dfc515d86a6f0c48.patch

### 1000+: Our own patches
Patch1001:	chromium-64-system-curl.patch
Patch1002:	chromium-69-no-static-libstdc++.patch
Patch1003:	chromium-system-zlib.patch
Patch1004:	chromium-107-system-libs.patch
# Drop Chromium-private AVFMT_FLAG_NOH264PARSE when using system FFmpeg.
%if %{system ffmpeg}
Patch1005:	chromium-system-ffmpeg-no-noh264parse.patch
# System FFmpeg decoder names differ from Chromium's fork (opus vs libopus,
# mp3float vs mp3). Without this, avcodec_open2 rejects YouTube Opus and
# HTML5 MP3.
Patch1009:	chromium-system-ffmpeg-runtime.patch
%endif
# JPEG XL: Chromium 151+ decodes via the Rust jxl crate (third_party/rust/jxl),
# not C libjxl. enable_jxl_decoder defaults to true; we set it explicitly in
# openmandriva.gn_args. The old chromium-restore-jpeg-xl-support.patch (C API +
# vendored libjxl) is obsolete and must not be reintroduced.
Patch1006:	chromium-extra-widevine-search-paths.patch
Patch1007:	chromium-116-dont-override-thinlto-cache-policy.patch
Patch1008:	chromium-116-system-brotli.patch
Patch1010:	chromium-132-system-toolchain.patch
Patch1011:	perfetto-system-gn.patch
%if %{system zlib}
Patch1012:	chromium-105-minizip-ng.patch
%endif
Patch1013:	chromium-132-compile.patch
Patch1014:	chromium-150-partition-alloc-stub.patch
Patch1053:	chromium-150-skcms-avx512-flags.patch
# Clang 23 ICE on aarch64 if -fmodule-name=* _Private is on every cxx command
# while use_clang_modules=false (ABF 653532, 653753).
Patch1054:	chromium-151-no-fmodule-name-without-modules.patch
Patch1015:	chromium-147-clang22-no-no-lifetime-dse.patch
Patch1016:	chroimum-119-workaround-crash-on-startup.patch
# More and better search engines
# https://bugs.chromium.org/p/chromium/issues/detail?id=1502905
# FIXME needs porting, currently seems to cause crash on first startup
#Patch1017:	chromium-124-search-engine-choice.patch
Patch1018:	chromium-81-unbundle-zlib.patch
Patch1019:	chromium-121-rust-clang_lib.patch
# https://issues.chromium.org/issues/403871216
Patch1020:	chromium-135-bug-403871216.patch
Patch1021:	chromium-127-system-bindgen.patch
Patch1022:	chromium-115-fix-generate_fontconfig_caches.patch
%if %{system zlib}
Patch1024:	chromium-127-minizip-ng.patch
%endif
# https://issues.chromium.org/issues/381407882
Patch1030:	chromium-133-workaround-bug-381407882.patch
Patch1031:	chromium-148-qt-printing.patch
# Qt native file dialogs when XDG portals are unavailable (no GTK fallback).
Patch1032:	chromium-150-qt-file-dialog.patch
# Qt LinuxUi must not construct GtkUi as a fallback (dlopen + gtk_init_check).
Patch1033:	chromium-151-qt-no-gtk-fallback.patch
Patch1040:	chromium-134-drop-workarounds-for-ancient-mesa-bugs.patch
Patch1041:	chromium-134-drop-workarounds-for-ancient-mesa-bugs-part2.patch
Patch1042:	chromium-134-if-chromeos-can-do-it-so-can-linux.patch
#Patch1044:	chromium-136-no-unknown-clang-flag.patch
Patch1047:	chromium-system-bindgen.patch
# Keeping the source here for now, just in case we need to backport
# to 6.0 or something else that has old python
# Not applying it anymore though.
#Patch1048:	ublock-python-3.11.patch
# The default is "more secure", but to the point where it breaks
# things -- showing both interfaces makes Jitsi work.
# Having it actually working is more important than hiding network
# infrastructure.
Patch1049:	helium-webrtc-default-to-publicandprivateinterfaces.patch
Patch1050:	dont-assume-system-rust-is-prehistoric.patch
Patch1051:	chromium-149-no-flags-for-unreleased-clang.patch
Patch1052:	chromium-148-fix-build-without-ubsan.patch
# Do not offer Helium's crash-report dialog for GPU-process dumps written
# while probing Vulkan. The GPU process is still allowed to crash and fall
# back; Vulkan stays enabled for hardware where it works.
Patch1055:	helium-hide-gpu-probe-crash-notification.patch
# Ozone/Wayland cannot use native Vulkan. Decline it silently and keep
# --ozone-platform=wayland; X11 still gets Vulkan by default.
Patch1056:	helium-wayland-ozone-silent-no-vulkan.patch
# Chromium 152 CBOR depends on Crubit (bundled rust-toolchain). System rust
# sets rust_sysroot_absolute and enable_cpp_api_from_rust=false; keep the
# C++ CBOR path and do not load rust-toolchain Crubit BUILD.gn files.
Patch1057:	chromium-152-cbor-no-crubit-without-chromium-rust.patch

# ============================================================================
# Patches 2000 to 2999 are applied inside the CEF tree.
# ============================================================================
# Rebase CEF's chromium patchset so it applies on top of Helium/ungoogled
# (domain substitution in nested CEF patches, drop libxml_visibility for
# system libxml, chrome_runtime_views ctor/dtor vs zen-mode + shortcut
# service, crashpad_1995 vs Helium crash-key sanitization / versioning).
Patch2000:	cef-7977-helium-patch-rebase.patch
# Incomplete type content::WebContents after Chromium include cleanup
# (CEF file_dialog_manager.cc needs the full web_contents.h).
Patch2001:	cef-7871-web_contents-include.patch
Patch2002:	cef-126-zlib-ng.patch
# Qt cefclient sample + host libstdc++ wrapper (applied inside cef/).
Patch2003:	cef-7977-qt-cefclient.patch
# Soften CEF nested-patch apply for Helium tree (patch --fuzz=3; no git apply).
Patch2004:	cef-patcher-fuzz.patch

# ============================================================================
# Patches 3000+ are from the various chromium upstream repositories
# and applied inside their respective directories.
# ============================================================================

# ============================================================================
# Patches 4000+ are applied inside the helium tree before
# the ungoogling scripts are run
# ============================================================================

Provides:	%{crname}
Obsoletes:	chromium-browser-unstable < %{EVRD}
Obsoletes:	chromium-browser < %{EVRD}
BuildRequires:	glibc-static-devel
BuildRequires:	gperf
BuildRequires:	bison
BuildRequires:	re2c
BuildRequires:	flex
BuildRequires:	git
BuildRequires:	rust
BuildRequires:	rustfmt
BuildRequires:	rust-bindgen-cli
# Dawn/tint generate-sources-gn.py runs tools/golang/<cipd-plat>/bin/go; the
# lite tarball omits the CIPD golang package (Absent: third_party/dawn/tools/golang/).
BuildRequires:	golang
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(krb5)
BuildRequires:	pkgconfig(libunwind)
BuildRequires:	pkgconfig(com_err)
BuildRequires:	alsa-oss-devel
BuildRequires:	atomic-devel
BuildRequires:	snappy-devel
BuildRequires:	jsoncpp-devel
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(wayland-egl)
BuildRequires:	pkgconfig(nss)
BuildRequires:	pkgconfig(gbm)
BuildRequires:	pkgconfig(libglvnd)
BuildRequires:	pkgconfig(libva)
BuildRequires:	pkgconfig(libva-drm)
BuildRequires:	pkgconfig(libva-glx)
BuildRequires:	pkgconfig(libva-x11)
BuildRequires:	pkgconfig(dri)
BuildRequires:	pkgconfig(Qt6Core)
BuildRequires:	pkgconfig(Qt6DBus)
BuildRequires:	pkgconfig(Qt6Gui)
BuildRequires:	pkgconfig(Qt6Widgets)
BuildRequires:	pkgconfig(Qt6OpenGL)
BuildRequires:	pkgconfig(Qt6PrintSupport)
BuildRequires:	pkgconfig(RapidJSON)
BuildRequires:	pkgconfig(xkbcommon)
BuildRequires:	pkgconfig(atspi-2)
BuildRequires:	pkgconfig(atk)
BuildRequires:	pkgconfig(atk-bridge-2.0)
BuildRequires:	pkgconfig(gtk+-3.0)
BuildRequires:	pkgconfig(gtk4)
BuildRequires:	pkgconfig(pangocairo)
BuildRequires:	pkgconfig(libopenjp2)
BuildRequires:	pkgconfig(libpipewire-0.3)
BuildRequires:	pkgconfig(libinput)
BuildRequires:	pkgconfig(epoxy)
BuildRequires:	pkgconfig(xcomposite)
BuildRequires:	pkgconfig(xdamage)
BuildRequires:	%{_lib}GL-devel
BuildRequires:	bzip2-devel
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	clang lld
%if %{system brotli}
BuildRequires:	pkgconfig(libbrotlicommon)
BuildRequires:	pkgconfig(libbrotlidec)
BuildRequires:	pkgconfig(libbrotlienc)
BuildRequires:	brotli
%endif
%if %{system ffmpeg}
BuildRequires:	pkgconfig(libavcodec)
BuildRequires:	pkgconfig(libavfilter)
BuildRequires:	pkgconfig(libavformat) >= 57.41.100
BuildRequires:	pkgconfig(libavutil)
%endif
%if %{system flac}
BuildRequires:	pkgconfig(flac)
%endif
%if %{system fontconfig}
BuildRequires:	pkgconfig(fontconfig)
%endif
%if %{system harfbuzz}
BuildRequires:	harfbuzz-devel
%endif
%if %{system icu}
BuildRequires:	pkgconfig(icu-i18n)
%endif
%if %{system libaom}
BuildRequires:	pkgconfig(aom)
%endif
%if %{system libdrm}
BuildRequires:	pkgconfig(libdrm)
%endif
%if %{system libjpeg}
BuildRequires:	jpeg-devel
%endif
%if %{system libjxl}
BuildRequires:	pkgconfig(libjxl)
%endif
%if %{system libpng}
BuildRequires:	pkgconfig(libpng)
%endif
%if %{system libusb}
BuildRequires:	pkgconfig(libusb-1.0)
%endif
%if %{system libvpx}
BuildRequires:	pkgconfig(vpx)
%endif
%if %{system libwebp}
BuildRequires:	pkgconfig(libwebp)
%endif
%if %{system libxml}
BuildRequires:	pkgconfig(libxml-2.0)
%endif
%if %{system libxslt}
BuildRequires:	pkgconfig(libxslt)
%endif
%if %{system opus}
BuildRequires:	pkgconfig(opus)
%endif
%if %{system openh264}
BuildRequires:	pkgconfig(openh264)
%endif
# FIXME as of 0.7.1, re2 headers seem to be required even when
# not using system re2. This is clearly a build system bug, but
# as long as the 2 versions are in sync, won't break things badly
#if system re2
BuildRequires:	pkgconfig(re2)
#endif
%if %{system zlib}
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(minizip)
%endif
BuildRequires:	pkgconfig(nspr)
BuildRequires:	pkgconfig(xscrnsaver)
BuildRequires:	pkgconfig(xshmfence)
BuildRequires:	pkgconfig(glu)
BuildRequires:	pkgconfig(gl)
BuildRequires:	cups-devel
BuildRequires:	pkgconfig(dbus-glib-1)
BuildRequires:	pkgconfig(libsystemd)
BuildRequires:	pkgconfig(gnome-keyring-1)
BuildRequires:	pam-devel
BuildRequires:	pkgconfig(xtst)
BuildRequires:	pkgconfig(libpulse)
BuildRequires:	pkgconfig(xt)
BuildRequires:	cap-devel
BuildRequires:	elfutils-devel
BuildRequires:	pkgconfig(gnutls)
BuildRequires:	pkgconfig(udev)
BuildRequires:	pkgconfig(speex)
BuildRequires:	pkgconfig(lcms2)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(snappy)

BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(protobuf)
BuildRequires:	python%{pyver}dist(protobuf)
BuildRequires:	python%{pyver}dist(markupsafe)

BuildRequires:	yasm
BuildRequires:	speech-dispatcher-devel
BuildRequires:	pkgconfig(libpci)
BuildRequires:	pkgconfig(libexif)
BuildRequires:	ninja
BuildRequires:	nodejs
BuildRequires:	jdk-current

Recommends: (%{name}-qt6 = %{EVRD} if %{_lib}Qt6Gui)

%description
Helium is a browser that combines a focus on privacy
with a minimal design and sophisticated technology to
make the web faster, safer, and easier.

Based on Ungoogled Chromium, it is highly compatible
with the latest versions of Chrome, but without feeding
your data to Google.

%package qt6
Summary: Qt 6.x integration for Helium
Group: System/Libraries
Requires: %{name} = %{EVRD}
Obsoletes: chromium-browser-stable-qt6
Obsoletes: %{name}-qt5 < %{EVRD}

%description qt6
Qt 6.x integration for Helium

%package -n cef-qt6
Version: %{chromium}
Summary: Qt 6.x integration for CEF
Group: System/Libraries
Requires: cef = %{EVRD}
Supplements: cef = %{EVRD}
Obsoletes: cef-qt5 < %{EVRD}

%description -n cef-qt6
Qt 6.x integration for CEF

%if 0%{?cef:1}
%package -n cef
Version: %{chromium}
Summary: Chromium Embedded Framework - library for embeddind Chromium in custom applications
# FIXME cef hardcodes a gtk dependency somewhere. It should
# really be dropped in favor of Qt
BuildRequires: pkgconfig(gtk+-3.0)
BuildRequires: pkgconfig(gtk+-unix-print-3.0)
Group: System/Libraries

%description -n cef
Chromium Embedded Framework - library for embeddind Chromium in custom applications

%package -n cef-devel
Version: %{chromium}
Summary: Chromium Embedded Framework - library for embeddind Chromium in custom applications
Group: Development/Libraries
Requires: cef = %{EVRD}

%description -n cef-devel
Chromium Embedded Framework - library for embedding Chromium in custom
applications. Provides both the OnlyOffice/OBS-style tree under
%{_libdir}/cef and a normal system layout (headers in %{_includedir}/cef,
libcef.so / libcef_dll_wrapper.a symlinks in %{_libdir}, and pkg-config
files cef.pc / libcef.pc) for ordinary build systems.

# Prebuilt sample apps (GTK + Qt). Optional demos / smoke tests; not required
# for embedding. Sources remain in cef-devel under tests/.
%package -n cef-examples
Version: %{chromium}
Summary: Sample applications for the Chromium Embedded Framework (GTK and Qt)
Group: Development/Other
Requires: cef = %{EVRD}
# Qt sample needs the CEF Qt shim; GTK sample is fine with it installed too.
Requires: cef-qt6 = %{EVRD}
# GTK/Qt library deps are picked up automatically from the ELF binaries.

%description -n cef-examples
Prebuilt cefclient (GTK) and cefclient_qt sample browsers that embed libcef.
Useful for testing the CEF stack and as a reference for embedding into GTK or
Qt applications. Library headers, the C++ wrapper, and sample sources live in
cef-devel.
%endif

%package chromedriver
Summary:	WebDriver for Google Chrome/Chromium
Group:		Development/Other
Requires:	%{name} = %{helium_version}-%{release}

%description chromedriver
WebDriver is an open source tool for automated testing of webapps across many
browsers. It provides capabilities for navigating to web pages, user input,
JavaScript execution, and more. ChromeDriver is a standalone server which
implements WebDriver's wire protocol for Chromium. It is being developed by
members of the Chromium and WebDriver teams.

%prep
# Not using %%autosetup so we can apply patches after
# ungoogled-chromium patches have been applied
%setup -q -n chromium-%{chromium} -a 1000

HEDIR=$(pwd)/helium-%{helium_version}
mkdir -p third_party/search_engines_data/resources_internal
cd third_party/search_engines_data/resources_internal
tar xf %{S:1001}
cd ../../..
mkdir -p components/helium_onboarding
cd components/helium_onboarding
tar xf %{S:1002}
cd ../..
mkdir -p third_party/ublock
cd third_party/ublock
tar x --strip-components=1 -f %{S:1003}
cd ../..
cd $HEDIR
%autopatch -p1 -m 4000
cd ..
echo %{helium_version} >$HEDIR/chromium_version.txt
# Disable a few patches: We don't want to allow Google to spy on our
# users, but we don't want to prevent users from voluntarily using
# Google services.
# Also, disable some security-for-usability tradeoffs by default
sed -i \
	-e '/disable-autofill/d' \
	-e '/prefs-only-keep-cookies-until-exit/d' \
	-e '/XXXdisable-webstore-urls.patch/d' \
	$HEDIR/patches/series
python $HEDIR/utils/prune_binaries.py ./ $HEDIR/pruning.list --verbose || :
python $HEDIR/utils/patches.py apply ./ $HEDIR/patches
python $HEDIR/utils/domain_substitution.py apply -r $HEDIR/domain_regex.list -f $HEDIR/domain_substitution.list -c domainsubcache.tar.gz ./

%if 0%{?cef:1}
tar xf %{S:10}
mv cef-* cef
# CEF tools (make_distrib, version_manager) expect a git checkout of CEF.
# Do not git-init the Chromium tree: a bare init makes CEF's patcher use
# strict `git apply`, which fails against Helium/ungoogled context shifts.
# Without Chromium .git the patcher falls back to patch(1) (see cef-patcher-fuzz).
cd third_party/pdfium ; git init; cd ../..
cd cef; git init; cd ..
cd cef
%autopatch -p1 -m 2000 -M 2999
COMMIT_NUMBER=%(echo %{helium_version} |cut -d. -f3) COMMIT_HASH=%{cef} python tools/make_version_header.py include/cef_version.h --cef_version VERSION.in --chrome_version ../chrome/VERSION --cpp_header_dir include
cd ..

cd third_party/test_fonts
tar xf %{S:11}
cd ../..
%endif

%autopatch -p1 -M 1999

cd third_party/webrtc
%autopatch -p1 -m 3000 -M 3009
cd -
cd media
%autopatch -p1 -m 3010 -M 3019
cd -

rm -rf third_party/binutils/
# Get rid of the pre-built eu-strip binary, it is x86_64 and of mysterious origin
#rm -rf buildtools/third_party/eu-strip/bin/eu-strip
  
# Replace it with a symlink to the system copy
#ln -s %{_bindir}/eu-strip buildtools/third_party/eu-strip/bin/eu-strip

echo "%{revision}" > build/LASTCHANGE.in

#sed -i 's!-nostdlib++!!g'  build/config/posix/BUILD.gn
sed -i 's!ffmpeg_buildflags!ffmpeg_features!g' build/linux/unbundle/ffmpeg.gn

# Allow building against system libraries in official builds
sed -i 's/OFFICIAL_BUILD/GOOGLE_CHROME_BUILD/' \
	tools/generate_shim_headers/generate_shim_headers.py

# Blink generate_bindings.py fans out to multiprocessing.cpu_count() workers.
# On high-core ABF builders that collides with ninja -j and OOM-kills the pool
# (aarch64 build_lists 630579 and 648862: FAILED generate_bindings_interface
# code=267, leaked multiprocessing semaphores). A RAM-based cap of 16 is still
# too high next to ninja -j and thin LTO; keep a small fixed pool.
_blink_tq=third_party/blink/renderer/bindings/scripts/bind_gen/task_queue.py
%ifarch %{aarch64}
_blink_bind_workers=2
%else
_blink_bind_workers=4
%endif
if ! grep -q 'self._pool_size = multiprocessing.cpu_count()' ${_blink_tq}; then
	echo "ERROR: blink TaskQueue pool_size assignment changed; update helium.spec"
	exit 1
fi
sed -i "s/self\._pool_size = multiprocessing\.cpu_count()/self._pool_size = min(multiprocessing.cpu_count(), ${_blink_bind_workers})/" \
	${_blink_tq}

%if ! %{with libcxx}
# Get rid of internal libc++ headers to make sure they aren't accidentally
# used instead of their libstdc++ counterparts
rm -rf third_party/libc++ third_party/libc++abi
%endif

# Extra version info is copied from the environment
export CHROME_VERSION_EXTRA="%{product_vendor} %{product_version}"

# use the system nodejs
mkdir -p third_party/node/linux/node-linux-x64/bin
ln -sfn /usr/bin/node third_party/node/linux/node-linux-x64/bin/
sed -i -e "s,^NODE_VERSION=.*,NODE_VERSION=\"v%(rpm -q --qf '%%{VERSION}' nodejs)\"," third_party/node/update_node_binaries

# Dawn tint code generation (//third_party/dawn/src/tint:generate_sources) runs
# tools/golang/<cipd>/bin/go. Point the CIPD layout at the system GOROOT so
# generate-sources-gn.py finds a working go (lite tarball has no CIPD golang).
mkdir -p third_party/dawn/tools/golang
%ifarch %{aarch64}
ln -sfn /usr/lib/golang third_party/dawn/tools/golang/linux-arm64
%else
ln -sfn /usr/lib/golang third_party/dawn/tools/golang/linux-amd64
%endif

# Remove bundled libs
# We could use build/linux/unbundle/remove_bundled_libraries.py here, but
# that requires listing the (much bigger set of) remaining libraries and
# pulls in yet another python2 dep -- so let's use the trick found in the
# Arch PKGBUILD file instead
for lib in %{system_libs}; do
	# Fix mismatch between name and directory name
	[ "$lib" = "libjpeg" ] && lib="libjpeg_turbo"
	if echo $lib |grep -q ^absl_; then
		continue
	fi
	find "third_party/$lib" -type f \
		\! -path "third_party/$lib/chromium/*" \
		\! -path "third_party/$lib/google/*" \
		\! -path "third_party/harfbuzz/utils/hb_scoped.h" \
		\! -regex '.*\.\(gn\|gni\|isolate\)' \
		-delete
done
python build/linux/unbundle/replace_gn_files.py \
	--system-libraries %{system_libs}
# Forcing an outdated copy of what should really match system headers
# is just about as dumb as something can get
cp -f %{_includedir}/wayland-client-core.h third_party/wayland/src/src/

# workaround build failure
if [ ! -f chrome/test/data/webui/i18n_process_css_test.html ]; then
	touch chrome/test/data/webui/i18n_process_css_test.html
fi

# third_party/ublock (Helium) generates a file manifest and puts it into code,
# %%autosetup's backup files should not show up there
find third_party/ublock -name "*.*~" |xargs rm -f

# FIXME third_party/rust-toolchain has been removed in 132,
# but at least one reference to rust-toolchain/bin/bindgen
# is hardcoded in gn files
# check if still necessary after update
mkdir -p third_party/rust-toolchain/bin
ln -sf %{_bindir}/bindgen third_party/rust-toolchain/bin/

# Fix placeholders for version information
sed -i -e 's,@HELIUM_MAJOR@.@HELIUM_MINOR@.@HELIUM_PATCH@,%{helium_version},g' base/version_info/version_info_values.h.version
sed -i -e 's,@HELIUM_PLATFORM@,OpenMandriva,g' base/version_info/version_info_values.h.version

%build
HEDIR=$(pwd)/helium-%{helium_version}

# Dual browser+CEF needs tens of GB for out/*/obj. ABF znver1 builders have hit
# ENOSPC mid-link (build_list 632620: code_cache_generator / v8_context_snapshot
# linker exit -2, then OSError errno 28). Free only build-tree throwaways —
# never %{_sourcedir} (needed for .src.rpm / rpmbuild -ba).
df -h . 2>/dev/null || :
# domainsubcache is created in %prep and not needed after domain substitution.
rm -f domainsubcache.tar.gz 2>/dev/null || :
# Docs are not compiled; drop to free a bit more space before ninja.
rm -rf docs 2>/dev/null || :
df -h . 2>/dev/null || :

. %{_sysconfdir}/profile.d/90java.sh

%ifarch %{arm}
# Use linker flags to reduce memory consumption on low-mem architectures
mkdir -p bfd
ln -sfn %{_bindir}/ld.bfd bfd/ld
export PATH=$PWD/bfd:$PATH
# Use linker flags to reduce memory consumption
%global ldflags %{ldflags} -fuse-ld=bfd -Wl,--no-keep-memory -Wl,--reduce-memory-overheads
%endif
%ifarch %{ix86}
# Workaround for build failure
%global ldflags %{ldflags} -Wl,-z,notext
%endif
%global optflags %(echo %{optflags} -fdebug-types-section | sed -e 's/-g3 //')
%global optflags %{optflags} -I%{_includedir}/libunwind

# Chromium builds tend to barf if not told precisely what to use
export CC="%{_bindir}/gcc"
export CXX="%{_bindir}/g++"
export AR="%{__ar}"
export NM="%{_bindir}/llvm-nm"

_lto_cpus="$(getconf _NPROCESSORS_ONLN)"
if [ $_lto_cpus -gt 4 ]; then
	# LTO is very memory intensive, so
	# 32 parallel LTO jobs may not be
	# a good idea...
	_lto_cpus=4
fi

# FIXME error: the option `Z` is only accepted on the nightly compiler
export RUSTC_BOOTSTRAP=1

%if "%{_lib}" != "lib"
# Something hardcodes ../../[...]/usr/lib as LIBCLANG_PATH
# which of course doesn't catch lib64 and friends...
#sed -i -e "s,args.libclang_path,'%{_libdir}',g" build/rust/run_bindgen.py
sed -i -e 's,/lib,/%{_lib},g' build/rust/rust_bindgen.gni
sed -i -e 's,/lib/clang/,/lib64/clang/,g' buildtools/third_party/libc++/modules.gni third_party/openscreen/src/buildtools/third_party/libc++/BUILD.gn
%endif

# We use our version of clang, regardless of what upstream wants
sed -i -E 's,(clang_version.*= *)".*,\1"23",' build/toolchain/toolchain.gni

# Fix reference to a header that doesn't exist
sed -i -e "s,#include \"gpu/webgpu/dawn_commit_hash.h\",#define DAWN_COMMIT_HASH \"$(cat gpu/webgpu/DAWN_VERSION)\"," components/viz/host/gpu_host_impl.cc

cat >openmandriva.gn_args <<EOF
use_sysroot=false
# PartitionAlloc-Everywhere (as malloc) fights snmalloc; keep PA itself
# available so Blink/base dump providers that need USE_PARTITION_ALLOC build.
# Chromium 150 fails partition_alloc_memory_dump_provider.cc without this.
use_partition_alloc=true
use_partition_alloc_as_malloc=false
# BRP/dangling-ptr features need PA-E; leave off while as_malloc is false
enable_backup_ref_ptr_support=false
enable_dangling_raw_ptr_checks=false
use_allocator_shim=false
is_debug=false
is_clang=true
# FIXME at some point, instead of disabling modules, fix them.
# The problem is that the C++ modules (see build/modules/linux-x64/module.modulemap)
# hardcode references to Chromium's Debian sysroot instead of system headers.
# see build/modules/modularize/README.md for instructions on rebuilding
use_clang_modules=false
# Chromium 150 defaults use_unified_system_module=true on linux and then
# rebase_path(sysroot) in build/modules/BUILD.gn; with use_sysroot=false
# that is an empty path and gn gen dies with Empty directory path.
use_unified_system_module=false
#use_autogenerated_modules=true
clang_base_path="%{_prefix}"
clang_use_chrome_plugins=false
node_version_check=false
treat_warnings_as_errors=false
%if %{with libcxx}
use_custom_libcxx=true
%else
use_custom_libcxx=false
%endif
EOF
for i in %{system_libs}; do
	# ffmpeg is unbundled by replace_gn_files.py (third_party/ffmpeg/BUILD.gn
	# becomes the system shim). There is no use_system_ffmpeg GN arg.
	[ "$i" = ffmpeg ] && continue
	echo use_system_$i=true >>openmandriva.gn_args
done
if ! echo %{system_libs} |grep -q icu; then
	echo icu_use_data_file=true >>openmandriva.gn_args
fi
cat >>openmandriva.gn_args <<EOF
use_system_lcms2=true
use_system_libffi=true
use_system_libopenjpeg2=true
# We don't currently ship libsync
#use_system_libsync=true
use_system_libwayland=true
use_system_libwayland_client=true
use_system_libwayland_server=true
use_system_lua=true
use_system_minigbm=true
use_system_openjpeg2=true
use_system_protobuf=true
use_system_wayland=true
use_system_wayland_client=true
use_system_wayland_scanner=true
use_system_wayland_server=true
use_xkbcommon=true
enable_vulkan=true
use_vulkan=true
angle_enable_vulkan=true
angle_enable_swiftshader=true
skia_use_dawn=true
use_dawn=true
use_gtk=true
gtk_version=4
use_qt5=false
use_qt6=true
moc_qt6_path="%{_qtdir}/libexec"
fatal_linker_warnings=false
system_libdir="%{_libdir}"
# use_aura=true
# use_gio=true
proprietary_codecs=true
ffmpeg_branding="ChromeOS"
enable_mse_mpeg2ts_stream_parser=true
%ifarch %{ix86}
target_cpu="x86"
%endif
%ifarch %{x86_64}
target_cpu="x64"
%endif
%ifarch %{arm}
target_cpu="arm"
remove_webcore_debug_symbols=true
%endif
%ifarch %{armx}
rtc_build_with_neon=true
%endif
%ifarch %{aarch64}
target_cpu="arm64"
# if this is true (default for non official builds) it tries to use
# a prebuilt x86 binary in the source tree
devtools_skip_typecheck=false
%endif
%if 0
google_api_key="%{google_api_key}"
google_default_client_id="%{google_default_client_id}"
google_default_client_secret="%{google_default_client_secret}"
%endif
use_lld=true
%ifarch %{x86_64} %{aarch64}
# x86_64: ThinLTO OOMs / ENOSPC on multi-GB chrome links.
# aarch64: ThinLTO merges DWARF32 until lld fails LINK chrome with
# R_AARCH64_ABS32 out of range in .debug_info (ABF 648862, 649252).
# Chromium asserts if concurrent_links is set together with use_thin_lto
# (aarch64 638819), so only set it when ThinLTO is off.
thin_lto_enable_optimizations=false
use_thin_lto=false
is_cfi=false
concurrent_links=2
%else
thin_lto_enable_optimizations=true
use_thin_lto=true
%endif
custom_toolchain="//build/toolchain/linux/unbundle:default"
host_toolchain="//build/toolchain/linux/unbundle:default"
v8_snapshot_toolchain="//build/toolchain/linux/unbundle:default"
symbol_level=0

use_pulseaudio=true
link_pulseaudio=true
# With system ffmpeg (unbundle), there is no private libffmpeg.so component.
# Keep this false so installers/tests do not expect a chrome-dir libffmpeg.so.
is_component_ffmpeg=false
enable_hangout_services_extension=true
enable_widevine=true
use_vaapi=true
use_ozone=true
angle_link_glx=true
angle_test_enable_system_egl=true
enable_hevc_parser_and_hw_decoder=true
enable_av1_decoder=true
# JPEG XL image decoding (Blink). Uses Chromium's Rust jxl crate, not system
# libjxl. Default is true since Chromium 151; set explicitly for clarity.
enable_jxl_decoder=true
enable_media_drm_storage=true
%ifarch znver1
# This really is znver1 only, as it enables SSE4.2, BMI2 and AVX2
enable_perfetto_x64_cpu_opt=true
%endif
# Chromium 150 always adds -fmodule-name=..._Private to cxx/cc tool
# commands (gcc_toolchain.gni). That flag makes clang treat -x c++-header
# PCH units as module interface units, which fail with:
#   error: missing 'export module' declaration in module interface unit
# Upstream already defaults PCH off on Linux (and for official builds);
# keep it off rather than fighting the new module flags.
enable_precompiled_headers=false
is_official_build=true
# Errors out because it pretends to be ChromeOS only, but should actually work...
# FIXME try removing the assert in ui/ozone/platform/drm/BUILD.gn
#ozone_platform_drm=true
perfetto_use_system_zlib=true
rtc_link_pipewire=true
rtc_use_pipewire=true
use_libinput=true
use_real_dbus_clients=true
use_vaapi_image_codecs=true
rust_sysroot_absolute="%{_prefix}"
rust_bindgen_root="%{_prefix}"
# 107: Build failure: GN_DEFINES+=" enable_wayland_server=true"
# 124: Fails with 
# ld.lld: error: undefined symbol: google::protobuf::compiler::CodeGenerator::GenerateAll(std::__Cr::vector<google::protobuf::FileDescriptor const*, std::__Cr::allocator<google::protobuf::FileDescriptor const*>> const&, std::__Cr::basic_string<char, std::__Cr::char_traits<char>, std::__Cr::allocator<char>> const&, google::protobuf::compiler::GeneratorContext*, std::__Cr::basic_string<char, std::__Cr::char_traits<char>, std::__Cr::allocator<char>>*) const
# >>> referenced by ld-temp.o
# (probably hardcoded use of bundled headers somewhere...)
# perfetto_use_system_protobuf=true
use_v4lplugin=true
# Can't use vaapi and v4l2_codec at the same time, there is no
# selection at runtime
#use_v4l2_codec=true
use_webaudio_ffmpeg=true
EOF
echo rustc_version=\"$(rustc --version | awk '{ print $2; }')\" >>openmandriva.gn_args #" (the trailing #" is a workaround for a neovim syntax highlighting bug)

# -gdwarf-4 is for the sake of debugedit
# https://sourceware.org/bugzilla/show_bug.cgi?id=29773
if %{__cc} --version 2>/dev/null | head -1 | grep -qi clang || echo %{__cc} | grep -qi clang; then
	export CFLAGS="%{optflags} -Qunused-arguments -fPIE -fpie -fPIC -gdwarf-4"
	export CXXFLAGS="%{optflags} -Qunused-arguments -fPIE -fpie -fPIC -gdwarf-4"
	if echo %{optflags} |grep -qE -- '-O[sz]'; then
		# FIXME this should get a real fix
		# _Float32 acts up with -Os/-Oz [at compile time]
		export CFLAGS="$CFLAGS -O2"
		export CXXFLAGS="$CXXFLAGS -O2"
	fi
	export LDFLAGS="%{build_ldflags} -Wl,--thinlto-jobs=$_lto_cpus"
	export AR="%{_bindir}/llvm-ar"
	export NM="%{_bindir}/llvm-nm"
	export RANLIB="%{_bindir}/llvm-ranlib"
else
	export CFLAGS="%{optflags}"
	export CXXFLAGS="%{optflags}"
fi
export CC="%{__cc}"
export CXX="%{__cxx}"

# Distro -march/-m* flags are kept.  skcms AVX-512 TUs use explicit
# -mavx512* (see chromium-150-skcms-avx512-flags.patch) so they still work
# when $CFLAGS ends with -march=znver1 (which would otherwise override
# -march=x86-64-v4).  Perfetto/abseil also need the distro SSSE3/BMI2 flags.

# Chromium 150+: gcc_toolchain.gni rebases the ar path for ninja inputs.
# Loading //build/toolchain/linux/unbundle evaluates both the "default"
# and "host" toolchains; the latter reads BUILD_* via getenv().  Empty
# BUILD_AR yields: ERROR Empty directory path at gcc_toolchain.gni.
# For a native (non-cross) build, mirror the target tools into BUILD_*.
export BUILD_CC="$CC"
export BUILD_CXX="$CXX"
export BUILD_AR="${AR:-%{_bindir}/ar}"
export BUILD_NM="${NM:-%{_bindir}/nm}"
export BUILD_CFLAGS="${CFLAGS-}"
export BUILD_CXXFLAGS="${CXXFLAGS-}"
export BUILD_CPPFLAGS="${CPPFLAGS-}"
export BUILD_LDFLAGS="${LDFLAGS-}"

python tools/gn/bootstrap/bootstrap.py --skip-generate-buildfiles

python third_party/libaddressinput/chromium/tools/update-strings.py

# gatesing gshitheads try pretty hard to force their toolchain on everyone
mkdir -p third_party/rust-toolchain/bin
for bin in rustc cargo rustfmt bindgen; do
    [ -f %{_bindir}/$bin ] && ln -sf %{_bindir}/$bin third_party/rust-toolchain/bin/$bin
done
mkdir -p third_party/gperf/cipd/bin
ln -sfn %{_bindir}/gperf third_party/gperf/cipd/bin/

# Choose ninja -j from free disk so parallel .o/.tmp files do not ENOSPC.
# Rough budget: ~1.5 GiB free headroom per compile job, cap at min(nproc, 32).
_ninja_jobs=$(df -Pk . | awk -v nproc="$(getconf _NPROCESSORS_ONLN)" '
	NR==2 {
		free_gb = $4 / 1024 / 1024
		j = int(free_gb / 1.5)
		if (j < 4) j = 4
		if (j > nproc) j = nproc
		if (j > 32) j = 32
		print j
	}')
echo "Using ninja -j${_ninja_jobs} (nproc=$(getconf _NPROCESSORS_ONLN))"
df -h . || :

%if %{with browser}
# Browser is configured and linked *before* CEF's Chromium patchset. Those
# patches rewrite shared chrome/blink/v8 sources and flip ENABLE_CEF /
# blink_heap_inside_shared_library; shipping chrome from a post-patch tree
# (or reusing its .o files) is not safe — ninja only rebuilds what depfiles
# and command-line hashes notice.
#
# Browser and CEF both use openmandriva.gn_args (is_component_ffmpeg=false
# when ffmpeg is in system_libs; unbundle is via replace_gn_files.py).
out/Release/gn gen --script-executable=/usr/bin/python --args="$(cat $HEDIR/flags.gn ; echo ; cat openmandriva.gn_args)" out/Release
%if %{system ffmpeg}
# gn pretty-prints args.gn as "is_component_ffmpeg = false"
if ! grep -qE 'is_component_ffmpeg[[:space:]]*=[[:space:]]*false' out/Release/args.gn; then
	echo "FATAL: gn did not set is_component_ffmpeg=false" >&2
	exit 1
fi
if ! grep -q 'USE_SYSTEM_FFMPEG=true' third_party/ffmpeg/BUILD.gn; then
	echo "FATAL: system ffmpeg unbundle missing (USE_SYSTEM_FFMPEG)" >&2
	exit 1
fi
%endif
ninja -j${_ninja_jobs} -C out/Release chrome chrome_sandbox chromedriver
%if %{system ffmpeg}
# No private component DSO when linking system libav*.
if [ -e out/Release/libffmpeg.so ]; then
	echo "FATAL: out/Release/libffmpeg.so present despite system ffmpeg" >&2
	exit 1
fi
if ! readelf -d out/Release/chrome | grep -q 'NEEDED.*libavcodec'; then
	echo "FATAL: chrome is not linked against system libavcodec" >&2
	exit 1
fi
if readelf -d out/Release/chrome | grep -q 'NEEDED.*libffmpeg\.so'; then
	echo "FATAL: chrome still NEEDs private libffmpeg.so" >&2
	exit 1
fi
%endif
# Freeze the shipping browser payload *now*, before patch.sh mtimes sources
# under out/Release's still-valid ninja graph.
rm -rf browser-dist
mkdir -p browser-dist/locales
cp -a out/Release/chrome out/Release/chrome_sandbox \
	out/Release/chrome_crashpad_handler out/Release/chromedriver \
	out/Release/libqt6_shim.so out/Release/libGLESv2.so \
	out/Release/libEGL.so \
	out/Release/libvulkan.so.1 out/Release/libvk_swiftshader.so \
	out/Release/chrome_100_percent.pak out/Release/resources.pak \
	out/Release/vk_swiftshader_icd.json \
	out/Release/*.bin \
	browser-dist/
# Only present when building Chromium's private component FFmpeg.
if [ -e out/Release/libffmpeg.so ]; then
	cp -a out/Release/libffmpeg.so browser-dist/
fi
cp -a out/Release/locales/*.pak browser-dist/locales/
cp -a out/Release/angledata out/Release/resources browser-dist/
if [ -e out/Release/icudtl.dat ]; then
	cp -a out/Release/icudtl.dat browser-dist/
fi
# Dual browser+CEF: drop compiler intermediates (not the gn binary) so the
# CEF tree has disk. Never touch browser-dist after this.
%if 0%{?cef:1}
rm -rf out/Release/obj out/Release/gen out/Release/thinlto-cache
df -h . || :
%endif
%endif

%if 0%{?cef:1}
# Generate CEF translated sources (libcef_dll wrappers, cef_paths.gypi, …)
# before applying CEF's Chromium patchset. version_manager needs a working
# clang for API hashes; point it at the system toolchain when Chromium's
# bundled llvm-build is absent (lite tarball / unbundle builds).
cd cef
if [ ! -x ../third_party/llvm-build/Release+Asserts/bin/clang ]; then
	mkdir -p ../third_party/llvm-build/Release+Asserts/bin
	ln -sfn %{_bindir}/clang ../third_party/llvm-build/Release+Asserts/bin/clang
	ln -sfn %{_bindir}/clang++ ../third_party/llvm-build/Release+Asserts/bin/clang++
fi
python tools/version_manager.py -u --fast-check || :
./tools/patch.sh
cd ..
%if %{system ffmpeg}
# CEF patch.sh rewrites shared Chromium sources; re-assert system FFmpeg
# unbundle + drop Chromium-private AVFMT_FLAG_NOH264PARSE for libcef too.
if ! grep -q 'USE_SYSTEM_FFMPEG=true' third_party/ffmpeg/BUILD.gn; then
	echo "FATAL: system ffmpeg unbundle lost after cef/tools/patch.sh" >&2
	exit 1
fi
# Match the assignment, not the explanatory comment that names the flag.
if grep -q 'flags |= AVFMT_FLAG_NOH264PARSE' media/filters/ffmpeg_glue.cc; then
	# Patch1005 may have been overwritten by cef/tools/patch.sh; re-apply.
	%{_bindir}/patch -p1 --fuzz=0 --forward < %{PATCH1005}
fi
if grep -q 'flags |= AVFMT_FLAG_NOH264PARSE' media/filters/ffmpeg_glue.cc; then
	echo "FATAL: AVFMT_FLAG_NOH264PARSE assignment still present (system ffmpeg)" >&2
	exit 1
fi
if ! grep -q 'libopus,opus,flac' media/ffmpeg/ffmpeg_common.cc || ! grep -q 'mp3,mp3float' media/ffmpeg/ffmpeg_common.cc; then
	%{_bindir}/patch -p1 --fuzz=0 --forward < %{PATCH1009}
fi
if ! grep -q 'libopus,opus,flac' media/ffmpeg/ffmpeg_common.cc || ! grep -q 'mp3,mp3float' media/ffmpeg/ffmpeg_common.cc; then
	echo "FATAL: system FFmpeg opus/mp3 allowlist missing after cef/tools/patch.sh" >&2
	exit 1
fi
%endif

# Fresh output dir: empty obj/ tree, new args.gn / build.ninja. Nothing is
# reused from out/Release, so a missed header dep cannot leave a pre-patch .o.
# use_thin_lto=false: LTO OOMs linking libcef.so even with 64 GB RAM.
# blink_heap_inside_shared_library=true: else R_X86_64_TPOFF32 on -shared.
# enable_cef=true: v8_used_in_shared_library tracks this after patch.sh.
# Same openmandriva.gn_args as the browser (system ffmpeg, no component DSO),
# but no GTK: libcef dlopens GTK3 and gtk_init_check() opens a second Wayland
# display next to Qt (OBS Browser: realloc(): invalid next size).
out/Release/gn gen --script-executable=/usr/bin/python --args="$(cat $HEDIR/flags.gn ; echo ; cat openmandriva.gn_args) is_cfi=false use_thin_lto=false chrome_pgo_phase=0 blink_heap_inside_shared_library=true enable_cef=true use_gtk=false cef_use_gtk=false" out/Release-CEF
%if %{system ffmpeg}
if ! grep -qE 'is_component_ffmpeg[[:space:]]*=[[:space:]]*false' out/Release-CEF/args.gn; then
	echo "FATAL: CEF gn did not set is_component_ffmpeg=false" >&2
	exit 1
fi
if ! grep -q 'USE_SYSTEM_FFMPEG=true' third_party/ffmpeg/BUILD.gn; then
	echo "FATAL: system ffmpeg unbundle missing after CEF gn gen" >&2
	exit 1
fi
%endif
# Last assignment in --args must win over openmandriva.gn_args use_gtk=true.
if ! grep -q '^use_gtk=false$' out/Release-CEF/args.gn && \
   ! grep -q 'use_gtk = false' out/Release-CEF/args.gn; then
	echo "FATAL: CEF gn args did not disable GTK (use_gtk=false)" >&2
	exit 1
fi
# Do *not* ninja the `cef` group: it is testonly and pulls ceftests +
# libcef_static_unittests. We package libcef, the wrapper, sandbox, samples.
# No GTK cefclient when use_gtk/cef_use_gtk are false; Qt sample is enough.
ninja -j${_ninja_jobs} -C out/Release-CEF libcef chrome_sandbox cefclient_qt libcef_dll_wrapper
%if %{system ffmpeg}
if [ -e out/Release-CEF/libffmpeg.so ]; then
	echo "FATAL: out/Release-CEF/libffmpeg.so present despite system ffmpeg" >&2
	exit 1
fi
if ! readelf -d out/Release-CEF/libcef.so | grep -q 'NEEDED.*libavcodec'; then
	echo "FATAL: libcef.so is not linked against system libavcodec" >&2
	exit 1
fi
if readelf -d out/Release-CEF/libcef.so | grep -q 'NEEDED.*libffmpeg\.so'; then
	echo "FATAL: libcef.so still NEEDs private libffmpeg.so" >&2
	exit 1
fi
%endif
# libcef_dll_wrapper.a is a thin archive (object paths, not contents). Expand
# it while obj/ still exists, then drop CEF intermediates so %install has room
# for BUILDROOT copies of libcef.so + Resources (ENOSPC at that step on ABF).
mkdir -p out/Release-CEF/libcef_dll_wrapper
(
	cd out/Release-CEF/obj/cef
	# Built with system libstdc++ (not Chromium's private libc++) so host apps
	# (Qt, boost, etc.) can link it without mixing C++ standard libraries.
	# libcef.so itself still uses Chromium's libc++ behind the C API.
	llvm-ar -t libcef_dll_wrapper.a | xargs llvm-ar cru libcef_dll_wrapper_full.a
	mv -f libcef_dll_wrapper_full.a ../../libcef_dll_wrapper/libcef_dll_wrapper.a
	llvm-ranlib ../../libcef_dll_wrapper/libcef_dll_wrapper.a
)
# Official binary trees are assembled by tools/make_distrib.py (generates
# cef_config.h and other public headers under gen/cef/include, cmake files,
# README/CREDITS, etc.). Point it at our ninja output dir and run before
# purging intermediates for disk space.
ln -sfn Release-CEF out/%{cef_gn_dir}
# about_credits.html is required by make_distrib; CEF ninja usually has it.
if [ ! -f out/Release-CEF/gen/components/resources/about_credits.html ]; then
	mkdir -p out/Release-CEF/gen/components/resources
	printf '%s\n' '<html><body>credits unavailable</body></html>' \
		> out/Release-CEF/gen/components/resources/about_credits.html
fi
# --minimal appends _minimal to --distrib-subdir (cef_dist -> cef_dist_minimal).
# --allow-partial: Debug tree is not built. --no-archive: we package via rpm.
# --no-format: skip clang-format on transferred autogen sources.
( cd cef && PYTHONPATH=tools python tools/make_distrib.py \
	--ninja-build %{?cef_md_arch} --allow-partial --minimal \
	--no-symbols --no-docs --no-archive --no-format \
	--distrib-subdir=cef_dist \
	--output-dir ../cef_binary_distrib )
# OM extras not shipped by upstream make_distrib (and fat wrapper for linkers).
_cef_dist=cef_binary_distrib/cef_dist_minimal
cp -a out/Release-CEF/libcef_dll_wrapper "$_cef_dist"/
# snapshot_blob.bin is still used by some embedders; not always in make_distrib.
if [ -f out/Release-CEF/snapshot_blob.bin ]; then
	cp -a out/Release-CEF/snapshot_blob.bin "$_cef_dist"/Release/
fi
# Private component FFmpeg only (system ffmpeg: libcef links libav* directly).
if [ -f out/Release-CEF/libffmpeg.so ]; then
	cp -a out/Release-CEF/libffmpeg.so "$_cef_dist"/Release/
fi
if [ -f out/Release-CEF/libqt6_shim.so ]; then
	cp -a out/Release-CEF/libqt6_shim.so "$_cef_dist"/Release/
fi
install -m 755 out/Release-CEF/cefclient_qt "$_cef_dist"/Release/
if [ -e out/Release-CEF/cefclient ]; then
	install -m 755 out/Release-CEF/cefclient "$_cef_dist"/Release/
fi
if [ -d out/Release-CEF/cefclient_files ]; then
	cp -a out/Release-CEF/cefclient_files "$_cef_dist"/Release/
fi
# Keep both sandbox names (ninja: chrome_sandbox; official: chrome-sandbox).
if [ -e "$_cef_dist"/Release/chrome-sandbox ] && [ ! -e "$_cef_dist"/Release/chrome_sandbox ]; then
	ln -s chrome-sandbox "$_cef_dist"/Release/chrome_sandbox
elif [ -e "$_cef_dist"/Release/chrome_sandbox ] && [ ! -e "$_cef_dist"/Release/chrome-sandbox ]; then
	ln -s chrome_sandbox "$_cef_dist"/Release/chrome-sandbox
fi
# Drop CEF intermediates so %install has room for BUILDROOT copies
# (ENOSPC at that step on ABF).
rm -rf out/Release-CEF/obj out/Release-CEF/gen out/Release-CEF/thinlto-cache
df -h . || :
%endif

%install
%if %{with browser}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}/%{name}/locales
mkdir -p %{buildroot}%{_libdir}/%{name}/themes
mkdir -p %{buildroot}%{_mandir}/man1
install -m 755 %{SOURCE1} %{buildroot}%{_libdir}/%{name}/
# browser-dist/ was snapshotted after the pre-CEF-patch ninja; do not
# install chrome from out/Release (patch.sh has since rewritten sources).
install -m 755 browser-dist/chrome %{buildroot}%{_libdir}/%{name}/
install -m 4755 browser-dist/chrome_sandbox %{buildroot}%{_libdir}/%{name}/chrome-sandbox
install -m 755 browser-dist/chrome_crashpad_handler %{buildroot}%{_libdir}/%{name}/
install -m 644 browser-dist/locales/*.pak %{buildroot}%{_libdir}/%{name}/locales/
install -m 644 browser-dist/chrome_100_percent.pak %{buildroot}%{_libdir}/%{name}/
install -m 644 browser-dist/resources.pak %{buildroot}%{_libdir}/%{name}/
install -m 755 browser-dist/libqt6_shim.so %{buildroot}%{_libdir}/%{name}/
# libGLESv2.so/libEGL.so look like dupes from the system, but aren't:
# Loading happens in ui/ozone/common/egl_util.cc -- indicating libGLESv2.so
# and libEGL.so (as opposed to their .1/.2 counterparts) are ANGLE (OpenGL ES
# -> native GL API wrapper)
# Now for most HW that shouldn't be necessary, so we may want to get rid of
# the custom libs and just use Mesa's libraries directly at some point.
install -m 755 browser-dist/libGLESv2.so %{buildroot}%{_libdir}/%{name}/
install -m 755 browser-dist/libEGL.so %{buildroot}%{_libdir}/%{name}/
# ANGLE data files (fake ICD for custom vulkan bits?), probably needed unless and
# until we drop the custom libEGL/libGLESv2
cp -a browser-dist/angledata %{buildroot}%{_libdir}/%{name}/
cp browser-dist/vk_swiftshader_icd.json %{buildroot}%{_libdir}/%{name}/
# Private component FFmpeg (absent when using system ffmpeg via unbundle).
if [ -e browser-dist/libffmpeg.so ]; then
	install -m 755 browser-dist/libffmpeg.so %{buildroot}%{_libdir}/%{name}/
fi
# FIXME is the custom vulkan needed, or is this just dupes from system vulkan
# for prehistoric distros?
install -m 755 browser-dist/libvulkan.so.1 %{buildroot}%{_libdir}/%{name}/
install -m 755 browser-dist/libvk_swiftshader.so %{buildroot}%{_libdir}/%{name}/
# May or may not be there depending on whether or not we use system icu
[ -e browser-dist/icudtl.dat ] && install -m 644 browser-dist/icudtl.dat %{buildroot}%{_libdir}/%{name}/
install -m 644 browser-dist/*.bin %{buildroot}%{_libdir}/%{name}/
ln -s %{_libdir}/%{name}/chromium-wrapper %{buildroot}%{_bindir}/%{name}
cp -a browser-dist/chromedriver %{buildroot}%{_libdir}/%{name}/chromedriver
ln -s %{_libdir}/%{name}/chromedriver %{buildroot}%{_bindir}/chromedriver

find browser-dist/resources/ -name "*.d" -exec rm {} \;
cp -r browser-dist/resources %{buildroot}%{_libdir}/%{name}

# desktop file
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 %{SOURCE2} %{buildroot}%{_datadir}/applications/

# icon
%if "%{name}" == "helium"
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -m 644 helium-*/resources/branding/product_logo.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/helium.svg
gzip -9 %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/helium.svg
mv %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/helium.svg.gz %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/helium.svgz
%else
for i in 24 48 64 128 256; do
        mkdir -p %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps
        install -m 644 chrome/app/theme/chromium/product_logo_$i.png \
                %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/%{name}.png
done
%endif

# Install the master_preferences file
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
install -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/%{name}

find %{buildroot} -name "*.nexe" -exec strip {} \;

# drirc workaround for VAAPI
mkdir -p %{buildroot}%{_datadir}/drirc.d/
cp %{S:4} %{buildroot}%{_datadir}/drirc.d/10-%{name}.conf

sed -e 's,chromium,helium,g;s,Chromium,Helium,g' %{buildroot}%{_datadir}/applications/chromium-browser.desktop >%{buildroot}%{_datadir}/applications/%{name}.desktop
rm %{buildroot}%{_datadir}/applications/chromium-browser.desktop
%if 0%{?cef:1}
# Browser payloads are already in BUILDROOT; drop the browser out tree before
# copying CEF (libcef.so alone is multi-GB) so dual-build installs fit on ABF.
rm -rf out/Release
%endif
%endif

%if 0%{?cef:1}
# Layout matches official CEF binary distributions (OnlyOffice/OBS CEF_ROOT):
# Release/, Resources/, include/ (incl. generated cef_config.h etc.),
# libcef_dll/, cmake/, plus our fat libcef_dll_wrapper/ and OM Qt shim.
# Assembled in %build via tools/make_distrib.py --minimal.
_cef_dist=cef_binary_distrib/cef_dist_minimal
if [ ! -d "$_cef_dist" ]; then
	echo "FATAL: missing $_cef_dist (make_distrib failed in %%build)" >&2
	exit 1
fi
mkdir -p %{buildroot}%{_libdir}/cef
cp -a "$_cef_dist"/Release "$_cef_dist"/Resources "$_cef_dist"/include \
	"$_cef_dist"/libcef_dll "$_cef_dist"/libcef_dll_wrapper \
	%{buildroot}%{_libdir}/cef/
if [ -d "$_cef_dist"/cmake ]; then
	cp -a "$_cef_dist"/cmake %{buildroot}%{_libdir}/cef/
fi
# Linux CEF sets DIR_ASSETS to libcef's directory (Release/). make_distrib
# --minimal puts icudtl.dat and *.pak in Resources/; without these links
# CefInitialize CHECK-fails in InitializeICUFromDataFile (OBS Browser source).
for f in icudtl.dat chrome_100_percent.pak chrome_200_percent.pak resources.pak; do
	if [ -f %{buildroot}%{_libdir}/cef/Resources/$f ] && \
	   [ ! -e %{buildroot}%{_libdir}/cef/Release/$f ]; then
		ln -sfn ../Resources/$f %{buildroot}%{_libdir}/cef/Release/$f
	fi
done
if [ -d %{buildroot}%{_libdir}/cef/Resources/locales ] && \
   [ ! -e %{buildroot}%{_libdir}/cef/Release/locales ]; then
	ln -sfn ../Resources/locales %{buildroot}%{_libdir}/cef/Release/locales
fi
# Sample sources for cef-devel (not part of --minimal).
cp -a cef/tests %{buildroot}%{_libdir}/cef/
# Header referenced by CEF wrappers but not always in the transfer list.
mkdir -p %{buildroot}%{_libdir}/cef/include/base/internal/net/base
cp -a net/base/net_error_list.h \
	%{buildroot}%{_libdir}/cef/include/base/internal/net/base/
# Required for OBS/OnlyOffice; fail early if make_distrib missed it.
if [ ! -f %{buildroot}%{_libdir}/cef/include/cef_config.h ]; then
	echo "FATAL: cef_config.h missing from make_distrib output" >&2
	exit 1
fi

# --- FHS / system-library convenience (in addition to the OnlyOffice tree) ---
# Real payload stays under %{_libdir}/cef so resource/sandbox discovery that
# follows libcef.so's real path continues to work. Symlinks make -lcef and
# pkg-config work like any other system library.
mkdir -p %{buildroot}%{_libdir} %{buildroot}%{_includedir} \
	%{buildroot}%{_libdir}/pkgconfig
# libcef.so and companion shims live in Release/; expose the main DSO at
# the standard linker search path (relative so multiarch libdirs work).
ln -sfn cef/Release/libcef.so %{buildroot}%{_libdir}/libcef.so
# Static C++ wrapper (libstdc++ ABI) for apps using the CEF C++ API.
ln -sfn cef/libcef_dll_wrapper/libcef_dll_wrapper.a \
	%{buildroot}%{_libdir}/libcef_dll_wrapper.a
# Headers as %{_includedir}/cef → same tree OnlyOffice sees under cef/include.
# Absolute path avoids guessing lib vs lib64 from include/.
ln -sfn %{_libdir}/cef/include %{buildroot}%{_includedir}/cef
# pkg-config
sed -e 's|@PREFIX@|%{_prefix}|g' \
	-e 's|@LIBDIR@|%{_libdir}|g' \
	-e 's|@INCLUDEDIR@|%{_includedir}|g' \
	-e 's|@VERSION@|%{chromium}|g' \
	%{SOURCE12} > %{buildroot}%{_libdir}/pkgconfig/cef.pc
# Alias used by some build systems that look for "libcef" rather than "cef".
ln -sfn cef.pc %{buildroot}%{_libdir}/pkgconfig/libcef.pc
# Sample apps: live next to libcef.so so $ORIGIN rpath finds the library, and
# so GetResourceDir() resolves ./cefclient_files beside the executable.
# Copied into the make_distrib tree in %build so we can drop out/Release.
install -m 755 "$_cef_dist"/Release/cefclient_qt %{buildroot}%{_libdir}/cef/Release/
if [ -e "$_cef_dist"/Release/cefclient ]; then
	install -m 755 "$_cef_dist"/Release/cefclient %{buildroot}%{_libdir}/cef/Release/
fi
if [ -d "$_cef_dist"/Release/cefclient_files ]; then
	cp -a "$_cef_dist"/Release/cefclient_files %{buildroot}%{_libdir}/cef/Release/
fi
# Convenience launchers (exec the real binary so $ORIGIN stays Release/).
# Unquoted heredoc so rpm expands %{_libdir}; escape $ so the shell keeps "$@".
mkdir -p %{buildroot}%{_bindir}
if [ -e %{buildroot}%{_libdir}/cef/Release/cefclient ]; then
cat > %{buildroot}%{_bindir}/cefclient << EOF
#!/bin/sh
exec %{_libdir}/cef/Release/cefclient "\$@"
EOF
chmod 755 %{buildroot}%{_bindir}/cefclient
fi
cat > %{buildroot}%{_bindir}/cefclient_qt << EOF
#!/bin/sh
exec %{_libdir}/cef/Release/cefclient_qt "\$@"
EOF
chmod 755 %{buildroot}%{_bindir}/cefclient_qt

%files -n cef
%dir %{_libdir}/cef
%{_libdir}/cef/Release
%exclude %{_libdir}/cef/Release/libqt6_shim.so
%exclude %{_libdir}/cef/Release/cefclient
%exclude %{_libdir}/cef/Release/cefclient_qt
%exclude %{_libdir}/cef/Release/cefclient_files
%{_libdir}/cef/Resources
# FHS symlink: linker finds -lcef without special -L paths.
%{_libdir}/libcef.so

%files -n cef-qt6
%{_libdir}/cef/Release/libqt6_shim.so

%files -n cef-devel
%{_libdir}/cef/include
%{_libdir}/cef/libcef_dll
%{_libdir}/cef/tests
%{_libdir}/cef/libcef_dll_wrapper
# CMake helpers from make_distrib (wrapper rebuild / sample projects).
%{_libdir}/cef/cmake
# FHS / pkg-config view of the same files.
%{_includedir}/cef
%{_libdir}/libcef_dll_wrapper.a
%{_libdir}/pkgconfig/cef.pc
%{_libdir}/pkgconfig/libcef.pc

%files -n cef-examples
%optional %{_bindir}/cefclient
%{_bindir}/cefclient_qt
%optional %{_libdir}/cef/Release/cefclient
%{_libdir}/cef/Release/cefclient_qt
%optional %{_libdir}/cef/Release/cefclient_files
%endif

%if %{with browser}
%files
%doc LICENSE AUTHORS
%config %{_sysconfdir}/%{name}
%{_datadir}/drirc.d/10-%{name}.conf
%{_bindir}/%{name}
%{_libdir}/%{name}/*.bin
%{_libdir}/%{name}/*.so*
%exclude %{_libdir}/%{name}/libqt6_shim.so
%{_libdir}/%{name}/*.json
%{_libdir}/%{name}/angledata
%{_libdir}/%{name}/chromium-wrapper
%{_libdir}/%{name}/chrome
%{_libdir}/%{name}/chrome-sandbox
%{_libdir}/%{name}/chrome_crashpad_handler
%optional %{_libdir}/%{name}/icudtl.dat
%{_libdir}/%{name}/locales
%{_libdir}/%{name}/chrome_100_percent.pak
%{_libdir}/%{name}/resources.pak
%{_libdir}/%{name}/resources
%{_libdir}/%{name}/themes
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.*

%files qt6
%{_libdir}/%{name}/libqt6_shim.so

%files chromedriver
%doc LICENSE AUTHORS
%{_bindir}/chromedriver
%{_libdir}/%{name}/chromedriver
%endif

%clean
# don't wipe BUILD
