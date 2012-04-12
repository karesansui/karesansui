%define __check_files %{nil}

# plugins
%define with_perl       1
%define with_python     1
%define with_ipmi       0
%define with_curl       0
%define with_curl_json  0
%define with_nut        0
%define with_ping       0
%define with_postgresql 0
%define with_mysql      0
%define with_snmp       0
%define with_sensors    0
%define with_rrdtool    1
%define with_rrdcached  1
%define with_virt       1
%define with_apache     0
%define with_dns        0
%define with_nginx      0
%define with_syslog     1

Summary:        Statistics collection daemon for filling RRD files
Name:           collectd
Version:        4.10.3
Release:        1%{?dist}
License:        GPLv2
Group:          System Environment/Daemons
URL:            http://collectd.org/
Vendor:         Karesansui Project
Packager:       Taizo ITO <taizo@karesansui-project.info>

Source:         http://collectd.org/files/%{name}-%{version}.tar.bz2
Source1:        collectd-httpd.conf
Source2:        collection.conf
Patch1:         collectd-4.10.2-include-collectd.d.patch
Patch100:       threshold_message-4.9.1.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%ifnarch ppc sparc sparc64
%if %{with_virt}
BuildRequires: libvirt-devel
%endif
%if %{with_sensors}
BuildRequires: lm_sensors-devel
%endif
%endif
BuildRequires: libxml2-devel
%if %{with_rrdtool}
BuildRequires: rrdtool-devel
%endif
%if %{with_curl}
BuildRequires: curl-devel
%endif
%if %{with_perl}
%if 0%{?fedora} >= 8
BuildRequires: perl-libs, perl-devel
%else
BuildRequires: perl
%endif
BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: perl(ExtUtils::Embed)
%endif
%if %{with_snmp}
BuildRequires: net-snmp-devel
%endif
BuildRequires: libpcap-devel
%if %{with_mysql}
BuildRequires: mysql-devel
%endif
%if %{with_ipmi}
BuildRequires: OpenIPMI-devel
%endif
%if %{with_postgresql}
BuildRequires: postgresql-devel
%endif
%if %{with_nut}
BuildRequires: nut-devel
%endif
#BuildRequires: iptables-devel
%if %{with_ping}
BuildRequires: liboping-devel
%endif
%if %{with_python}
BuildRequires: python-devel
%endif
BuildRequires: libgcrypt-devel

%description
collectd is a small daemon written in C for performance.  It reads various
system  statistics  and updates  RRD files,  creating  them if necessary.
Since the daemon doesn't need to startup every time it wants to update the
files it's very fast and easy on the system. Also, the statistics are very
fine grained since the files are updated every 10 seconds.


%if %{with_apache}
%package apache
Summary:       Apache plugin for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}
%description apache
This plugin collects data provided by Apache's 'mod_status'.
%endif

%if %{with_dns}
%package dns
Summary:       DNS traffic analysis module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}
%description dns
This plugin collects DNS traffic data.
%endif

%package email
Summary:       Email plugin for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}, spamassassin
%description email
This plugin collects data provided by spamassassin.

%if %{with_ipmi}
%package ipmi
Summary:       IPMI module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}
%description ipmi
This plugin for collectd provides IPMI support.
%endif

%if %{with_mysql}
%package mysql
Summary:       MySQL module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}
%description mysql
MySQL querying plugin. This plugins provides data of issued commands,
called handlers and database traffic.
%endif

%if %{with_nginx}
%package nginx
Summary:       Nginx plugin for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}
%description nginx
This plugin gets data provided by nginx.
%endif

%if %{with_nut}
%package nut
Summary:       Network UPS Tools module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}
%description nut
This plugin for collectd provides Network UPS Tools support.
%endif

%if %{with_perl}
%package -n perl-Collectd
Summary:       Perl bindings for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
%description -n perl-Collectd
This package contains Perl bindings and plugin for collectd.
%endif

%if %{with_ping}
%package ping
Summary:       ping module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}
%description ping
This plugin for collectd provides network latency statistics.
%endif

