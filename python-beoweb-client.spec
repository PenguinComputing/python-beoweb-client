%define build_number %([ -e /build/.scyld-build-number ] && cat /build/.scyld-build-number || echo `date +"%y%m%d.%H.%M"`)

%define name 			python-beoweb-client
%define version 		0.1
%define scyld_python_prefix     /opt/scyld/python/2.6.5
%define scyld_python_site_packages %{scyld_python_prefix}/lib/python2.6/site-packages

Summary: Scyld Beoweb Client
Name: %{name}
Version: %{version}
Release: %{build_number}
Vendor: Penguin Computing, Inc.
Packager: Penguin Computing Inc. <http://www.penguincomputing.com>
License: (c) 2002-2016 Penguin Computing, Inc.
Group: Development/Tools
URL: http://www.penguincomputing.com
Distribution: Scyld ClusterWare
Requires: python-scyld >= 2.6.5.1
Requires: python-scyld-utils >= 1.2.0
Requires: python-cloud-auth-client
BuildRoot: /var/tmp/%{name}-%{version}-%{release}-root
BuildRequires: python-scyld
Source0: %{name}-%{version}.tar.gz

%description
Client library for Scyld Beoweb API

%prep
%setup -q -n %{name} -c

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}%{scyld_python_prefix}
PATH=%{scyld_python_prefix}/bin:$PATH
python setup.py install --single-version-externally-managed --root ${RPM_BUILD_ROOT}

%clean
%__rm -rf "$RPM_BUILD_ROOT"

%files
%defattr(-, root, root, -)
%{scyld_python_site_packages}/*

%post
# Make sure pip is present
PATH=%{scyld_python_prefix}/bin:$PATH
which pip
if [ $? != 0 ]; then
    %{scyld_python_site_packages}/easy_install pip
fi

pip install -r %{scyld_python_site_packages}/python_beoweb_client-%{version}-py2.6.egg-info/requires.txt

%changelog
* Mon Oct 17 2016 Limin Gu <lgu@penguincomputing.com>
- Packaging from github source

