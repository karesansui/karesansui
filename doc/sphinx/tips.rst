Tips
====

Graphical Desktop Sharing System
--------------------------------

How to connect to SPICE service with SPICE client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Installing SPICE client.

.. code-block:: bash

    # yum install spice-client

2. Connecting with SPICE client.

.. code-block:: bash

    $ spicec -h <host> -p <port_number> -w <password>


How to connect to VNC service with VNC client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Installing VNC client.

.. code-block:: bash

    # yum install vnc

2. Connecting with VNC client.

.. code-block:: bash

    $ vncviewer <host>:<port_number>

Or

.. code-block:: bash

    $ java -jar /opt/oc4j/j2ee/home/applications/OVS/webapp1/Class/VncViewer.jar HOST <host> PORT <port_number>


Network
-------

Device eth1 is present rather than eth0 after copying a KVM guest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you cloned a KVM guest, you may find the lack of an eth0 device.
That occurs due to a new twist of CentOS 6/Red Hat Enterprise Linux 6 – dynamic device management.


1. Log in the KVM guest and modify udev configuration file.

.. code-block:: bash

    # vi /etc/udev/rules.d/70-persistent-net.rules

    #SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="52:54:00:01:a8:a0", ATTR{type}=="1", KERNEL=="eth*", NAME="eth0"     # <- comment out

    SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="00:16:36:1e:e8:00", ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="eth*", NAME="eth0" # <- change to 'eth0'

2. Restart the KVM guest.


CD/DVD-ROM Drive
----------------

How to attach CD/DVD-ROM device to guests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can attach CD/DVD-ROM device by executing the following Karesansui's job command.

* Using physical CD/DVD-ROM on host.

.. code-block:: bash

    # /usr/share/karesansui/bin/append_disk.py -n <guest_name> -d /dev/sr0 -t vdc -b virtio -D block -N qemu -T raw -W cdrom

Or

.. code-block:: bash

    # /usr/share/karesansui/bin/append_disk.py -n <guest_name> -d /dev/sr0 -t hdc -b ide -D block -N qemu -T raw -W cdrom

.. note::

   You need to manually mount the cdrom before restarting the guest.

* Using ISO9660 image file on host.

.. code-block:: bash

    # /usr/share/karesansui/bin/append_disk.py -n <guest_name> -d /path/to/iso_file -t vdc -b virtio -D file -N qemu -T raw -W cdrom

Or

.. code-block:: bash

    # /usr/share/karesansui/bin/append_disk.py -n <guest_name> -d /path/to/iso_file -t hdc -b ide -D file -N qemu -T raw -W cdrom

Then, restart the guest.


Miscellious
-----------

How to work with CentOS 5 or Red Hat Enterprize Linux 5
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The installed packages should be more up to date, particularly packages such as dbus, libgcrypt and audit.

.. code-block:: bash

    # yum update dbus libgcrypt audit

Otherwise, errors occur as below:

.. code-block:: bash

    libvirtd: symbol lookup error: libvirtd: undefined symbol: dbus_watch_get_unix_fd

Or

.. code-block:: bash

    ImportError: '/usr/lib/libgnutls.so.13: symbol gcry_cipher_setkey, version GCRYPT_1.2 not defined in file libgcrypt.so.11 with link time reference'

Or

.. code-block:: bash

    ImportError: '/usr/lib/libvirt.so.0: undefined symbol: audit_encode_nv_string'

Using the Xen hypervisor
^^^^^^^^^^^^^^^^^^^^^^^^

Setting up a network bridge (for CentOS 5)
::::::::::::::::::::::::::::::::::::::::::


.. note::

    If you are accessing the server via SSH or Telnet instead of console, you MAY be disconnected when you restart the network service after modifying network settings. You should configure the settings via the local console. 

1. Edit xend configuration file

You may need to modify xend configuration file.

Replace network-bridge to network-dummy in /etc/xen/xend-config.sxp.

.. code-block:: bash

   (network-script network-dummy)

2. Create the network script defining a Linux bridge associated with the network card.

The script file path is /etc/sysconfig/network-scripts/ifcfg-xenbr0, where xenbr0 is the name of the bridge.

