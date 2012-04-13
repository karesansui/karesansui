%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define __app karesansui
%define version 3.0.0
%define release 1
%define date %(echo `LANG=C date +%%Y%%m%%d%%H%%M%%S`)

%define name karesansui
%define _kss_sysconfdir %{_sysconfdir}/%{__app}
%define _psi_sysconfdir %{_sysconfdir}/pysilhouette
%define _kss_bindir     %{_datarootdir}/%{__app}/bin
%define _kss_datadir    %{_sharedstatedir}/%{__app}

%define _bindir   %{_kss_bindir}
%define _tmpdir   %{_kss_datadir}/tmp
%define _cachedir %{_kss_datadir}/cache

%define _user           kss
%define _group          kss
%define _user_doc       Karesansui Project
%define _uid_min        250
%define _uid_max        300

Summary:        Virtualization management tool(Web Application) 
Summary(ja):    オープンソースの仮想ホスト管理アプリケーション
Name:           %{name}
Version:        %{version}
Release:        %{release}
License:        MIT/X11
Group:          Applications/System
URL:            http://karesansui-project.info/
Vendor:         Karesansui Project
Packager:       Taizo ITO <taizo@karesansui-project.info>

Source0:        %{__app}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix:         %{_prefix}
BuildArch:      noarch
Provides:       %{__app}
Requires:       libvirt-python
Requires:       pysilhouette
Requires:       PyXML

%description
On the Web for virtualization management software to manage.
The guest OS and the management of resources and dynamic changes can be done easily.
RESTful Web applications in architecture.

%package lib
Summary: libraries for Karesansui Core
Group: Applications/System
License: MIT/X11
Requires: %{name} = %{version}

%description lib
libraries for Karesansui Core

%package data
Summary: UI data for Karesansui Core
Group: Applications/System
License: MIT/X11
Requires: %{name} = %{version}

%description data
UI data for Karesansui Core

%package gadget
Summary: Basic gadget collection for Karesansui Core
Group: Applications/System
License: MIT/X11
Requires: %{name} = %{version}

%description gadget
Basic gadget collection for Karesansui Core

%package bin
Summary: Basic command collection for Karesansui Core
Group: Applications/System
License: MIT/X11
Requires: %{name} = %{version}

%description bin
Basic command collection for Karesansui Core

%package test
Summary: Unit test environment for Karesansui Core
Group: Applications/System
License: MIT/X11
Requires: %{name} = %{version}
Requires: python-paste

%description test
Unit test environment for Karesansui Core

%package plus
Summary: additional packages that extend functionality of existing packages
Group: Applications/System
License: See the source code
Requires: %{name} = %{version}
Requires: rpm-python

%description plus
additional packages that extend functionality of existing packages

%prep
%setup -n %{__app}-%{version}

%build
%{__python} setup.py build

%install
%{__rm} -rf %{buildroot}
%{__python} setup.py install -O0 --skip-build --root %{buildroot} --install-scripts=%{_bindir} # --record=INSTALLED_FILES

install -d -m 0770 $RPM_BUILD_ROOT%{_kss_sysconfdir}
install -d -m 0770 $RPM_BUILD_ROOT%{_psi_sysconfdir}
install -d -m 0770 $RPM_BUILD_ROOT%{_bindir}
install -d -m 0770 $RPM_BUILD_ROOT%{_tmpdir}
install -d -m 0770 $RPM_BUILD_ROOT%{_cachedir}
install -d -m 0770 $RPM_BUILD_ROOT/var/log/%{__app}
install -d -m 0770 $RPM_BUILD_ROOT%{_sysconfdir}/cron.d/
install -d -m 0770 $RPM_BUILD_ROOT%{_kss_sysconfdir}/virt/

