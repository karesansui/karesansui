%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %global pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%global srcname SQLAlchemy

Name:           python-sqlalchemy
Version:        0.5.8
Release:        1%{?dist}
Summary:        Modular and flexible ORM library for python

Group:          Development/Libraries
License:        MIT
URL:            http://www.sqlalchemy.org/
Source0:        http://pypi.python.org/packages/source/S/%{srcname}/%{srcname}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel
BuildRequires:  python-setuptools >= 0.6c3
BuildRequires: python-nose

%description
SQLAlchemy is an Object Relational Mappper (ORM) that provides a flexible,
high-level interface to SQL databases.  Database and domain concepts are
decoupled, allowing both sides maximum flexibility and power. SQLAlchemy
provides a powerful mapping layer that can work as automatically or as manually
as you choose, determining relationships based on foreign keys or letting you
define the join conditions explicitly, to bridge the gap between database and
domain.

%prep
%setup -q -n %{srcname}-%{version}

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build
sed -i 's/\r//' examples/dynamic_dict/dynamic_dict.py

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{python_sitelib}
python setup.py install --skip-build --root $RPM_BUILD_ROOT

# remove unnecessary scripts for building documentation
rm -rf doc/build

%clean
rm -rf $RPM_BUILD_ROOT

#%check
#export PYTHONPATH=.
#python setup.py develop -d .
#nosetests

%files
%defattr(-,root,root,-)
%doc README LICENSE PKG-INFO CHANGES doc examples
%{python_sitelib}/*

%changelog
* Mon Nov 30 2009 Taizo ITO <taizo@karesansui-project.info> - 0.5.8-1
- for CentOS 5