%if %{with_postgresql}
%package postgresql
Summary:       PostgreSQL module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}
%description postgresql
PostgreSQL querying plugin. This plugins provides data of issued commands,
called handlers and database traffic.
%endif

%if %{with_rrdtool}
%package rrdtool
Summary:       RRDTool module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}, rrdtool
%description rrdtool
This plugin for collectd provides rrdtool support.
%endif

%if %{with_rrdcached}
%package rrdcached
Summary:       rrdcached-plugin for collectd.
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}, rrdtool
BuildRequires: rrdtool-devel
%description rrdcached
This pluging collectd data provided by rrdcached.
%endif

%ifnarch ppc sparc sparc64
%if %{with_sensors}
%package sensors
Summary:       Libsensors module for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}, lm_sensors
%description sensors
This plugin for collectd provides querying of sensors supported by
lm_sensors.
%endif
%endif

%if %{with_snmp}
%package snmp
Summary:        SNMP module for collectd
Group:          System Environment/Daemons
Requires:       collectd = %{version}-%{release}, net-snmp
%description snmp
This plugin for collectd provides querying of net-snmp.
%endif

%package web
Summary:        Contrib web interface to viewing rrd files
Group:          System Environment/Daemons
Requires:       collectd = %{version}-%{release}
Requires:       collectd-rrdtool = %{version}-%{release}
Requires:       perl-HTML-Parser, perl-Regexp-Common, rrdtool-perl, httpd
%description web
This package will allow for a simple web interface to view rrd files created by
collectd.

%ifnarch ppc sparc sparc64
%if %{with_virt}
%package virt
Summary:       Libvirt plugin for collectd
Group:         System Environment/Daemons
Requires:      collectd = %{version}-%{release}
%description virt
This plugin collects information from virtualized guests.
%endif
%endif

%prep
%setup -q
%patch1 -p1
%patch100 -p1 -b .threshold_message

sed -i.orig -e 's|-Werror||g' Makefile.in */Makefile.in


%build
%configure \
    --disable-static \
    --disable-ascent \
    --disable-apple_sensors \
    --disable-dbi  \
    --disable-gmond \
    --disable-ipvs \
    --disable-java \
    --disable-memcachec \
    --disable-modbus \
    --disable-netapp \
    --disable-netlink \
    --disable-notify_desktop \
    --disable-notify_email \
    --disable-onewire \
    --disable-oracle \
    --disable-pinba \
    --disable-routeros \
    --disable-tape \
    --disable-tokyotyrant \
    --disable-xmms \
    --disable-zfs_arc \
%if %{with_apache}
    --enable-apache \
%else
    --disable-apache \
%endif
    --enable-apcups \
    --enable-battery \
    --enable-conntrack \
    --enable-contextswitch \
    --enable-cpu \
    --enable-cpufreq \
    --enable-memory \
    --enable-csv \
%if %{with_curl}
    --enable-curl \
    --enable-curl_xml \
%else
    --disable-curl \
    --disable-curl_xml \
%endif
%if %{with_curl_json}
    --enable-curl_json  \
%else
    --disable-curl_json  \
%endif
    --enable-df \
    --enable-disk \
%if %{with_dns}
    --enable-dns \
    --enable-bind \
%else
    --disable-dns \
    --disable-bind \
%endif
    --enable-email \
    --enable-entropy \
    --enable-exec \
    --enable-filecount \
    --enable-fscache \
    --enable-hddtemp \
    --enable-interface \
%if %{with_rrdtool}
    --enable-rrdtool \
%else
    --disable-rrdtool \
%endif
%if %{with_rrdcached}
    --enable-rrdcached \
%else
    --disable-rrdcached \
%endif
%if %{with_ping}
    --enable-ipmi \
%else
    --disable-ipmi \
%endif
    --enable-iptables \
    --enable-irq \
%ifnarch ppc sparc sparc64
%if %{with_virt}
    --enable-libvirt \