pushd sample
%{__cp} -f  application.conf.example $RPM_BUILD_ROOT%{_kss_sysconfdir}/application.conf.example
%{__cp} -f  application.conf.example $RPM_BUILD_ROOT%{_kss_sysconfdir}/application.conf
%{__cp} -f  log.conf.example         $RPM_BUILD_ROOT%{_kss_sysconfdir}/log.conf.example
%{__cp} -f  log.conf.example         $RPM_BUILD_ROOT%{_kss_sysconfdir}/log.conf
%{__cp} -fr lighttpd/                $RPM_BUILD_ROOT%{_kss_sysconfdir}/lighttpd.example/
%{__cp} -fr apache/                  $RPM_BUILD_ROOT%{_kss_sysconfdir}/apache.example/
%{__cp} -fr nginx/                   $RPM_BUILD_ROOT%{_kss_sysconfdir}/nginx.example/
%{__cp} -f  whitelist.conf.example   $RPM_BUILD_ROOT%{_kss_sysconfdir}/
%{__cp} -f  service.xml.example      $RPM_BUILD_ROOT%{_kss_sysconfdir}/service.xml
%{__cp} -f  logview.xml.example      $RPM_BUILD_ROOT%{_kss_sysconfdir}/logview.xml
%{__cp} -f  cron_cleantmp.example    $RPM_BUILD_ROOT/etc/cron.d/%{__app}_cleantmp
popd

find $RPM_BUILD_ROOT%{python_sitelib} -type d -exec chmod g+rwx \{\} \; 2>/dev/null


%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Add group
getent group | %{__grep} "^%{_group}:" >/dev/null 2>&1
if [ $? -ne 0 ]; then
  __uid=%{_uid_min}
  while test ${__uid} -le %{_uid_max}
  do
    getent group | %{__grep} "^[^:]*:x:${__uid}:" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
      _gid=${__uid}
      break
    fi
    __uid=`expr ${__uid} + 1`
  done
  /usr/sbin/groupadd -g ${_gid} -f %{_group}
fi

# Add user
getent passwd | %{__grep} "^%{_user}:" >/dev/null 2>&1
if [ $? -ne 0 ]; then
  __uid=%{_uid_min}
  while test ${__uid} -le %{_uid_max}
  do
    getent passwd | %{__grep} "^[^:]*:x:${__uid}:" >/dev/null 2>&1
    if [ $? -ne 0 ]; then
      _uid=${__uid}
      break
    fi
    __uid=`expr ${__uid} + 1`
  done
  /usr/sbin/useradd -c "%{_user_doc}" -u ${_uid} -g %{_group} -s /bin/false -r %{_user} 2> /dev/null || :
fi

%post
# Modify libvirt configuration file.
libvirtd_conf=%{_sysconfdir}/libvirt/libvirtd.conf
if [ -f ${libvirtd_conf} ]; then
  %{__grep} '^unix_sock_group = "root"' ${libvirtd_conf} >/dev/null 2>&1
  if [ $? -eq 0 ]; then
    %{__sed} -e "s#unix_sock_group = \"root\"#unix_sock_group = \"%{_group}\"#" ${libvirtd_conf} >${libvirtd_conf}.$$
    %{__cp} -f ${libvirtd_conf}.$$ ${libvirtd_conf}
    %{__rm} -f ${libvirtd_conf}.$$
  fi
fi

# Make directory
libvirt_datadir=/var/lib/libvirt
if [ -d ${libvirt_datadir} ]; then
  for subdir in boot domains images network qemu
  do
    if [ ! -e ${libvirt_datadir}/${subdir} ]; then
      %{__mkdir_p} ${libvirt_datadir}/${subdir}
    fi
    %{__chmod} g+rwx ${libvirt_datadir}/${subdir} >/dev/null 2>&1
    %{__chmod} o-rwx ${libvirt_datadir}/${subdir} >/dev/null 2>&1
  done
  %{__chgrp} -R %{_group} ${libvirt_datadir}/ >/dev/null 2>&1
  %{__chmod} g+rwx ${libvirt_datadir}/ >/dev/null 2>&1
