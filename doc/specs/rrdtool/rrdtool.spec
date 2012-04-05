%{?el6:# Tag: rfx}

%{?el5:%define _without_egg_info 1}
%{?el4:%define _without_egg_info 1}
%{?el4:%define _without_xulrunner 1}
%{?el3:%define _without_egg_info 1}
%{?el3:%define _without_xulrunner 1}
%{?el2:%define _without_egg_info 1}
%{?el2:%define _without_xulrunner 1}

%define perl_vendorarch %(eval "`%{__perl} -V:installvendorarch`"; echo $installvendorarch)
%define perl_vendorlib %(eval "`%{__perl} -V:installvendorlib`"; echo $installvendorlib)
%define python_sitearch %(%{__python} -c 'from distutils import sysconfig; print sysconfig.get_python_lib(1)')
%define python_version %(%{__python} -c 'import string, sys; print string.split(sys.version, " ")[0]')

Summary:        Round Robin Database Tool to store and display time-series data
Name:           rrdtool
Version:        1.4.7
Release:        1%{?dist}
License:        GPL
Group:          Applications/Databases
URL:            http://people.ee.ethz.ch/~oetiker/webtools/rrdtool/
Vendor:         Karesansui Project
Packager:       Taizo ITO <taizo@karesansui-project.info>

Source: http://oss.oetiker.ch/rrdtool/pub/rrdtool-%{version}.tar.gz
Source1: rrdcached.init
Source2: rrdcached.sysconfig
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires: cairo-devel
BuildRequires: freetype-devel
BuildRequires: gcc-c++
BuildRequires: glib2-devel
BuildRequires: gettext-devel
BuildRequires: groff
BuildRequires: intltool
BuildRequires: libpng-devel
BuildRequires: libxml2-devel
BuildRequires: openssl-devel
BuildRequires: pango-devel
BuildRequires: python-devel >= 2.3
#%{!?_without_xulrunner:BuildRequires: xulrunner-devel}
BuildRequires: zlib-devel
Requires: cairo
Requires: gettext
Requires: glib2
Requires: libxml2
Requires: openssl
Requires: perl
Requires: pango
Requires: python
Requires: xorg-x11-fonts-Type1
Requires: zlib

%description
RRD is the Acronym for Round Robin Database. RRD is a system to store and
display time-series data (i.e. network bandwidth, machine-room temperature,
server load average). It stores the data in a very compact way that will not
expand over time, and it presents useful graphs by processing the data to
enforce a certain data density. It can be used either via simple wrapper
scripts (from shell or Perl) or via frontends that poll network devices and
put a friendly user interface on it.

%package devel
Summary: RRDtool static libraries and header files
Group: Development/Libraries
Requires: %{name} = %{version}

%description devel
RRD is the Acronym for Round Robin Database. RRD is a system to store and
display time-series data (i.e. network bandwidth, machine-room temperature,
server load average). This package allow you to use directly this library.

%package -n perl-rrdtool
Summary: Perl RRDtool bindings
Group: Development/Languages
Requires: %{name} = %{version}
Obsoletes: rrdtool-perl <= %{version}-%{release}
Provides: rrdtool-perl = %{version}-%{release}

%description -n perl-rrdtool
The Perl RRDtool bindings

%package -n python-rrdtool
Summary: Python RRDtool bindings
Group: Development/Languages
BuildRequires: python
Requires: python >= %{python_version}
Requires: %{name} = %{version}
Obsoletes: rrdtool-python <= %{version}-%{release}
Provides: rrdtool-python = %{version}-%{release}

%description -n python-rrdtool
Python RRDtool bindings.

%prep
%setup

### Fix incorrect $prefix/lib for LUA in configure
%{__perl} -pi.orig -e 's|/lib\b|/%{_lib}|g;' configure

%build
%configure \
    --with-perl-options='INSTALLDIRS="vendor"' \
    --with-pic

%{__make}

%install
%{__rm} -rf %{buildroot}
%{__make} install DESTDIR="%{buildroot}"

find %{buildroot} -name .packlist -exec %{__rm} {} \;
%{__rm} -f %{buildroot}%{perl_archlib}/perllocal.pod
%{__rm} -f %{buildroot}%{perl_vendorarch}/ntmake.pl

# Init script/sysconfig for rrfdcached
%{__mkdir} -p %{buildroot}%{_initrddir}
%{__cp} %{SOURCE1} %{buildroot}%{_initrddir}/rrdcached
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__cp} %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/rrdcached

# Create dir for rrdcached data and unix socket
%{__mkdir} -p %{buildroot}%{_localstatedir}/rrdtool/rrdcached

%clean
%{__rm} -rf %{buildroot}

%pre
# Add the "rrdcached" user
/usr/sbin/useradd -c "rrdcached" \
    -s /sbin/nologin -r -d %{_localstatedir}/rrdtool/rrdcached rrdcached  2> /dev/null || :

%post
# Register the rrdcached service
/sbin/chkconfig --add rrdcached

%preun
if [ $1 = 0 ]; then
    /sbin/service rrdcached stop > /dev/null 2>&1
    /sbin/chkconfig --del rrdcached
fi


%files
%defattr(-, root, root, 0755)
%doc CHANGES CONTRIBUTORS COPYING COPYRIGHT NEWS README THREADS TODO
%doc examples/
%doc %{_mandir}/man1/*.1*
%doc %{_mandir}/man3/librrd.3*
%{_initrddir}/rrdcached
%{_sysconfdir}/sysconfig/rrdcached
%{_bindir}/rrdcached
%{_bindir}/rrdcgi
%{_bindir}/rrdtool
%{_bindir}/rrdupdate
%{_datadir}/rrdtool/
%{_libdir}/librrd.so.*
%{_libdir}/librrd_th.so.*
%attr(775,rrdcached,rrdcached) %dir %{_localstatedir}/rrdtool/rrdcached

%files devel
%defattr(-, root, root, 0755)
%{_includedir}/rrd.h
%{_includedir}/rrd_client.h
%{_includedir}/rrd_format.h
%{_libdir}/librrd.a
%{_libdir}/librrd.so
%{_libdir}/librrd_th.a
%{_libdir}/librrd_th.so
%{_libdir}/pkgconfig/librrd.pc
%exclude %{_libdir}/librrd.la
%exclude %{_libdir}/librrd_th.la

%files -n perl-rrdtool
%defattr(-, root, root, 0755)
%doc bindings/perl-shared/MANIFEST bindings/perl-shared/README
%doc %{_mandir}/man3/RRDp.3*
%doc %{_mandir}/man3/RRDs.3*
%{perl_vendorarch}/RRDs.pm
%{perl_vendorarch}/auto/RRDs/*
%{perl_vendorlib}/RRDp.pm

%files -n python-rrdtool
%defattr(-, root, root, 0755)
%doc bindings/python/ACKNOWLEDGEMENT bindings/python/AUTHORS bindings/python/COPYING bindings/python/README
%{!?_without_egg_info:%{python_sitearch}/*.egg-info}
%{python_sitearch}/rrdtoolmodule.so

%changelog
* Mon Apr  2 2012 Taizo ITO <taizo@karesansui-project.info> - 1.4.5-1
- Updated to release 1.4.5.
