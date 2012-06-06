Installing Karesansui
=====================

## About this document ##
<a name='about_document'/>

This document is written in the Markdown format and contains some inline HTML.
This document is also available online at [https://github.com/karesansui/karesansui/blob/master/INSTALL-debian.md][install].

This document is based on Debian Squeeze (6.x x86_64). However, following the similar steps described within the document allows you to install Karesansui on any other Linux distribution.

  [install]: https://github.com/karesansui/karesansui/blob/master/INSTALL-debian.md


## Installing operating system ##
<a name='installing_operating_system'/>

Karesansui only works on systems that have the virtualization system installed.
So you need to enable KVM (Kernel-based Virtual Machine).

Just do usual installation, but be careful of the points below:

* (Required) On software setup, check "_Virtual Host_" and "_Customize Now_"
* (Required) On software group setup, check "_Virtualization_" - "_Virtualization_","_Virtualization Client_","_Virtualization Platform_" ,"_Virtualization Tools_"

If you want to enable KVM after installing OS, you need to execute the following commands:

A hash (#) prompt indicates you are logged-in as the root user; a dollar ($) prompt indicates you are logged-in as the specific general account.

###For `Debian 6`:

    # aptitude install qemu-kvm libvirtd-bin vlan ifenslave bridge-utils
    # invoke-rc.d libvirt-bin start
    # /sbin/modprobe -b kvm-intel (or /sbin/modprobe -b kvm-amd)

Please make sure that the kernel modules for KVM are loaded.

    # /sbin/lsmod | grep kvm
    kvm_intel              50380  0 
    kvm                   305081  1 kvm_intel

 *If you use an AMD processor, _kvm_amd_ must be loaded instead of _kvm_intel_.


## Configuring the network ##
<a name='configuring_the_network'/>

After installing Linux, the first Ethernet interface is typically identified as _eth0_ and allows only outbound communication from the KVM guests.
To share the interface with KVM guests and enable full network access, including communication to and from an external host, you need to set up a Linux bridge in Linux system.
Although a bit out of scope of this do we asume you want redundancy for each link plus multiple networks available to each guest. So we combine both bonding multiple interfaces and bridging those to the guests and host. In this example we use 6 ethernet connections to establish 3 redundant links. On top of that we also add tagged vlans to one bond.

### Setting up bonds, vlans and bridges ###
we create the following bonds (this way we distribute the ethernet connections across different pci cards to be even safe from device and off course, cables are connected to defferent switches):
  # bond0: eth0 and eth2 (connected to management lan, this is where the kvm server will have its own ip address.)
  # bond1: eth1 and eth4 (connected to some internet feed)
  # bond2: eth3 and eth5 (connected to vlan tagged lans which will have multiple bridges, one for each vlan in order to provide untagged vlans to the guests that have an interface in that bridge)

Note: If you are accessing the server via SSH or Telnet instead of console, you MAY be disconnected when you restart the network service after modifying network settings. You should configure the settings via the local console. 

###Procedure for `Debian 6`:

####1. Install networkdrivers

    # aptitude install vlan ifenslave bridge-utils

####2. Create the network interfaces file

The script file path is _/etc/network/interfaces_.

    # The loopback network interface
    auto lo
    iface lo inet loopback

    allow-hotplug eth0 eth1 eth2 eth3 eth4 eth5

    auto bond0
    iface bond0 inet manual
      bond_mode active-backup
      bond_miimon 100 
      slaves eth0 eth2

    auto br-lan
    iface br-lan inet static
      address 10.1.1.2
      netmask 255.255.0.0
      gateway 10.1.1.1
      bridge_ports bond0
      bridge_stp off 

    auto bond1
    iface bond1 inet manual
      bond_mode active-backup
      bond_miimon 100 
      slaves eth1 eth4

    auto br-inet
    iface br-inet inet manual
      bridge_ports bond1
      bridge_stp off 

    auto bond2
    iface bond2 inet manual
      bond_mode active-backup
      bond_miimon 100 
      slaves eth3 eth5

    auto vlan10
    iface vlan10 inet manual
      vlan-raw-device bond2

    auto br-vlan10
    iface br-vlan10 inet manual
      bridge_ports vlan10
      bridge_stp off 

    auto vlan11
    iface vlan11 inet manual
      vlan-raw-device bond2

    auto br-vlan11
    iface br-vlan11 inet manual
      bridge_ports vlan11
      bridge_stp off

####3. Configure Bonding

You need to config bonding a bit to be able to use multiple bonds. Therefor add this to a file _/etc/modprobe.d/bonding.conf_:

    alias bond0 bonding
    alias bond1 bonding
    alias bond2 bonding
    options bonding mode=1 miimon=100 max_bonds=3

####4. Add the accepted bridge rule to your iptables firewall script

I don't know where you save your script on Debian, but it should have something like:

    # /sbin/iptables -A FORWARD -m physdev --physdev-is-bridged -j ACCEPT

####5. Restart network services

In order for all the network config modifications to take effect, you need to restart your network services.

    # invoke-rc.d networking stop && invoke-rc.d networking start

####5. Check the status of current interfaces

    # /bin/ip a

should output something like:

    1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN 
        link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
        inet 127.0.0.1/8 scope host lo
        inet6 ::1/128 scope host 
           valid_lft forever preferred_lft forever
    2: eth0: <BROADCAST,MULTICAST,SLAVE,UP,LOWER_UP> mtu 1500 qdisc mq master bond0 state UP qlen 1000
        link/ether 3c:4a:92:6d:7e:a2 brd ff:ff:ff:ff:ff:ff
    3: eth1: <NO-CARRIER,BROADCAST,MULTICAST,SLAVE,UP> mtu 1500 qdisc mq master bond1 state DOWN qlen 1000
        link/ether 3c:4a:92:6d:7e:a4 brd ff:ff:ff:ff:ff:ff
    4: eth2: <BROADCAST,MULTICAST,SLAVE,UP,LOWER_UP> mtu 1500 qdisc mq master bond0 state UP qlen 1000
        link/ether 3c:4a:92:6d:7e:a2 brd ff:ff:ff:ff:ff:ff
    5: eth3: <NO-CARRIER,BROADCAST,MULTICAST,SLAVE,UP> mtu 1500 qdisc mq master bond2 state DOWN qlen 1000
        link/ether 3c:4a:92:6d:7e:a8 brd ff:ff:ff:ff:ff:ff
    6: eth4: <NO-CARRIER,BROADCAST,MULTICAST,SLAVE,UP> mtu 1500 qdisc mq master bond1 state DOWN qlen 1000
        link/ether 3c:4a:92:6d:7e:a4 brd ff:ff:ff:ff:ff:ff
    7: eth5: <NO-CARRIER,BROADCAST,MULTICAST,SLAVE,UP> mtu 1500 qdisc mq master bond2 state DOWN qlen 1000
        link/ether 3c:4a:92:6d:7e:a8 brd ff:ff:ff:ff:ff:ff
    8: bond0: <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP 
        link/ether 3c:4a:92:6d:7e:a2 brd ff:ff:ff:ff:ff:ff
        inet6 fe80::3e4a:92ff:fe6d:7ea2/64 scope link 
           valid_lft forever preferred_lft forever
    9: bond1: <BROADCAST,MULTICAST,MASTER,UP> mtu 1500 qdisc noqueue state UNKNOWN 
        link/ether 3c:4a:92:6d:7e:a4 brd ff:ff:ff:ff:ff:ff
    10: bond2: <BROADCAST,MULTICAST,PROMISC,MASTER,UP> mtu 1500 qdisc noqueue state UNKNOWN 
        link/ether 3c:4a:92:6d:7e:a8 brd ff:ff:ff:ff:ff:ff
    11: br-lan: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN 
        link/ether 3c:4a:92:6d:7e:a2 brd ff:ff:ff:ff:ff:ff
        inet 10.1.1.2/16 brd 10.120.255.255 scope global br-lan
        inet6 fe80::3e4a:92ff:fe6d:7ea2/64 scope link 
           valid_lft forever preferred_lft forever
    12: br-inet: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN 
        link/ether 3c:4a:92:6d:7e:a4 brd ff:ff:ff:ff:ff:ff
        inet6 fe80::3e4a:92ff:fe6d:7ea4/64 scope link 
           valid_lft forever preferred_lft forever
    13: vlan10@bond2: <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP 
        link/ether 3c:4a:92:6d:7e:a8 brd ff:ff:ff:ff:ff:ff
        inet6 fe80::3e4a:92ff:fe6d:7ea8/64 scope link 
           valid_lft forever preferred_lft forever
    14: br-vlan10: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN 
        link/ether 3c:4a:92:6d:7e:a8 brd ff:ff:ff:ff:ff:ff
        inet6 fe80::3e4a:92ff:fe6d:7ea8/64 scope link 
           valid_lft forever preferred_lft forever
    15: vlan11@bond2: <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP 
        link/ether 3c:4a:92:6d:7e:a8 brd ff:ff:ff:ff:ff:ff
        inet6 fe80::3e4a:92ff:fe6d:7ea8/64 scope link 
           valid_lft forever preferred_lft forever
    16: br-vlan11: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN 
        link/ether 3c:4a:92:6d:7e:a8 brd ff:ff:ff:ff:ff:ff
        inet6 fe80::3e4a:92ff:fe6d:7ea8/64 scope link 
           valid_lft forever preferred_lft forever

###Alternate Procedure:
This should work on a Debian box as well. I don't extend it to the docu above though

####1. Activate promiscuous mode on eth0.

    # /sbin/ifconfig eth0 0.0.0.0 promisc up

####2. Create the bridge interface.

    # /usr/sbin/brctl addbr br0

####3. Add interfaces to the bridge. 

    # /usr/sbin/brctl addif br0 eth0

####4. Put up the bridge. 

    # ifconfig br0 up

####5. Configure the virtual bridge interface to take part in your network.

    # ifconfig br0 172.23.233.1 netmask 255.255.255.0
    # route add default gw 172.23.233.254


## Installing dependent software/libs ##
<a name='installing_dependent_software_libs'/>

To install and set up Karesansui, you need to install it's dependent software/libs first.
You can install most of them by using the software updater provided by each distribution, but some software need to be built on your machine.

###For `Debian 6`:

#####Fetching packages from Debian repository.

    # aptitude install python-mako python-sqlalchemy python-simplejson rrdtool python-rrdtool python-flup collectd collectd-utils python-webpy tightvnc-java
    # aptitude install git python-setuptools python-virtualenv python-pip
    # aptitude install pbuilder cdbs python-dev

#####Fetching packages from PyPI.

    # easy_install PyXML

## Installing pysilhouette ##
<a name='installing_pysilhouette'/>

### What is pysilhouette? ###

Pysilhouette is a python-based background job manager, intended to co-work with various python-based web applications such as Karesansui.
It makes it available to get job status to programmers, which was difficult in http-based stateless/interactive session before.
It is also developed by Karesansui Project Team.

####1. Fetching pysilhouette source code from github repository.

    $ git clone git://github.com/karesansui/pysilhouette.git

####2. Installing pysilhouette with Python's distutils.

    $ cd pysilhouette
    $ python setup.py build
    # python setup.py install --root=/ --record=INSTALLED_FILES --prefix=/usr --install-layout=deb

    #### Create pysilhouette account ####
    # /usr/sbin/useradd -c "Pysilhouette" -d /var/lib/pysilhouette -s /bin/false -r pysilhouette

    #### Create the application's system directories ####
    # mkdir /etc/pysilhouette
    # mkdir /var/log/pysilhouette
    # mkdir /var/lib/pysilhouette
    # chown -R pysilhouette:pysilhouette /var/log/pysilhouette
    # chown -R pysilhouette:pysilhouette /var/lib/pysilhouette

    #### Copy several programs, configuration files and SysV init script ####
    # cp -f pysilhouette/debian/silhouetted.init /etc/init.d/silhouetted 
    # cp -f pysilhouette/debian/performerd.init /etc/init.d/performerd 
    # cp -f pysilhouette/debian/silhouetted.default /etc/default/silhouetted
    # cp -f pysilhouette/sample/log.conf.example /etc/pysilhouette/log.conf
    # cp -f pysilhouette/sample/silhouette.conf.example /etc/pysilhouette/silhouette.conf
    # cp -f pysilhouette/sample/whitelist.conf.example /etc/pysilhouette/whitelist.conf
    # ln -s `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib(0,0)"`/pysilhouette/silhouette.py /usr/bin
    # cp -f pysilhouette/tools/psil-cleandb /usr/sbin
    # cp -f pysilhouette/tools/psil-set /usr/sbin
    # chmod 0744 /usr/sbin/psil-*

    #### Modify the following files if necessary. 
    ## vi /etc/init.d/silhouetted
    ## vi /etc/default/silhouetted

## Installing karesansui ##
<a name='installing_karesansui'/>

####1. Fetching karesansui source code from github repository.

    $ git clone git://github.com/karesansui/karesansui.git # No need if already downloaded.

####2. Installing karesansui with Python's distutils.

    $ cd karesansui
    $ python setup.py build
    # python setup.py install --record=INSTALLED_FILES --install-scripts=/usr/share/karesansui/bin --prefix=/usr --install-layout=deb

    #### Create kss account ####
    # /usr/sbin/useradd -c "Karesansui Project" -s /bin/false -r -m -d /var/lib/karesansui kss
    # gpasswd -a libvirt-qemu kss

    #### Create the application's system directories ####
    # mkdir -p /etc/karesansui/virt
    # mkdir -p /var/log/karesansui
    # mkdir -p /var/lib/karesansui/{tmp,cache}

    #### Change attributes of the application's directories/files ####
    # chgrp -R kss   /etc/karesansui
    # chmod g+rwx    /etc/karesansui/virt
    # chmod o-rwx    /etc/karesansui/virt
    # chmod -R g+rw  /etc/karesansui
    # chmod -R o-rwx /etc/karesansui
    # chgrp -R kss   /var/log/karesansui
    # chmod -R 0770  /var/log/karesansui
    # chgrp -R kss   /var/lib/karesansui
    # chmod -R 0770  /var/lib/karesansui
    # chgrp -R kss `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib(0,0)"`/karesansui
    # find `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib(0,0)"`/karesansui -type d -exec chmod g+rwx \{\} \;
    # find /usr/share/karesansui/ -type d -exec chgrp -R kss \{\} \;
    # find /usr/share/karesansui/ -type d -exec chmod g+rwx \{\} \;

    #### Copy several programs, configuration files and SysV init script ####
    # cp -f  karesansui/sample/application.conf.example /etc/karesansui/application.conf
    # cp -f  karesansui/sample/log.conf.example /etc/karesansui/log.conf
    # cp -f  karesansui/sample/service.xml.example /etc/karesansui/service.xml
    # cp -f  karesansui/sample/logview.xml.example /etc/karesansui/logview.xml
    # cp -f  karesansui/sample/cron_cleantmp.example /etc/cron.d/karesansui_cleantmp
    # cp -f  karesansui/sample/whitelist.conf.example /etc/pysilhouette/whitelist.conf


## Configuring pysilhouette ##
<a name='configuring_pysilhouette'/>

You may need to modify the following configuration files.

<table style='border: solid 1px #000000; border-collapse: collapse;'>
 <tr><th>File name</th><th>Description</th></tr>
 <tr>
  <td nowrap>/etc/pysilhouette/silhouette.conf</td>
  <td>Configuration file for the silhouetted daemon.</td>
 </tr>
 <tr>
  <td nowrap>/etc/pysilhouette/log.conf</td>
  <td>Configuration file for logging.</td>
 </tr>
 <tr>
  <td nowrap>/etc/pysilhouette/whitelist.conf</td>
  <td>Contains a whitelist of commands that can be executed by the pysilhouette as a background job.</td>
 </tr>
 <tr>
  <td nowrap>/etc/sysconfig/silhouetted</td>
  <td>Used to set some other bootup parameters.</td>
 </tr>
</table>

Add pysilhouette as a service and enable it for auto start at bootup.

    # update-rc.d silhouetted defaults

## Configuring karesansui ##
<a name='configuring_karesansui'/>

You may need to modify the following configuration files.

<table style='border: solid 1px #000000; border-collapse: collapse;'>
 <tr><th>File name</th><th>Description</th></tr>
 <tr>
  <td nowrap>/etc/karesansui/application.conf</td>
  <td>Configuration file for karesansui(<b>*You need to set 'application.uniqkey' parameter. Its value is supposed to be generated by the uuidgen program.</b>)</td>
 </tr>
 <tr>
  <td nowrap>/etc/karesansui/log.conf</td>
  <td>Configuration file for logging.</td>
 </tr>
 <tr>
  <td nowrap>/etc/karesansui/service.xml</td>
  <td>Used to define services related to karesansui.</td>
 </tr>
 <tr>
  <td nowrap>/etc/karesansui/service.xml</td>
  <td>Used to define log files related to karesansui.</td>
 </tr>
 <tr>
  <td nowrap>/etc/cron.d/karesansui_cleantmp</td>
  <td>Configuration file for the cron daemon. Clean/delete unnecessary temporary files at a specific interval.</td>
 </tr>
</table>


## Creating database for karesansui ##
<a name='creating_database_for_karesansui'/>

With a script bundled with the source code, you can create a database for karesansui and insert information of the administrator into the database.

    # python karesansui/tools/initialize_database.py -m <Administrator's E-mail Address> -p <Administrator's Password> -l en_US

If you use a SQLite database, you must change the attributes of the database file.

    # chgrp -R kss /var/lib/karesansui/karesansui.db
    # chmod -R g+w /var/lib/karesansui/karesansui.db
    # chmod -R o-rwx /var/lib/karesansui/karesansui.db


## Creating database for pysilhouette ##
<a name='creating_database_for_pysilhouette'/>

You can create a database for pysilhouette by executing the following command:

    # python -c "import karesansui; from pysilhouette.prep import readconf; karesansui.sheconf = readconf('/etc/pysilhouette/silhouette.conf'); import karesansui.db._2pysilhouette; karesansui.db._2pysilhouette.get_metadata().create_all()"

If you use a SQLite database, you must change the attributes of the database file.

    # chgrp -R kss /var/lib/pysilhouette/
    # chmod -R g+rw /var/lib/pysilhouette/
    # chmod -R o-rwx /var/lib/pysilhouette/


## Starting pysilhouette service ##
<a name='starting_pysilhouette_service'/>

    # invoke-rc.d silhouetted start


## Configuring libvirt ##
<a name='configuring_libvirt'/>

####1. Edit libvirt configuration file

You may need to modify the following configuration files.

__/etc/libvirt/libvirtd.conf__

 * listen_tcp = 1
 * tcp_port = "16509"
 * unix_sock_group = "kss"
 * auth_tcp = "none"

__/etc/default/libvirt-bin__

 * libvirtd_opts="-d --listen"

####2. Create directories for libvirt

    # mkdir -p /var/lib/libvirt/{disk,domains,snapshot}
    # chgrp -R kss  /var/lib/libvirt
    # chmod -R 0770 /var/lib/libvirt

    # chgrp -R kss /etc/libvirt
    # find /etc/libvirt -type d -exec chmod g+rwx \{\} \;

####3. Create a TLS certificates for libvirt 

First, set up a Certificate Authority (CA).

    # aptitude install gnutls-bin
    $ certtool --generate-privkey > cakey.pem
    $ vi ca.info
    cn = Name of your organization
    ca
    cert_signing_key
    $ certtool --generate-self-signed --load-privkey cakey.pem --template ca.info --outfile cacert.pem

Issue server certificates.

    $ certtool --generate-privkey > serverkey.pem
    $ vi server.info
    organization = Name of your organization
    cn = Your FQDN
    tls_www_server
    encryption_key
    signing_key
    $ certtool --generate-certificate --load-privkey serverkey.pem   --load-ca-certificate cacert.pem --load-ca-privkey cakey.pem   --template server.info --outfile servercert.pem

Install the certificates.

    # mkdir -p /etc/pki/libvirt/private/
    # mkdir -p /etc/pki/CA/
    # cp -i cacert.pem /etc/pki/CA/
    # cp -i servercert.pem /etc/pki/libvirt/
    # cp -i serverkey.pem /etc/pki/libvirt/private/

####4. Enable libvirtd service

Restart service and enable it for auto start at bootup.

    # update-rc.d libvirt-bin defaults
    # invoke-rc.d libvirt-bin restart

####5. Check for connectivity to libvirtd

Please make sure that virsh client can connect to the QEMU monitor with libvirt.

    # virsh -c qemu+tcp://localhost:16509/system list

If the connection attempt succeed, it will display message as below:

    Id Name                 State
    ----------------------------------

####6. Create the default storage pool for libvirt

    # KARESANSUI_CONF=/etc/karesansui/application.conf python -c "from karesansui.prep import built_in; built_in()"
    # /usr/share/karesansui/bin/create_storage_pool.py --name=default --target_path=/var/lib/libvirt/domains --mode=0770 --owner=0 --group=`id -g kss` --type=dir
    # virsh pool-refresh default
    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*


## Checking for connectivity to Karesansui management console
<a name='checking_for_connectivity_to_karesansui_management_console'/>

You have now finished setting up Karesansui itself.

Confirm that you can access the Karesansui URL from your browser through the app's python-webpy built-in web server.

First, run the karesansui program using the built-in server.

    # su -s /bin/bash kss -c "KARESANSUI_CONF=/etc/karesansui/application.conf SEARCH_PATH= /usr/share/karesansui/bin/karesansui.fcgi"

If the setting up is successful, it always seems to display the following:

<pre>
http://0.0.0.0:8080/
</pre>

Please access the following URL from your browser after starting the server. 
The username and password values for HTTP basic authentication must match the ones specified during database creation 'Creating database for karesansui'.

<pre>
http://[your-server-name]:8080/karesansui/v3/
</pre>

If the console is displayed correctly, the installation appears to be completed successfully.


Using other HTTP server
=======================

## With Lighttpd ##
<a name='with_lighttpd'/>

###Procedure for `CentOS 6`:

####1. Installing packages.

    # aptitude install lighttpd
    # lighty-enable-mod fastcgi

####2. Configuring group members.

Add _lighttpd_ user to _kss_ group and _kss_ user to _lighttpd_ group.

    # gpasswd -a lighttpd kss
    # gpasswd -a kss lighttpd

####3. Configuring lighttpd settings.

Append the line below to _/etc/lighttpd/lighttpd.conf_.

    include "conf.d/karesansui.conf"

Edit _/etc/lighttpd/modules.conf_ to enable the following modules.

    mod_alias
    mod_rewrite
    mod_fastcgi

Copy the sample configuration file bundled with the source code to the location of lighttpd config directory, and edit it if necessary.

    # cp karesansui/sample/lighttpd/karesansui.conf /etc/lighttpd/conf.d/


####4. Setting up a simple SSL configuration with lighttpd

    # mkdir -p /etc/lighttpd/ssl
    # openssl req -new -x509 -keyout /etc/lighttpd/ssl/server.pem -out /etc/lighttpd/ssl/server.pem -days 3650 -nodes
    # chmod 400 /etc/lighttpd/ssl/server.pem

####5. Start web service

If you have already tried to run Karesansui with other web server, you need to remove existing files with the following command:

    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*log

Restart service and enable it for auto start at bootup.

    # update-rc.d lighttpd defaults
    # invoke-rc.d lighttpd restart

If SELinux is set to "Enforcing", lighttpd may not work properly. Set it to "Permissive" mode and try to restart the service again.

    # /usr/sbin/setenforce 0
    # invoke-rc.d lighttpd restart

Moreover, if you need to use "Permissive" mode at the next reboot, you have to modify /etc/selinux/config file as well.

    SELINUX=permissive

####6. Checking for connectivity to Karesansui management console

Please access the following URL from your browser after starting the server. 
The username and password values for HTTP basic authentication must match the ones specified during database creation 'Creating database for karesansui'.

<pre>
https://[your-server-name]/karesansui/v3/
</pre>


## With Apache ##
<a name='with_apache'/>

###Procedure for `CentOS 6`:

####1. Installing packages.

Install several packages from [RepoForge](http://repoforge.org/) repository.

    # wget http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm
    # rpm -Uvh rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm 
    # yum install httpd mod_fastcgi

####2. Configuring group members.

Add _apache_ user to _kss_ group and _kss_ user to _apache_ group.

    # gpasswd -a apache kss
    # gpasswd -a kss apache

####3. Configuring apache settings.

Copy the sample configuration file bundled with the source code to the location of httpd config directory, and edit it if necessary.

    # cp karesansui/sample/apache/fastcgi.conf /etc/httpd/conf.d/

####4. Start web service

If you have already tried to run Karesansui with other web server, you need to remove existing files with the following command:

    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*log

Restart service and enable it for auto start at bootup.

    # update-rc.d apache2 defaults
    # invoke-rc.d apache2 restart

    # chmod 777 /tmp/dynamic
    # chown apache:apache /tmp/dynamic
    # invoke-rc.d apache2 restart

If SELinux is set to "Enforcing", apache may not work properly. Set it to "Permissive" mode and try to restart the service again.

    # /usr/sbin/setenforce 0
    # invoke-rc.d apache2 restart

Moreover, if you need to use "Permissive" mode at the next reboot, you have to modify /etc/selinux/config file as well.

    SELINUX=permissive

####6. Checking for connectivity to Karesansui management console

Please access the following URL from your browser after starting the server. 
The username and password values for HTTP basic authentication must match the ones specified during database creation 'Creating database for karesansui'.

<pre>
https://[your-server-name]/karesansui/v3/
</pre>


## With Nginx ##
<a name='with_nginx'/>

###Procedure for `CentOS 6`:

####1. Installing packages.

    # aptitude install nginx spawn-fcgi

####2. Configuring group members.

Add _nginx_ user to _kss_ group and _kss_ user to _nginx_ group.

    # gpasswd -a nginx kss
    # gpasswd -a kss nginx

####3. Configuring nginx settings.

Copy the sample configuration file bundled with the source code to the location of nginx config directory, and edit it if necessary.

    # cp karesansui/sample/nginx/karesansui.conf /etc/nginx/conf.d/

####4. Start web service

If you have already tried to run Karesansui with other web server, you need to remove existing files with the following command:

    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*log

First, run the karesansui program using the built-in server.

    # su -s /bin/bash kss -c "KARESANSUI_CONF=/etc/karesansui/application.conf SEARCH_PATH= /usr/share/karesansui/bin/karesansui.fcgi 127.0.0.1:8080"

Restart service and enable it for auto start at bootup.

    # update-rc.d nginx defaults
    # invoke-rc.d nginx restart

####6. Checking for connectivity to Karesansui management console

Please access the following URL from your browser after starting the server. 
The username and password values for HTTP basic authentication must match the ones specified during database creation 'Creating database for karesansui'.

<pre>
http://[your-server-name]/karesansui/v3/
</pre>


Other settings
==============

## Configuring collectd ##
<a name='configuring_collectd'/>

### What is collectd? ###

[collectd](http://collectd.org/) is a daemon which collects system information periodically and provides means to store performance data.
In Karesansui, It is used to display the statistics graphs.

###Procedure for `CentOS 6`:

You may need to change the settings for the collectd plugins.
Please follow the steps described below.

####1. Edit collectd configuration file. (/etc/collectd.conf)

__Global settings__

    Hostname    your.host.name
    FQDNLookup   true
    BaseDir     "/var/lib/collectd"
    PIDFile     "/var/run/collectd.pid"
    PluginDir   "/usr/lib64/collectd/"
    TypesDB     "/usr/share/collectd/types.db"
    Interval     10
    Timeout      2
    ReadThreads  5

__LoadPlugin section__

    LoadPlugin cpu
    LoadPlugin df
    LoadPlugin disk
    LoadPlugin interface
    LoadPlugin libvirt
    LoadPlugin load
    LoadPlugin memory
    LoadPlugin network
    LoadPlugin rrdtool
    LoadPlugin uptime
    LoadPlugin users

__Plugin configuration__

    <Plugin df>
        ReportReserved     false
        ReportByDevice     true
        ReportInodes       false
        IgnoreSelected     false
    </Plugin>

    <Plugin disk>
        Disk "/^[hs]d[a-f][0-9]?$/"
        IgnoreSelected false
    </Plugin>

    <Plugin interface>
       IgnoreSelected false
    </Plugin>

    <Plugin libvirt>
        HostnameFormat     name
        Connection         "qemu+tcp://127.0.0.1:16509/system?no_verify=1"
        IgnoreSelected     false
        RefreshInterval    60
    </Plugin>

    <Plugin rrdtool>
        DataDir "/var/lib/collectd"
        CacheTimeout 120
        CacheFlush   900
    </Plugin>

####2. Restart collectd service.

In order for all the modifications to take effect, you need to restart collectd service.

    # update-rc.d collectd defaults
    # invoke-rc.d collectd restart


Feedback & Suggestions
======================
Is there something wrong, outdated or unclear in this document? Please let us know so we can make it better. If you can contribute anything, we would greatly appreciate it!

