%global astal_commit cbcd9f49dd6b9638dc5623b56cc6e1e0a60b593e
%global astal_shortcommit %(c=%{astal_commit}; echo ${c:0:7})
%global bumpver 2

Summary:	Metapackage for Astal
Name:		astal
Version:	1~%{bumpver}.git%{astal_shortcommit}
Release:	1
Group:		Window Manager/Utilities
License:	LGPL-2.1


Requires:	%{mklibname astal-io}
Requires:	%{mklibname astal-libs}
Requires:	%{mklibname astal-lua}
Requires:	%{mklibname astal-gtk3}
Requires:	%{mklibname astal-gtk4}
Requires:	astal-gjs
Requires:	%{mklibname appmenu-glib-translator}


%description
This package is a meta-package, meaning that its purpose is to contain all dependencies for running astal/ags2

%files

#---------------------------------------------------------------------------
