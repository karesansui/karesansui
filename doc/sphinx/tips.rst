Tips
====

Graphical Desktop Sharing System
--------------------------------

How to connect to SPICE service with SPICE client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Installing SPICE client.

    # yum install spice-client

2. Connecting with SPICE client.

    $ spicec -h <host> -p <port_number> -w <password>


How to connect to VNC service with VNC client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Installing VNC client.

    # yum install vnc

2. Connecting with VNC client.

    $ vncviewer <host>:<port_number>
    or $ java -jar /opt/oc4j/j2ee/home/applications/OVS/webapp1/Class/VncViewer.jar HOST <host> PORT <port_number>


Network
-------

Device eth1 is present rather than eth0 after copying a KVM guest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you cloned a KVM guest, you may find the lack of an eth0 device.
That occurs due to a new twist of CentOS 6/Red Hat Enterprise Linux 6 – dynamic device management.


1. Log in the KVM guest and modify udev configuration file.

    # vi /etc/udev/rules.d/70-persistent-net.rules

    #SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="52:54:00:01:a8:a0", ATTR{type}=="1", KERNEL=="eth*", NAME="eth0"     # <- comment out

    SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", ATTR{address}=="00:16:36:1e:e8:00", ATTR{dev_id}=="0x0", ATTR{type}=="1", KERNEL=="eth*", NAME="eth0" # <- change to 'eth0'

2. Restart the KVM guest.


CD/DVD-ROM Drive
----------------

How to attach CD/DVD-ROM device to guests.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can attach CD/DVD-ROM device by executing the following Karesansui's job command.

* Using physical CD/DVD-ROM on host.

    # /usr/share/karesansui/bin/append_disk.py -n <guest_name> -d /dev/sr0 -t vdc -b virtio -D block -N qemu -T raw -W cdrom

    Or

    # /usr/share/karesansui/bin/append_disk.py -n <guest_name> -d /dev/sr0 -t hdc -b ide -D block -N qemu -T raw -W cdrom

.. note::
   You need to manually mount the cdrom before restarting the guest.

* Using ISO9660 image file on host.

    # /usr/share/karesansui/bin/append_disk.py -n <guest_name> -d /path/to/iso_file -t vdc -b virtio -D file -N qemu -T raw -W cdrom

    Or

    # /usr/share/karesansui/bin/append_disk.py -n <guest_name> -d /path/to/iso_file -t hdc -b ide -D file -N qemu -T raw -W cdrom

Then, restart the guest.




More information are coming soon...
