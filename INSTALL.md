Installing Karesansui
=====================

## About this document ##

This document is written in the Markdown format and contains some inline HTML.
This document is also available online at [https://github.com/karesansui/karesansui/blob/master/INSTALL.md][install].

This document is based on CentOS 6.x (x86_64). However, following the similar steps of the document allows you to install Karesansui on any other Linux distribution.

  [install]: https://github.com/karesansui/karesansui/blob/master/INSTALL.md


## Installing operating system ##

Karesansui only works on systems that have the virtualization system installed.
So you need to enable KVM (Kernel-based Virtual Machine).

Just do usual installation, but be careful of the points below:

* (Required) On software setup, check "_Virtual Host_" and "_Customize Now_"
* (Required) On software group setup, check "_Virtualization_" - "_Virtualization_","_Virtualization Client_","_Virtualization Platform_" ,"_Virtualization Tools_"

If you want to enable KVM after installing OS, you need to execute the following commands:

A hash (#) prompt indicates you are logged-in as the root user; a dollar ($) prompt indicates you are logged-in as the specific general account.

###For `CentOS 6`:

    # yum groupinstall "Virtualization" "Virtualization Client" "Virtualization Platform" "Virtualization Tools"
    # /sbin/modprobe -b kvm-intel (or /sbin/modprobe -b kvm-amd)
    # /sbin/modprobe -b vhost_net

Please make sure that the kernel modules for KVM are loaded.

    # /sbin/lsmod | grep kvm
    kvm_intel              50380  0 
    kvm                   305081  1 kvm_intel

 *In case of the AMD processor _kvm_amd_ must be loaded instead of _kvm_intel_.


## Configuring the network ##

After installing Linux, the first Ethernet interface is typically identified as _eth0_ and allows only outbound communication from the KVM guests.
To share the interface with KVM guests and enable full network access, including communication to and from an external host, you need to set up a Linux bridge in Linux system.

### Setting up a network bridge ###

Note: If you are accessing the server via SSH or Telnet instead of console, you MAY be disconnected when you restarting the network service after modifying network settings. You should configure the settings via the local console. 

###Procedure for `CentOS 6`:

####1. Create the network script for defining a Linux bridge associated with the network card.

The script file path is _/etc/sysconfig/network-scripts/ifcfg-br0_, where _br0_ is the name of the bridge.

    # cp /etc/sysconfig/network-scripts/ifcfg-{eth0,br0}

####2. Edit the script file for br0 (/etc/sysconfig/network-scripts/ifcfg-br0)

If your network card is configured with a static IP address, your original network script file should look similar to the following example:

    DEVICE=eth0
    HWADDR=<the ethernet hardware address for this device>
    ONBOOT=yes
    IPADDR=<the IP address>
    BOOTPROTO=static
    NETMASK=<the netmask>
    TYPE=Ethernet

  You need to edit _ifcfg-br0_ as shown in the following example.

    DEVICE=br0                # <- Changed
    #HWADDR=<the ethernet hardware address for this device>  # <- Commented out
    ONBOOT=yes
    IPADDR=<the IP address>
    BOOTPROTO=static
    NETMASK=<the netmask>
    TYPE=Bridge               # <- Changed

####3. Edit the script file for eth0 (/etc/sysconfig/network-scripts/ifcfg-eth0)

Now you need to configure your network script for eth0. You will already have a script for _eth0_, but you’ll need to modify it by adding one line as _BRIDGE=br0_ so that it looks similar to the following script.

    DEVICE=eth0
    HWADDR=<the ethernet hardware address for this device>
    ONBOOT=yes
    #IPADDR=<the IP address>  # <- Commented out
    #BOOTPROTO=none           # <- Commented out
    #NETMASK=<the netmask>    # <- Commented out
    TYPE=Ethernet
    BRIDGE=br0                # <- Added

####4. Restart network services

In order for all the network script modifications to take effect, you need to restart your network services.

    # /etc/init.d/network restart

####5. Check the status of the current interfaces

    # /sbin/ifconfig -a

###Alternate Procedure:

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


## Installing dependencies ##

To install and set up Karesansui, you need to install its dependencies firstly.
You can install most of them by using the software updater provided by each distribution, but some softwares need to be built on your machine.

###For `CentOS 6`:

#####Fetching packages from CentOS-Base repository.

    # yum install PyXML python-mako python-sqlalchemy python-simplejson rrdtool rrdtool-python

#####Fetching packages from [EPEL(Extra Packages for Enterprise Linux)](http://fedoraproject.org/wiki/EPEL) repository.

    # wget ftp://ftp.iij.ad.jp/pub/linux/fedora/epel/6/x86_64/epel-release-6-5.noarch.rpm
    # rpm -Uvh epel-release-6-5.noarch.rpm 
    # yum install python-flup python-sqlite2
    # yum install collectd collectd-ping collectd-rrdtool collectd-virt

#####Building packages that are not provided by the offifial or the third party repositories on your machine.

######Step 1. Setting up RPM build environment.

Create a seperate account for building RPMs and set up the environment for it:

    # yum install rpm-build
    # useradd rpmbuild
    # su - rpmbuild
    $ mkdir -p ~/pkgs/{BUILD,RPMS/{i{3,4,5,6}86,x86_64,noarch},SOURCES,SPECS,SRPMS}
    $ echo '%_topdir %(echo $HOME)/pkgs' > ~/.rpmmacros

######Step 2. Fetching Karesansui source code from github repository.

    # yum install git python-setuptools
    # su - rpmbuild
    $ git clone git://github.com/karesansui/karesansui.git

######Step 3. Building python-webpy package.

    # su - rpmbuild
    $ cd ~/pkgs/SOURCES/
    $ wget http://webpy.org/static/web.py-0.36.tar.gz
    $ rpmbuild -ba ~/karesansui/sample/specs/python-webpy/python-webpy.spec

######Step 4. Building IPAexfont package.

    # su - rpmbuild
    $ cd ~/pkgs/SOURCES/
    $ wget http://iij.dl.sourceforge.jp/ipafonts/49986/IPAexfont00103.zip
    $ cp ~rpmbuild/karesansui/sample/specs/IPAexfont/09-ipaexfont.conf .
    $ rpmbuild -ba ~/karesansui/sample/specs/IPAexfont/IPAexfont.spec 

######Step 5. Building tightvnc-java package.

    # su - rpmbuild
    $ cd ~/pkgs/SOURCES/
    $ wget http://downloads.sourceforge.net/sourceforge/vnc-tight/tightvnc-1.3.10_javabin.tar.gz
    $ wget http://downloads.sourceforge.net/sourceforge/vnc-tight/tightvnc-1.3.10_javasrc.tar.gz
    $ rpmbuild -ba ~/karesansui/sample/specs/tightvnc-java/tightvnc-java.spec 

######Step 6. Installing the newly built packages.

Now you can install the newly built packages.

    $ cd ~/pkgs/RPMS/noarch
    # rpm -Uvh python-webpy-*.el6.noarch.rpm IPAexfont-*.el6.noarch.rpm tightvnc-java-*.el6.noarch.rpm 


## Installing pysilhouette ##

### What is pysilhouette ? ###

Pysilhouette is a python-based background job manager, intended to co-work with various python-based web applications such as Karesansui.
It makes it available to get job status to programmers, which was difficult in http-based stateless/interactive session before.
It is also developed by Karesansui Project Team.

###Procedure for `CentOS 6`:

####1. Fetching pysilhouette source code from github repository.

    # su - rpmbuild
    $ git clone git://github.com/karesansui/pysilhouette.git

####2a. (Method 1) Building pysilhouette package and installing it.

    $ cd ~/pysilhouette
    $ python setup.py sdist
    $ rpmbuild -ta dist/pysilhouette-*.tar.gz
    # rpm -Uvh ~rpmbuild/pkgs/RPMS/noarch/pysilhouette-*.noarch.rpm

####2b. (Method 2) Installing pysilhouette with Python's distutils.

    $ cd ~/pysilhouette
    $ python setup.py build
    # python setup.py install --root=/ --record=INSTALLED_FILES

    #### Create pysilhouette account ####
    # /usr/sbin/useradd -c "Pysilhouette" -s /bin/false -r pysilhouette

    #### Create the application's system directories ####
    # mkdir /etc/pysilhouette
    # mkdir /var/log/pysilhouette
    # mkdir /var/lib/pysilhouette

    #### Copy several programs, configuration files and SysV init script ####
    # cp -f ~rpmbuild/pysilhouette/sample/rc.d/init.d/* /etc/rc.d/init.d/
    # cp -f ~rpmbuild/pysilhouette/sample/sysconfig/silhouetted /etc/sysconfig/silhouetted
    # cp -f ~rpmbuild/pysilhouette/sample/log.conf.example /etc/pysilhouette/log.conf
    # cp -f ~rpmbuild/pysilhouette/sample/silhouette.conf.example /etc/pysilhouette/silhouette.conf
    # cp -f ~rpmbuild/pysilhouette/sample/whitelist.conf.example /etc/pysilhouette/whitelist.conf
    # ln -s `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`/pysilhouette/silhouette.py /usr/bin
    # cp -f ~rpmbuild/pysilhouette/tool/psil-cleandb /usr/sbin
    # cp -f ~rpmbuild/pysilhouette/tool/psil-set /usr/sbin
    # chmod 0744 /usr/sbin/psil-*

    #### Modify the following files if necessary. 
    ## vi /etc/rc.d/init.d/silhouetted
    ## vi /etc/sysconfig/silhouetted


## Installing karesansui ##

###Procedure for `CentOS 6`:

####1. Fetching karesansui source code from github repository.

    # su - rpmbuild
    $ git clone git://github.com/karesansui/karesansui.git # No need if already downloaded.

####2a. (Method 1) Building karesansui package and installing it.

    $ cd ~/karesansui
    $ python setup.py sdist
    $ rpmbuild -ta dist/karesansui-*.tar.gz
    # rpm -Uvh ~rpmbuild/pkgs/RPMS/noarch/karesansui-{,{bin,data,gadget,lib,plus}-}3.*.noarch.rpm

####2b. (Method 2) Installing karesansui with Python's distutils.

    $ cd ~/karesansui
    $ python setup.py build
    # python setup.py install --record=INSTALLED_FILES --install-scripts=/usr/share/karesansui/bin

    #### Create kss account ####
    # /usr/sbin/useradd -c "Karesansui Project" -s /bin/false -r kss
    # gpasswd -a qemu kss

    #### Create the application's system directories ####
    # mkdir /etc/karesansui/virt
    # mkdir /var/log/karesansui
    # mkdir -p /var/lib/karesansui/{tmp,cache}

    #### Change attributes of the application's directories/files ####
    # chgrp -R kss   /etc/karesansui
    # chmod g+rwx    /etc/karesansui/virt
    # chmod o-rwx    /etc/karesansui/virt
    # chmod -R g+rw  /etc/karesansui
    # chmod -R o-rwx /etc/karesansui
    # chgrp -R kss   /var/log/karesansui
    # chmod -R 0700  /var/log/karesansui
    # chgrp -R kss   /var/lib/karesansui
    # chmod -R 0770  /var/lib/karesansui
    # chgrp -R kss `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`/karesansui
    # find `python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`/karesansui -type d -exec chmod g+rwx \{\} \;
    # find /usr/share/karesansui/ -type d -exec chgrp -R kss \{\} \;
    # find /usr/share/karesansui/ -type d -exec chmod g+rwx \{\} \;

    #### Copy several programs, configuration files and SysV init script ####
    # cp -f  ~rpmbuild/karesansui/sample/application.conf.example /etc/karesansui/application.conf
    # cp -f  ~rpmbuild/karesansui/sample/log.conf.example /etc/karesansui/log.conf
    # cp -f  ~rpmbuild/karesansui/sample/service.xml.example /etc/karesansui/service.xml
    # cp -f  ~rpmbuild/karesansui/sample/logview.xml.example /etc/karesansui/logview.xml
    # cp -fr ~rpmbuild/karesansui/sample/template/ /etc/karesansui/template/
    # cp -f  ~rpmbuild/karesansui/sample/cron_cleantmp.example /etc/cron.d/karesansui_cleantmp
    # cp -f  ~rpmbuild/karesansui/sample/whitelist.conf.example /etc/pysilhouette/whitelist.conf


## Configuring pysilhouette ##

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

    # /sbin/chkconfig --add silhouetted
    # /sbin/chkconfig silhouetted on


## Configuring karesansui ##

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

With a script bundled with the source code, you can create a database for karesansui and insert information of the administrator into the database.

    # python ~rpmbuild/karesansui/tool/initialize_database.py -m <Administrator's E-mail Address> -p <Administrator's Password> -l en_US

If you use a SQLite database, you must change the attributes of the database file.

    # chgrp -R kss /var/lib/karesansui/karesansui.db
    # chmod -R g+w /var/lib/karesansui/karesansui.db
    # chmod -R o-rwx /var/lib/karesansui/karesansui.db


## Creating database for pysilhouette ##

You can create a database for pysilhouette by executing the following command:

    # python -c "import karesansui; from pysilhouette.prep import readconf; karesansui.sheconf = readconf('/etc/pysilhouette/silhouette.conf'); import karesansui.db._2pysilhouette; karesansui.db._2pysilhouette.get_metadata().create_all()"

If you use a SQLite database, you must change the attributes of the database file.

    # chgrp -R kss /var/lib/pysilhouette/
    # chmod -R g+rw /var/lib/pysilhouette/
    # chmod -R o-rwx /var/lib/pysilhouette/


## Configuring libvirt ##

####1. Edit libvirt configuration file

You may need to modify the following configuration files.

__/etc/libvirt/libvirtd.conf__

 * listen_tcp = 1
 * tcp_port = "16509"
 * unix_sock_group = "kss"
 * auth_tcp = "none"

__/etc/sysconfig/libvirtd__

 * LIBVIRTD_ARGS="--listen"

####2. Create directories for libvirt

    # mkdir /var/lib/libvirt/{disk,domains,snapshot}
    # chgrp -R kss  /var/lib/libvirt
    # chmod -R 0770 /var/lib/libvirt

    # chgrp -R kss /etc/libvirt
    # find /etc/libvirt -type d -exec chmod g+rwx \{\} \;

####3. Create a TLS certificates for libvirt 

First, set up a Certificate Authority (CA).

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
    cn = example
    tls_www_server
    encryption_key
    signing_key
    $ certtool --generate-certificate --load-privkey serverkey.pem   --load-ca-certificate cacert.pem --load-ca-privkey cakey.pem   --template server.info --outfile servercert.pem

Install the certificates.

    # mkdir -p /etc/pki/libvirt/private/
    # cp -i cacert.pem /etc/pki/CA/
    # cp -i servercert.pem /etc/pki/libvirt/
    # cp -i serverkey.pem /etc/pki/libvirt/private/

####4. Enable libvirtd service

Restart service and enable it for auto start at bootup.

    # /sbin/chkconfig libvirtd on
    # /etc/init.d/libvirtd restart

####5. Check for connectivity to libvirtd

Please make sure that virsh client can connect to the QEMU monitor with libvirt.

    # virsh -c qemu+tcp://localhost:16509/system list

####6. Create the default storage pool for libvirt

    # KARESANSUI_CONF=/etc/karesansui/application.conf python -c "from karesansui.prep import built_in; built_in()"
    # /usr/share/karesansui/bin/create_storage_pool.py --name=default --target_path=/var/lib/libvirt/domains --mode=0770 --owner=0 --group=`id -g kss` --type=dir
    # virsh pool-refresh default
    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*


## Checking for connectivity to Karesansui management console

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

If the console is displayed correctly, the installation will appear to complete successfully.


Using other HTTP server
=======================

## With Lighttpd ##

###Procedure for `CentOS 6`:

####1. Installing packages.

Install several packages from [EPEL(Extra Packages for Enterprise Linux)](http://fedoraproject.org/wiki/EPEL) repository.

    # wget ftp://ftp.iij.ad.jp/pub/linux/fedora/epel/6/x86_64/epel-release-6-5.noarch.rpm
    # rpm -Uvh epel-release-6-5.noarch.rpm 
    # yum install lighttpd lighttpd-fastcgi spawn-fcgi

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

    # cp ~rpmbuild/karesansui/sample/lighttpd/karesansui.conf /etc/lighttpd/conf.d/


####4. Setting up a simple SSL configuration with lighttpd

    # mkdir -p /etc/lighttpd/ssl
    # openssl req -new -x509 -keyout /etc/lighttpd/ssl/server.pem -out /etc/lighttpd/ssl/server.pem -days 3650 -nodes
    # chmod 400 /etc/lighttpd/ssl/server.pem

####5. Start web service

If you have already tried to run Karesansui with other web server, you need to remove existing files with the following command:

    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*log

Restart service and enable it for auto start at bootup.

    # /sbin/chkconfig lighttpd on
    # /etc/init.d/lighttpd restart

If SELinux is set to "Enforcing", lighttpd may not work properly. Set it to "Permissive" mode and try to restart the service again.

    # /usr/sbin/setenforce 0
    # /etc/init.d/lighttpd restart

Moreover, if you need to use "Permissive" mode at the next reboot, you have to modify /etc/selinux/config file as well.

    SELINUX=permissive

####6. Checking for connectivity to Karesansui management console

Please access the following URL from your browser after starting the server. 
The username and password values for HTTP basic authentication must match the ones specified during database creation 'Creating database for karesansui'.

<pre>
https://[your-server-name]/karesansui/v3/
</pre>


## With Apache ##

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

    # cp ~rpmbuild/karesansui/sample/apache/fastcgi.conf /etc/httpd/conf.d/

####4. Start web service

If you have already tried to run Karesansui with other web server, you need to remove existing files with the following command:

    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*log

Restart service and enable it for auto start at bootup.

    # /sbin/chkconfig httpd on
    # /etc/init.d/httpd restart

    # chmod 777 /tmp/dynamic
    # chown apache:apache /tmp/dynamic
    # /etc/init.d/httpd restart

If SELinux is set to "Enforcing", apache may not work properly. Set it to "Permissive" mode and try to restart the service again.

    # /usr/sbin/setenforce 0
    # /etc/init.d/httpd restart

Moreover, if you need to use "Permissive" mode at the next reboot, you have to modify /etc/selinux/config file as well.

    SELINUX=permissive

####6. Checking for connectivity to Karesansui management console

Please access the following URL from your browser after starting the server. 
The username and password values for HTTP basic authentication must match the ones specified during database creation 'Creating database for karesansui'.

<pre>
https://[your-server-name]/karesansui/v3/
</pre>


## With Nginx ##

###Procedure for `CentOS 6`:

####1. Installing packages.

Install several packages from [EPEL(Extra Packages for Enterprise Linux)](http://fedoraproject.org/wiki/EPEL) repository.

    # wget ftp://ftp.iij.ad.jp/pub/linux/fedora/epel/6/x86_64/epel-release-6-5.noarch.rpm
    # rpm -Uvh epel-release-6-5.noarch.rpm 
    # yum install nginx spawn-fcgi

####2. Configuring group members.

Add _nginx_ user to _kss_ group and _kss_ user to _nginx_ group.

    # gpasswd -a nginx kss
    # gpasswd -a kss nginx

####3. Configuring nginx settings.

Copy the sample configuration file bundled with the source code to the location of nginx config directory, and edit it if necessary.

    # cp ~rpmbuild/karesansui/sample/nginx/karesansui.conf /etc/nginx/conf.d/

####4. Start web service

If you have already tried to run Karesansui with other web server, you need to remove existing files with the following command:

    # rm -fr /usr/share/karesansui/bin/__cmd__.py /var/log/karesansui/*log

First, run the karesansui program using the built-in server.

    # su -s /bin/bash kss -c "KARESANSUI_CONF=/etc/karesansui/application.conf SEARCH_PATH= /usr/share/karesansui/bin/karesansui.fcgi 127.0.0.1:8080"

Restart service and enable it for auto start at bootup.

    # /sbin/chkconfig nginx on
    # /etc/init.d/nginx restart

####6. Checking for connectivity to Karesansui management console

Please access the following URL from your browser after starting the server. 
The username and password values for HTTP basic authentication must match the ones specified during database creation 'Creating database for karesansui'.

<pre>
http://[your-server-name]/karesansui/v3/
</pre>


Feedback & Suggestions
======================
Is there something wrong, unclear or outdated in this documentation? Please get in touch so we can make it better. If you can contribute, we would greatly appreciate it!

