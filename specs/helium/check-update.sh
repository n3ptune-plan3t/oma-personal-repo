#!/bin/sh
git ls-remote https://github.com/imputnet/helium |awk '{ print $2; }' |grep '^refs/tags/' |sed -e 's,^refs/tags/,,' |sort -V |tail -n1