fi

# Register whitelist commands to pysilhouette service.
if [ -d %{_psi_sysconfdir} ]; then
  if [ ! -s %{_psi_sysconfdir}/whitelist.conf ]; then
    %{__cp} -f %{_kss_sysconfdir}/whitelist.conf.example %{_psi_sysconfdir}/whitelist.conf
  fi
fi

gpasswd -a qemu %{_group} >/dev/null 2>&1

%postun
if [ $1 = 0 ]; then
  /usr/sbin/userdel %{_user} 2> /dev/null || :
  /usr/sbin/groupdel %{_group} 2> /dev/null || :

  # Modify libvirt configuration file.
  libvirtd_conf=%{_sysconfdir}/libvirt/libvirtd.conf
  if [ -f ${libvirtd_conf} ]; then
    %{__grep} '^unix_sock_group =' ${libvirtd_conf} >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      %{__sed} -e "s#unix_sock_group = .*#unix_sock_group = \"root\"#"  ${libvirtd_conf} >${libvirtd_conf}.$$
      %{__cp} -f ${libvirtd_conf}.$$ ${libvirtd_conf}
      %{__rm} -f ${libvirtd_conf}.$$
    fi
  fi
fi

#%files -f INSTALLED_FILES
#%defattr(-,root,root)
#%doc doc tools sample

