%define build_number %([ -e /build/.scyld-build-number ] && cat /build/.scyld-build-number || echo `date +"%y%m%d.%H.%M"`)
%define debug_package %{nil}

%define name 			python-beoweb-client
%define version 		0.1.2
%define _podtoolsenv     /opt/scyld/podtools/env

Summary: Scyld Beoweb Client
Name: %{name}
Version: %{version}
Release: %{build_number}
Vendor: Penguin Computing, Inc.
Packager: Penguin Computing Inc. <http://www.penguincomputing.com>
License: (c) 2002-2018 Penguin Computing, Inc.
Group: Development/Tools
URL: http://www.penguincomputing.com
Distribution: Scyld ClusterWare
Requires: python-scyld-utils >= 1.4.2
Requires: python-cloud-auth-client
BuildRoot: /var/tmp/%{name}-%{version}-%{release}-root
BuildRequires: python-scyld-utils python-cloud-auth-client 
Source0: %{name}-%{version}.tar.gz

%description
Client library for Scyld Beoweb API

%prep
%setup -q -n %{name} -c

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}%{_podtoolsenv}
source %{_podtoolsenv}/bin/activate
python setup.py install --single-version-externally-managed --root ${RPM_BUILD_ROOT}
pip install -r ${RPM_BUILD_ROOT}/%{_podtoolsenv}/lib/python*/site-packages/python_beoweb_client-%{version}-*.egg-info/requires.txt --root ${RPM_BUILD_ROOT}
deactivate

%post

%clean
%__rm -rf "$RPM_BUILD_ROOT"

%files
%defattr(-, root, root, -)
%{_podtoolsenv}/lib*/python*/site-packages/*

%changelog
* Fri May 11 2018 Limin Gu <lgu@penguincomputing.com>
- Move installation to podtools virtual environment.

* Thu Feb 08 2018 Aaron Kurtz <akurtz@penguincomputing.com>
- Fix failure to authenticate on first login
- Enforce HTTPS certificate verification on all requests
- Bump to v0.1.2

* Mon Oct 17 2016 Limin Gu <lgu@penguincomputing.com>
- Packaging from github source

