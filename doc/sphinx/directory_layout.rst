Directory Layout
================

Overview
--------

Here is overview of how Karesansui files and directories are structured.
This document is based on the CentOS 6.x (x86_64) directory structure.


Directory Structure
-------------------

/var/lib/libvirt
^^^^^^^^^^^^^^^^
Directory where libvirt stores its data.

The /var/lib/libvirt directory typically looks like this: 

.. code-block:: bash

    drwxrwx---. 2 root kss 4096 Dec  8 10:31 lxc
    drwxrwx---. 2 root kss 4096 Dec  8 10:31 boot
    drwxrwx---. 2 root kss 4096 Apr 12 17:46 dnsmasq
    drwxrwx---. 2 root kss 4096 Apr 12 17:46 network
    drwxrwx---. 3 root kss 4096 Apr 20 12:26 domains
    drwxrwx---. 5 qemu kss 4096 Apr 23 16:49 qemu

* lxc/

 Linux Containers (lxc) data. Karesansui does not use it.

* boot/

 Temporary kernel image or ramdisk image used at guest installation.

* dnsmasq/

 Configurations of NAT networking. libvirtd invokes dnsmasq and tells it to store state under this directory.

* network/

 Configurations of virtual network.

* domains/

 Virtual machine (VM) disk images. See `/var/lib/libvirt/domains <#id1>`_ for details.

* qemu/

 QEMU data. See `/var/lib/libvirt/qemu <#id2>`_ for details.


/var/lib/libvirt/domains
^^^^^^^^^^^^^^^^^^^^^^^^
Directory where the virtual machine (VM) disk images are stored in.

The /var/lib/libvirt/domains directory typically looks like this: 

.. code-block:: bash

    lrwxrwxrwx. 1 root root   43 Apr 19 18:20 a1590d77-64b6-ca53-49d9-b6f55fa56574 -> /var/lib/libvirt/domains/deb/images/deb.img
    lrwxrwxrwx. 1 root root   74 Apr 20 12:26 c7edf09b-e51d-8014-182f-09677db3c23a -> /var/lib/libvirt/domains/deb/disk/c7edf09b-e51d-8014-182f-09677db3c23a.img
    drwxrwx---. 5 root kss  4096 Apr 19 18:20 deb

* UUID-based file name (linked to /var/lib/libvirt/domains/<guest_name>/images/<guest_name>.img)

 Image file for the virtual machine (VM).

* UUID-based file name (linked to /var/lib/libvirt/domains/<guest_name>/disk/<uuid>.img)

 Image file for the virtual machine's additional disk.

* Directory named after the guest name

 A set of the virtual machine (VM) disk images. The list of its subdirectories and their descriptions is as follows: 

 * disk/

  Image file for the virtual machine's additional disk.

 * images/

  Image file for the virtual machine (VM).


/var/lib/libvirt/qemu
^^^^^^^^^^^^^^^^^^^^^
Directory where data and state for QEMU are stored in.

The /var/lib/libvirt/qemu directory typically looks like this: 

.. code-block:: bash

    srwxr-xr-x. 1 qemu qemu    0 Apr 23 16:49 deb.monitor
    drwxrwx---. 2 root kss  4096 Apr 12 17:46 dump
    drwxrwx---. 2 qemu kss  4096 Apr 12 17:46 save
    drwxrwx---. 3 qemu kss  4096 Apr 23 12:21 snapshot

* <guest_name>.monitor

 Socket file for QEMU monitor.

* dump/

 Directory where libvirtd will save dump files.

* save/

 Directory where libvirtd will dump the virtual machine (VM) into when the host is shutdowned.

* snapshot/

 Virtual machine (VM) snapshot information files.

 /var/lib/libvirt/qemu/snapshot/<guest_name>/<snapshor_tag>.xml


/etc/libvirt
^^^^^^^^^^^^
Directory where libvirt configuration files is located.

The /etc/libvirt directory typically looks like this: 

.. code-block:: bash

    -rw-r--r--. 1 root kss  11596 Apr 19 11:17 libvirtd.conf
    -rw-r--r--. 1 root kss  11305 Dec  8 10:31 qemu.conf
    drwxrwx---. 2 root kss   4096 Apr 12 17:39 nwfilter
    drwxrwx---. 4 root kss   4096 Apr 23 16:48 qemu
    drwxr-xr-x. 3 root root  4096 Apr 13 13:26 storage

* libvirtd.conf

 The libvirt daemon master configuration file.

* qemu.conf

 The QEMU driver configuration file.

* nwfilter/

 Configurations of firewall and network filtering.

* qemu/

 Configurations of KVM virtual machine and virtual network.

 * XML definition for KVM virtual machine
     /etc/libvirt/qemu/<guest_name>.xml

 * XML definition for QEMU virtual network
     /etc/libvirt/qemu/networks/<network_name>.xml

* storage/

 Configurations of the storage pool.


/etc/karesansui
^^^^^^^^^^^^^^^
Directory where karesansui configuration files is located.

The /etc/karesansui directory typically looks like this: 

.. code-block:: bash

    -rwxrwx---. 1 root kss  912 Apr 16 10:50 application.conf
    -rw-rw-r--. 1 root kss 2352 Apr 19 17:49 firewall.xml
    -rwxrwx---. 1 root kss 1814 Apr 18 18:10 log.conf
    -rwxrwx---. 1 root kss 3395 Apr 16 16:21 logview.xml
    -rwxrwx---. 1 root kss 1205 Apr 16 13:11 service.xml
    drwxrwx---. 3 root kss 4096 Apr 18 18:10 virt

* application.conf

 The karesansui main configuration file.

* firewall.xml

 XML definition for iptables