%files
%defattr(-,root,%{_group})
%doc doc tools sample AUTHORS COPYING TRADEMARKS.TXT INSTALL.md INSTALL.ja.md README.md README.ja.md
%dir %{python_sitelib}/
%dir %{python_sitelib}/karesansui/
%dir %{python_sitelib}/karesansui/db/
%dir %{python_sitelib}/karesansui/static/
%{python_sitelib}/karesansui/*.py*
%{python_sitelib}/karesansui/db/*.py*
%{python_sitelib}/karesansui/db/access/*.py*
%{python_sitelib}/karesansui/db/model/*.py*
%{python_sitelib}/karesansui/static/js/*
%{python_sitelib}/karesansui/static/lib/*
%{_kss_sysconfdir}/*.example
%defattr(0770,root,%{_group})
%config(noreplace) %{_kss_sysconfdir}/*.conf
%config(noreplace) %{_kss_sysconfdir}/*.xml
%dir %{_kss_sysconfdir}/
%dir %{_kss_sysconfdir}/virt/
%dir /var/log/%{__app}/
%dir %{_kss_datadir}/
%dir %{_tmpdir}/
%defattr(0770,root,%{_group})
%dir %{_cachedir}/
/etc/cron.d/*
%dir %{_datarootdir}/%{__app}

%files lib
%defattr(-,root,%{_group})
%dir %{python_sitelib}/karesansui/lib/
%{python_sitelib}/karesansui/lib/*

%files data
%defattr(-,root,%{_group})
%dir %{python_sitelib}/karesansui/static/css/
%dir %{python_sitelib}/karesansui/static/icon/
%dir %{python_sitelib}/karesansui/static/images/
%dir %{python_sitelib}/karesansui/locale/
%{python_sitelib}/karesansui/static/css/*
%{python_sitelib}/karesansui/static/icon/*
%{python_sitelib}/karesansui/static/images/*
%{python_sitelib}/karesansui/locale/*/LC_MESSAGES/*.mo

%files gadget
%defattr(-,root,%{_group})
%dir %{python_sitelib}/karesansui/gadget/
%dir %{python_sitelib}/karesansui/templates/default/
%{python_sitelib}/karesansui/gadget/*
%{python_sitelib}/karesansui/templates/default/*

%files bin
%defattr(0770,root,%{_group})
%dir %{_bindir}/
%defattr(0550,root,%{_group})
%{_bindir}/*

%files test
%defattr(-,root,%{_group})
%dir %{python_sitelib}/karesansui/tests/
%{python_sitelib}/karesansui/tests/*
%{python_sitelib}/karesansui*egg-info

%files plus
%defattr(-,root,%{_group})
%dir %{python_sitelib}/karesansui/plus/
%{python_sitelib}/karesansui/plus/*

%changelog
* Mon Apr  2 2012 Taizo ITO <taizo@karesansui-project.info> - 3.0.0-1
- version 3.0.0 beta release.

* Thu Jul 29 2010 Keisuke Fukawa <keisuke@karesansui-project.info> - 2.0.1-1
- version 2.0.1 stable release.

* Fri Jul 23 2010 Keisuke Fukawa <keisuke@karesansui-project.info> - 2.0.0-2
- version 2.0.0 stable release.

* Mon May 24 2010 Taizo ITO <taizo@karesansui-project.info> - 2.0.0-1
- version 2.0.0 beta release.
- 'karesansui-lib' sub package that includes python libraries is separated from core package.

* Wed Jan 06 2010 Kei Funagayama <kei@karesansui-project.info> - 1.1.0-4
- version 1.1.0 beta release.

* Fri Dec 25 2009 Taizo ITO <taizo@karesansui-project.info> - 1.1.0-3
- Fixed attach/detach device.

* Mon Dec 14 2009 Kei Funagayama <kei@karesansui-project.info> - 1.1.0-2
- Add "plus" package.
- Add Software Update feature.

* Thu Dec 10 2009 Taizo ITO <taizo@karesansui-project.info> - 1.1.0-1
- kvm support.
- Changed paths for domain's image data.

* Thu Oct 29 2009 Kei Funagayama <kei@karesansui-project.info> - 1.0.3-2
- CentOS(i386/x86_64) support.
- RHEL(i386/x86_64) support.

* Tue Sep 18 2009 Kei Funagayama <kei@karesansui-project.info> - 1.0.3-1
- Added checker for keymap selection.
- Fixed web server setting bugs.
- Fixed the following hungup bug.
    ** glibc detected *** /usr/bin/python: free(): invalid pointer:
- Changed the format of system uri path.
    fixed error "unexpected Xen URI path '/system', try xen:///" for libvirt-0.6.5.

* Thu Jun 18 2009 Kei Funagayama <kei@karesansui-project.info> - 1.0.2-1
- Sparce file support is now available at creating a guest environment.
- Keyboard maps selection is now available at creating a guest environment.
- Fixed rpm transaction closing order.
- Fixed checking of processor support.
- sqlite time to register with the system, had not added the time zone information.
- Network database is now available as pysilhouette database.
- Addresses an issue which karesansui does not work at multi-host environment.

* Tue Jun 9 2009 Kei Funagayama <kei@karesansui-project.info> - 1.0.1-1
- Karesansui now works on CentOS5.3 64bit(x86_64), RHEL5.3 64bit(x86_64) and RHEL5.3 32bit(x86).
- Added support for AMD Athlon64 or Opteron environment.
- Added favicons.
- Improves VNC console keyboard layout support.
- Prevents host environment's FQDN from being resolved.
- Highlights required items on input forms.
- Buttons turn disabled not to be clicked after clicking at dialog window.
- Karesansui now works when PostgreSQL is selected as database at the installation process.
- Addresses an issue which could not reach the management console after resetting F/W.
- Addresses an issue which could not move to other tabs while displaying guest console.
- Delete button is now turned disabled after destroying resources.
- Network configuration is now editable without errors.
- Addresses an issue which occurs when job search is performanced many times.
- Creating guest with empty value in "Memory Size" or "Disk Size" now works.
- Prevent input data from being posted to other resources when enter key is pressed on input forms.
- Improved a check logic about guest ID.
- Improved error handling on nonexistent NIC.

* Tue May 19 2009 Taizo ITO <taizo@karesansui-project.info> - 1.0.0-1
- Initial build.