%else
    --disable-libvirt \
%endif
%endif
    --enable-load \
    --enable-logfile \
    --enable-madwifi \
    --enable-match_empty_counter \
    --enable-match_hashed \
    --enable-match_regex \
    --enable-match_timediff \
    --enable-match_value \
    --enable-mbmon \
    --enable-memcached \
    --enable-memory \
    --enable-multimeter \
%if %{with_mysql}
    --enable-mysql \
%else
    --disable-mysql \
%endif
    --enable-network \
    --enable-nfs \
%if %{with_nginx}
    --enable-nginx \
%else
    --disable-nginx \
%endif
    --enable-ntpd \
%if %{with_nut}
    --enable-nut \
%else
    --disable-nut \
%endif
    --enable-olsrd \
    --enable-openvpn \
%if %{with_perl}
    --enable-perl \
%else
    --disable-perl \
%endif
%if %{with_ping}
    --enable-ping \
%else
    --disable-ping \
%endif
%if %{with_postgresql}
    --enable-postgresql \
%else
    --disable-postgresql \
%endif
    --enable-powerdns \
    --enable-processes \
    --enable-protocols \
%if %{with_python}
    --enable-python \
%else
    --disable-python \
%endif
%ifnarch ppc sparc sparc64
%if %{with_sensors}
    --enable-sensors \
%else
    --disable-sensors \
%endif
%endif
    --enable-serial \
%if %{with_nut}
    --enable-snmp \
%else
    --disable-snmp \
%endif
    --enable-swap \
%if %{with_syslog}
    --enable-syslog \
%else
    --disable-syslog \
%endif
    --enable-table \
    --enable-tail \
    --enable-target_notification \
    --enable-target_replace \
    --enable-target_scale \
    --enable-target_set \
    --enable-tcpconns \
    --enable-teamspeak2 \
    --enable-ted \
    --enable-thermal \
    --enable-unixsock \
    --enable-uptime \
    --enable-users \
    --enable-uuid \
    --enable-vmem \
    --enable-vserver \
    --enable-wireless \
    --with-libiptc \
%if %{with_python}
    --with-python \
%endif
%if %{with_perl}
    --with-perl-bindings=INSTALLDIRS=vendor \
%endif

%{__make} %{?_smp_mflags}


%install
%{__rm} -rf %{buildroot}
%{__rm} -rf contrib/SpamAssassin
%{__make} install DESTDIR="%{buildroot}"

%{__install} -Dp -m0644 src/collectd.conf %{buildroot}%{_sysconfdir}/collectd.conf
%{__install} -Dp -m0755 contrib/fedora/init.d-collectd %{buildroot}%{_initrddir}/collectd

%{__install} -d -m0755 %{buildroot}%{_localstatedir}/lib/collectd/
%{__install} -d -m0755 %{buildroot}/%{_datadir}/collectd/collection3/
%{__install} -d -m0755 %{buildroot}/%{_sysconfdir}/httpd/conf.d/


# Convert docs to UTF-8
find contrib/ -type f -exec %{__chmod} a-x {} \;
for f in contrib/README ChangeLog ; do
  mv $f $f.old; iconv -f iso-8859-1 -t utf-8 < $f.old > $f; rm $f.old
done

# Remove Perl hidden .packlist files.
find %{buildroot} -name .packlist -exec rm {} \;
# Remove Perl temporary file perllocal.pod
find %{buildroot} -name perllocal.pod -exec rm {} \;

