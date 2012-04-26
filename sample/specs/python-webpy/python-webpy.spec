%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary:        A simple web framework for Python
Name:           python-webpy
Version:        0.36
Release:        1%{?dist}
Source0:        http://webpy.org/static/web.py-%{version}.tar.gz
License:        Public domain
Group:          Development/Libraries
Vendor:         Karesansui Project
URL:            http://webpy.org/
Packager:       Taizo ITO <taizo@karesansui-project.info>
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch

%description
web.py is a web framework for python that is as simple as it is
powerful. web.py is in the public domain; you can use it for whatever
purpose with absolutely no restrictions. 

%prep
%setup -n web.py-%{version}


%build
%{__python} setup.py build

%install
%{__rm} -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{python_sitelib}/*

%changelog
* Tue Mar 13 2012 Taizo ITO <taizo@karesansui-project.info> - 0.36-1
- initial 