.. code-block:: bash

    # cp /etc/sysconfig/network-scripts/ifcfg-{eth0,xenbr0}

3. Edit the script file for xenbr0 (/etc/sysconfig/network-scripts/ifcfg-xenbr0)

If your network card is configured with a static IP address, your original network script file should look similar to the following example:

.. code-block:: bash

    DEVICE=eth0
    HWADDR=<the ethernet hardware address for this device>
    ONBOOT=yes
    IPADDR=<the IP address>
    BOOTPROTO=static
    NETMASK=<the netmask>
    TYPE=Ethernet

You need to edit ifcfg-xenbr0 as shown in the following example.

.. code-block:: bash

    DEVICE=xenbr0             # <- Changed
    #HWADDR=<the ethernet hardware address for this device>  # <- Commented out
    ONBOOT=yes
    IPADDR=<the IP address>
    BOOTPROTO=static
    NETMASK=<the netmask>
    TYPE=Bridge               # <- Changed

4. Edit the script file for eth0 (/etc/sysconfig/network-scripts/ifcfg-eth0)

Now you need to configure your network script for eth0. You will already have a script for eth0, but you’ll need to modify it by adding one line as BRIDGE=xenbr0 so that it looks similar to the following script.

.. code-block:: bash

    DEVICE=eth0
    HWADDR=<the ethernet hardware address for this device>
    ONBOOT=yes
    #IPADDR=<the IP address>  # <- Commented out
    #BOOTPROTO=none           # <- Commented out
    #NETMASK=<the netmask>    # <- Commented out
    TYPE=Ethernet
    BRIDGE=xenbr0             # <- Added

5. Restart network services and xend/libvirtd daemon.

In order for all the network script modifications to take effect, you need to restart your network services.

.. code-block:: bash

    # /etc/init.d/network restart
    # /etc/init.d/xend stop
    # /etc/init.d/libvirtd restart
    # /etc/init.d/xend start

6. Check the status of current interfaces

.. code-block:: bash

    # /sbin/ifconfig -a
    # virsh -c xen:/// list


How to associate Karesansui with libvirt's Xen driver (for CentOS 5)
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

1. Edit xend configuration file

You may need to modify xend configuration file.

Set xend-http-server parameter to yes in /etc/xen/xend-config.sxp.

.. code-block:: bash

   (xend-http-server yes)

2. Change permissions of Xen system files after every reboot to allow Karesansui to access Xen.

Here is a sample scriptlet.

.. code-block:: bash

    PRIVSEP_GROUP=kss

    # delegate admin privillege to PRIVSEP_GROUP
    if [ "x${PRIVSEP_GROUP}" != "x" -a -d /etc/xen/ ]; then
      chgrp ${PRIVSEP_GROUP} /etc/xen/
      chmod g+rwx /etc/xen/
    fi
    if [ "x${PRIVSEP_GROUP}" != "x" -a -d /var/lib/xend/ ]; then
      chgrp -R ${PRIVSEP_GROUP} /var/lib/xend/
      chmod -R g+rwx /var/lib/xend/
    fi
    if [ "x${PRIVSEP_GROUP}" != "x" -a  -d /var/run/xenstored/ ]; then
      chgrp -R ${PRIVSEP_GROUP} /var/run/xenstored/
      chmod -R g+rw /var/run/xenstored/
    fi
    if [ "x${PRIVSEP_GROUP}" != "x" -a  -e /proc/xen/privcmd ]; then
      chgrp ${PRIVSEP_GROUP} /proc/xen/privcmd
      chmod g+rw /proc/xen/privcmd
    fi
    find /etc/libvirt -type d  -exec chmod g+rwx \{\} \;
    find /etc/libvirt -type d  -exec chgrp kss \{\} \;

3. Edit libvirtd configuration file (/etc/libvirt/libvirtd.conf)

.. code-block:: bash

    unix_sock_group = "kss"
    unix_sock_ro_perms = "0777"
    unix_sock_rw_perms = "0770"

In order for modifications to take effect, you need to restart libvirtd.

.. code-block:: bash

    # /etc/init.d/libvirtd restart


More information are coming soon...