# copy web interface
cp -ad contrib/collection3/* %{buildroot}/%{_datadir}/collectd/collection3/
rm -f %{buildroot}/%{_datadir}/collectd/collection3/etc/collection.conf
cp %{SOURCE1} %{buildroot}/%{_sysconfdir}/httpd/conf.d/collectd.conf
cp %{SOURCE2} %{buildroot}%{_sysconfdir}/collection.conf
ln -s %{_sysconfdir}/collection.conf %{buildroot}/%{_datadir}/collectd/collection3/etc/collection.conf
chmod +x %{buildroot}/%{_datadir}/collectd/collection3/bin/*.cgi

# Move the Perl examples to a separate directory.
%if %{with_perl}
mkdir perl-examples
find contrib -name '*.p[lm]' -exec mv {} perl-examples/ \;
%endif

# postresql config example will be included by %doc
%if %{with_postgresql}
rm %{buildroot}%{_datadir}/collectd/postgresql_default.conf
%endif

# Move config contribs
mkdir -p %{buildroot}/etc/collectd.d/
%if %{with_apache}
cp contrib/redhat/apache.conf %{buildroot}/etc/collectd.d/apache.conf
%endif
cp contrib/redhat/email.conf %{buildroot}/etc/collectd.d/email.conf
%if %{with_mysql}
cp contrib/redhat/mysql.conf %{buildroot}/etc/collectd.d/mysql.conf
%endif
%if %{with_nginx}
cp contrib/redhat/nginx.conf %{buildroot}/etc/collectd.d/nginx.conf
%endif
%if %{with_sensors}
cp contrib/redhat/sensors.conf %{buildroot}/etc/collectd.d/sensors.conf
%endif
%if %{with_snmp}
cp contrib/redhat/snmp.conf %{buildroot}/etc/collectd.d/snmp.conf
%endif

# configs for subpackaged plugins


plugins="cpu df disk interface load logfile memory network processes swap uptime users"
%if %{with_dns}
  plugins="${plugins} dns"
%endif
%if %{with_virt}
  plugins="${plugins} libvirt"
%endif
%if %{with_rrdtool}
  plugins="${plugins} rrdtool rrdcached"
%endif
%if %{with_ipmi}
  plugins="${plugins} ipmi"
%endif
%if %{with_nut}
  plugins="${plugins} nut"
%endif
%if %{with_ping}
  plugins="${plugins} ping"
%endif
%if %{with_postgresql}
  plugins="${plugins} postgresql"
%endif
%if %{with_perl}
  plugins="${plugins} perl"
%endif
%if %{with_syslog}
  plugins="${plugins} syslog"
%endif

for p in ${plugins}
do
%{__cat} > %{buildroot}/etc/collectd.d/$p.conf <<EOF
LoadPlugin $p
EOF
done

# df.conf
%{__cat} >> %{buildroot}/etc/collectd.d/df.conf <<EOF

<Plugin "df">
    ReportReserved     false
    ReportByDevice     true
    ReportInodes       false
    IgnoreSelected     false
</Plugin>
EOF

# disk.conf
%{__cat} >> %{buildroot}/etc/collectd.d/disk.conf <<EOF

<Plugin "disk">
    Disk "/^(([hsv]|xv)d[a-f][0-9]?|([a-z]+\/)?c[0-9]d[0-9](p[0-9])?)$/"
    IgnoreSelected false
</Plugin>
EOF

# interface.conf
%{__cat} >> %{buildroot}/etc/collectd.d/interface.conf <<EOF

<Plugin "interface">
    IgnoreSelected false
</Plugin>
EOF

# logfile.conf
%{__cat} >> %{buildroot}/etc/collectd.d/logfile.conf <<EOF

<Plugin logfile>
        LogLevel "info"
        File "/var/log/collectd/collectd.log"
        Timestamp true
</Plugin>
EOF

%if %{with_virt}
# libvirt.conf
%{__cat} >> %{buildroot}/etc/collectd.d/libvirt.conf <<EOF

<Plugin "libvirt">
    HostnameFormat     name
    Connection         "qemu:///system?no_verify=1"
    #Connection         "xen:///?socket=/var/run/libvirt/libvirt-sock"
    IgnoreSelected     false
    RefreshInterval    60
</Plugin>
EOF
%endif

%if %{with_python}
# python.conf
%{__cat} >> %{buildroot}/etc/collectd.d/python.conf <<EOF
<LoadPlugin "python">
    Globals             true
</LoadPlugin>
#<Plugin "python">
#    Encoding            utf-8
#    LogTraces           true
#    Interactive         false
#    ModulePath          "/path/to/module/dir"
#    Import              "module_name"
#    <Module "module_name">
#    </Module>
#</Plugin>
EOF
%endif

%if %{with_syslog}
# syslog.conf
%{__cat} >> %{buildroot}/etc/collectd.d/syslog.conf <<EOF

<Plugin syslog>
        LogLevel info
</Plugin>
EOF
%endif

%if %{with_rrdcached}
# rrdcached.conf
%{__cat} >> %{buildroot}/etc/collectd.d/rrdcached.conf <<EOF

#<Plugin rrdcached>
#       DaemonAddress "unix:/var/rrdtool/rrdcached/rrdcached.sock"
#       DataDir "/var/lib/collectd"
#       CreateFiles true
#       CollectStatistics false
#</Plugin>
EOF
%endif

# *.la files shouldn't be distributed.
rm -f %{buildroot}/%{_libdir}/{collectd/,}*.la


%post
/sbin/chkconfig --add collectd


%preun
if [ $1 -eq 0 ]; then
    /sbin/service collectd stop &>/dev/null || :
    /sbin/chkconfig --del collectd
fi


%postun
/sbin/service collectd condrestart &>/dev/null || :


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-, root, root, -)

%config(noreplace) %{_sysconfdir}/collectd.conf
%config(noreplace) %{_sysconfdir}/collectd.d/
%if %{with_apache}
%exclude %{_sysconfdir}/collectd.d/apache.conf
%endif
%exclude %{_sysconfdir}/collectd.d/memory.conf
%exclude %{_sysconfdir}/collectd.d/cpu.conf
%exclude %{_sysconfdir}/collectd.d/df.conf
%exclude %{_sysconfdir}/collectd.d/disk.conf
%if %{with_dns}
%exclude %{_sysconfdir}/collectd.d/dns.conf
%endif
%exclude %{_sysconfdir}/collectd.d/email.conf
%if %{with_ipmi}
%exclude %{_sysconfdir}/collectd.d/ipmi.conf
%endif
%if %{with_virt}
%exclude %{_sysconfdir}/collectd.d/libvirt.conf
%endif
%exclude %{_sysconfdir}/collectd.d/load.conf
%exclude %{_sysconfdir}/collectd.d/logfile.conf
%if %{with_mysql}
%exclude %{_sysconfdir}/collectd.d/mysql.conf
%endif
%if %{with_nginx}
%exclude %{_sysconfdir}/collectd.d/nginx.conf
%endif
%exclude %{_sysconfdir}/collectd.d/network.conf
%if %{with_nut}
%exclude %{_sysconfdir}/collectd.d/nut.conf
%endif
%if %{with_perl}
%exclude %{_sysconfdir}/collectd.d/perl.conf
%endif
%if %{with_ping}
%exclude %{_sysconfdir}/collectd.d/ping.conf
%endif
%if %{with_postgresql}
%exclude %{_sysconfdir}/collectd.d/postgresql.conf
%endif
%exclude %{_sysconfdir}/collectd.d/processes.conf
%if %{with_rrdtool}
%exclude %{_sysconfdir}/collectd.d/rrdtool.conf
%endif
%if %{with_rrdcached}
%exclude %{_sysconfdir}/collectd.d/rrdcached.conf
%endif
%if %{with_sensors}
%exclude %{_sysconfdir}/collectd.d/sensors.conf
%endif
%if %{with_snmp}
%exclude %{_sysconfdir}/collectd.d/snmp.conf
%endif
%exclude %{_sysconfdir}/collectd.d/swap.conf

%{_initrddir}/collectd
%{_bindir}/collectd-nagios
%{_sbindir}/collectd
%{_sbindir}/collectdmon
%dir %{_localstatedir}/lib/collectd/

%dir %{_libdir}/collectd
%{_libdir}/collectd/apcups.so
%{_libdir}/collectd/battery.so
%{_libdir}/collectd/contextswitch.so
%{_libdir}/collectd/cpu.so
%{_libdir}/collectd/cpufreq.so
%{_libdir}/collectd/memory.so
%{_libdir}/collectd/csv.so
%if %{with_curl}
%{_libdir}/collectd/curl_xml.so
%endif
%{_libdir}/collectd/df.so
%{_libdir}/collectd/disk.so
%{_libdir}/collectd/entropy.so
%{_libdir}/collectd/exec.so
%{_libdir}/collectd/filecount.so
%{_libdir}/collectd/hddtemp.so
%{_libdir}/collectd/interface.so
%{_libdir}/collectd/iptables.so
%{_libdir}/collectd/irq.so
%{_libdir}/collectd/load.so
%{_libdir}/collectd/logfile.so
%{_libdir}/collectd/madwifi.so
%{_libdir}/collectd/match_empty_counter.so
%{_libdir}/collectd/match_hashed.so
%{_libdir}/collectd/mbmon.so
%{_libdir}/collectd/memcached.so
%{_libdir}/collectd/memory.so
%{_libdir}/collectd/multimeter.so
%{_libdir}/collectd/network.so
%{_libdir}/collectd/nfs.so
%{_libdir}/collectd/ntpd.so
%{_libdir}/collectd/olsrd.so
%{_libdir}/collectd/powerdns.so
%{_libdir}/collectd/processes.so
%if %{with_python}
%{_libdir}/collectd/python.so
%endif
%{_libdir}/collectd/serial.so
%{_libdir}/collectd/swap.so
%if %{with_syslog}
%{_libdir}/collectd/syslog.so
%endif
%{_libdir}/collectd/tail.so
%{_libdir}/collectd/target_scale.so
%{_libdir}/collectd/tcpconns.so
%{_libdir}/collectd/teamspeak2.so
%{_libdir}/collectd/thermal.so
%{_libdir}/collectd/unixsock.so
%{_libdir}/collectd/users.so
%{_libdir}/collectd/uuid.so
%{_libdir}/collectd/vmem.so
%{_libdir}/collectd/vserver.so
%{_libdir}/collectd/wireless.so

%{_libdir}/collectd/conntrack.so
%if %{with_curl}
%{_libdir}/collectd/curl.so
%endif
%{_libdir}/collectd/fscache.so
%{_libdir}/collectd/match_regex.so
%{_libdir}/collectd/match_timediff.so
%{_libdir}/collectd/match_value.so
%{_libdir}/collectd/openvpn.so
%{_libdir}/collectd/protocols.so
%{_libdir}/collectd/table.so
%{_libdir}/collectd/target_notification.so
%{_libdir}/collectd/target_replace.so
%{_libdir}/collectd/target_set.so
%{_libdir}/collectd/ted.so
%{_libdir}/collectd/uptime.so

%{_datadir}/collectd/types.db

# collectdclient - TBD reintroduce -devel subpackage?
%{_libdir}/libcollectdclient.so
%{_libdir}/libcollectdclient.so.0
%{_libdir}/libcollectdclient.so.0.0.0
%{_libdir}/pkgconfig/libcollectdclient.pc
%{_includedir}/collectd/client.h
%{_includedir}/collectd/lcc_features.h

%doc AUTHORS ChangeLog COPYING INSTALL README
%doc %{_mandir}/man1/collectd.1*
%doc %{_mandir}/man1/collectd-nagios.1*
%doc %{_mandir}/man1/collectdmon.1*
%doc %{_mandir}/man5/collectd.conf.5*
%doc %{_mandir}/man5/collectd-exec.5*
%doc %{_mandir}/man5/collectd-java.5*
%if %{with_python}
%doc %{_mandir}/man5/collectd-python.5*
%endif
%doc %{_mandir}/man5/collectd-unixsock.5*
%doc %{_mandir}/man5/types.db.5*

%if %{with_apache}
%files apache
%defattr(-, root, root, -)
%{_libdir}/collectd/apache.so
%config(noreplace) %{_sysconfdir}/collectd.d/apache.conf
%endif

%if %{with_dns}
%files dns
%defattr(-, root, root, -)
%{_libdir}/collectd/dns.so
%{_libdir}/collectd/bind.so
%config(noreplace) %{_sysconfdir}/collectd.d/dns.conf
%endif

%files email
%defattr(-, root, root, -)
%{_libdir}/collectd/email.so
%config(noreplace) %{_sysconfdir}/collectd.d/email.conf
%doc %{_mandir}/man5/collectd-email.5*

%if %{with_ipmi}
%files ipmi
%defattr(-, root, root, -)
%{_libdir}/collectd/ipmi.so
%config(noreplace) %{_sysconfdir}/collectd.d/ipmi.conf
%endif

%if %{with_mysql}
%files mysql
%defattr(-, root, root, -)
%{_libdir}/collectd/mysql.so
%config(noreplace) %{_sysconfdir}/collectd.d/mysql.conf
%endif

%if %{with_nginx}
%files nginx
%defattr(-, root, root, -)
%{_libdir}/collectd/nginx.so
%config(noreplace) %{_sysconfdir}/collectd.d/nginx.conf
%endif

%if %{with_nut}
%files nut
%defattr(-, root, root, -)
%{_libdir}/collectd/nut.so
%config(noreplace) %{_sysconfdir}/collectd.d/nut.conf
%endif

%if %{with_perl}
%files -n perl-Collectd
%defattr(-, root, root, -)
%doc perl-examples/*
%{_libdir}/collectd/perl.so
%{perl_vendorlib}/Collectd.pm
%{perl_vendorlib}/Collectd/
%config(noreplace) %{_sysconfdir}/collectd.d/perl.conf
%doc %{_mandir}/man5/collectd-perl.5*
%doc %{_mandir}/man3/Collectd::Unixsock.3pm*
%endif

%if %{with_ping}
%files ping
%defattr(-, root, root, -)
%{_libdir}/collectd/ping.so
%config(noreplace) %{_sysconfdir}/collectd.d/ping.conf
%endif

%if %{with_postgresql}
%files postgresql
%defattr(-, root, root, -)
%{_libdir}/collectd/postgresql.so
%config(noreplace) %{_sysconfdir}/collectd.d/postgresql.conf
%doc src/postgresql_default.conf
%endif

%if %{with_rrdtool}
%files rrdtool
%defattr(-, root, root, -)
%{_libdir}/collectd/rrdtool.so
%config(noreplace) %{_sysconfdir}/collectd.d/rrdtool.conf
%endif

%if %{with_rrdcached}
%files rrdcached
%defattr(-, root, root, -)
%{_libdir}/collectd/rrdcached.so
%config(noreplace) %{_sysconfdir}/collectd.d/rrdcached.conf
%endif

%ifnarch ppc sparc sparc64
%if %{with_sensors}
%files sensors
%defattr(-, root, root, -)
%{_libdir}/collectd/sensors.so
%config(noreplace) %{_sysconfdir}/collectd.d/sensors.conf
%endif
%endif

%if %{with_snmp}
%files snmp
%defattr(-, root, root, -)
%{_libdir}/collectd/snmp.so
%config(noreplace) %{_sysconfdir}/collectd.d/snmp.conf
%doc %{_mandir}/man5/collectd-snmp.5*
%endif

%files web
%defattr(-, root, root, -)
%{_datadir}/collectd/collection3/
%config(noreplace) %{_sysconfdir}/httpd/conf.d/collectd.conf
%config(noreplace) %{_sysconfdir}/collection.conf

%ifnarch ppc sparc sparc64
%if %{with_virt}
%files virt
%defattr(-, root, root, -)
%{_libdir}/collectd/libvirt.so
%config(noreplace) %{_sysconfdir}/collectd.d/libvirt.conf
%endif
%endif

%changelog
* Tue Mar 13 2012 Taizo ITO <taizo@karesansui-project.info> - 4.10.3-1
- Initial package.
