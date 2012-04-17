# Tutorial

For those who want to:

* Create a guest OS
* Learn other basic operations

This tutorial will help you get started and install guest OS.

## Installing Guest OS

#### Preparing for Guest OS Installation

Here is an example of installing CentOS 6(x86_64) as guest.
We describe three ways to do that.

######CASE 1: Able to connect to the Internet. (Network Install)

Using kernel image and OS image on an external server, you can install guest OS.
You cannot retrieve the images via proxy server at installation, so you should use an external FTP server.
Be sure that the host is able to connect to the URL of CentOS 6's OS image.

Examples of URL

* http://[Web-site-name]/centos/6/os/x86_64/
* ftp://[FTP-site-name]/Linux/centos/6/os/x86_64/


######CASE 2: NOT able to connect to the Internet. (Local Install/ISO image)

With the KVM hypervisor, you can install from ISO-9660 CD-ROM image.
If you doesn't have an ISO-9660 CD-ROM image but DVD-ROM, it may be created by using _dd_ command.

    # dd if=/dev/cdrom of=/iso/centos6-x86_64.iso
    dd: reading `/dev/cdrom': Input/output error
    269860+0 records in
    269860+0 records out

######CASE 3: NOT able to connect to the Internet. (Local Install/CD-ROM)

Using CentOS 6(x86_64) DVD, you can intall guest OS.
You may need to install FTP server software such as vsftpd before setting up your own FTP server temporarily.
Please insert CentOS 6(x86_64) DVD to drive, and mount OS image on AnonymousFTP area.

    # rpm -q vsftpd 2>/dev/null || yum -y install vsftpd
    # /etc/init.d/vsftpd restart
    # mount /dev/cdrom /var/ftp/pub

Check to be sure that you can login to localhost as AnonymousFTP user.

    # ftp localhost
    Connected to localhost (127.0.0.1).
    220 (vsFTPd 2.2.2)
    Name (localhost:root): ftp
    331 Please specify the password.
    Password:
    230 Login successful.
    Remote system type is UNIX.
    Using binary mode to transfer files.
    ftp> quit

If you fail to login, SELinux may work.
Please set SELinux disabled temporarily by executing the following command.

    # /usr/sbin/setenforce 0


#### Installing Guest OS

First, please click the host icon image on top window of Karesansui web console.
And click the '_Create_' in '_Guests_' tab, then '_Create guest_' window will be displayed.

Here we describe the ways to specify values for each case mentioned previously.

######CASE 1: Able to connect to the Internet. (Network Install)

Fill out the items listed below.
 
<table class='item_table'>
 <tr>
  <th>Item name</th>
  <th>Description</th>
  <th>Example</th>
 </tr>
 <tr>
  <td nowrap>Kernel image</td>
  <td nowrap>the URL of Linux kernel image</td>
  <td nowrap>ftp://ftp.iij.ad.jp/pub/linux/centos/6/os/x86_64/isolinux/vmlinuz</td>
 </tr>
 <tr>
  <td nowrap>Initrd image</td>
  <td nowrap>the URL of Linux initrd image</td>
  <td nowrap>ftp://ftp.iij.ad.jp/pub/linux/centos/6/os/x86_64/isolinux/initrd.img</td>
 </tr>
</table>

As for other items, you can see the details clicking "?" displayed at the right of each item.

######CASE 2: NOT able to connect to the Internet. (Local Install/ISO image)

Fill out the items listed below.

<table class='item_table'>
 <tr>
  <th>Item name</th>
  <th>Description</th>
  <th>Example</th>
 </tr>
 <tr>
  <td nowrap>ISO image</td>
  <td nowrap>the absolute path of ISO image</td>
  <td nowrap>/iso/centos6-x86_64.img</td>
 </tr>
</table>

As for other items, you can see the details clicking "?" displayed at the right of each item.

######CASE 3: NOT able to connect to the Internet. (Local Install/CD-ROM)

Fill out the items listed below.

<table class='item_table'>
 <tr>
  <th>Item name</th>
  <th>Description</th>
  <th>Example</th>
 </tr>
 <tr>
  <td nowrap>Kernel image</td>
  <td nowrap>the absolute path of Linux kernel image</td>
  <td nowrap>/var/ftp/pub/isolinux/vmlinuz</td>
 </tr>
 <tr>
  <td nowrap>Initrd image</td>
  <td nowrap>the absolute path of Linux initrd image</td>
  <td nowrap>/var/ftp/pub/isolinux/initrd.img</td>
 </tr>
</table>

As for other items, you can see the details clicking "?" displayed at the right of each item.

-----
Fill up all items, please click the "_Create_" button at the bottom of "_Create guest_" window.
Then, the message that the creation job is accepted will be displayed.

So the icon image that stands for new guest will appear in "_Guests_" window.

Please click the new guest icon, and then click the "_Console_" tab.
The console window of guest will be displayed. In this window, you can install CentOS 6 into guest as into real machine.


######CASE 1: Able to connect to the Internet. (Network Install)

In the guest installation,

######1. Selecting an Installation Method

You need to select the "HTTP" or "FTP".

######2 - 1. Installing via HTTP

Fill out the items listed below.

<table class='item_table'>
 <tr>
  <th>Item name</th>
  <th>Description</th>
  <th>Example</th>
 </tr>
 <tr>
  <td nowrap>Web site name</td>
  <td nowrap>Web site name that provides OS image</td>
  <td nowrap>mirror.centos.org</td>
 </tr>
 <tr>
  <td nowrap>CentOS directory</td>
  <td nowrap>CentOS directory path on web site</td>
  <td nowrap>/centos/6/os/x86_64/</td>
 </tr>
</table>

######2 - 2. Installing via FTP

Fill out the items listed below.

<table class='item_table'>
 <tr>
  <th>Item name</th>
  <th>Description</th>
  <th>Example</th>
 </tr>
 <tr>
  <td nowrap>FTP site name</td>
  <td nowrap>FTP site name that provides OS image</td>
  <td nowrap>ftp.iij.ad.jp</td>
 </tr>
 <tr>
  <td nowrap>CentOS directory</td>
  <td nowrap>CentOS directory path on FTP site</td>
  <td nowrap>/pub/linux/centos/6/os/x86_64/</td>
 </tr>
</table>

######CASE 2: NOT able to connect to the Internet. (Local Install/ISO image)

You can install a guest OS in the same way as using the installation disc.

######CASE 3: NOT able to connect to the Internet. (Local Install/CD-ROM)

In the guest installation,

######1. Selecting an Installation Method

You need to select the "FTP".

######2. Installing via FTP

Fill out the items listed below.

<table class='item_table'>
 <tr>
  <th>Item name</th>
  <th>Description</th>
  <th>Example</th>
 </tr>
 <tr>
  <td nowrap>FTP site name</td>
  <td nowrap>FTP site name that provides OS image</td>
  <td nowrap>IP address of your host (NOT loopback address)</td>
 </tr>
 <tr>
  <td nowrap>CentOS directory</td>
  <td nowrap>CentOS directory path on FTP site</td>
  <td nowrap>/pub/</td>
 </tr>
</table>

## That's It!

This is the end of the tutorial. You can now do basic operation about virtualization.

## Hints

To allow a user to shut down a guest properly by Karesansui management console, ACPI event daemon must be installed and running in each guest.
Under CentOS, Red Hat Enterprise Linux or Fedora Linux, _acpid_ package should be installed, and the ACPI event daemon must start automatically at each system boot.

    # rpm -q acpid 2>/dev/null || yum -y install acpid
    # /sbin/service haldaemon stop
    # /sbin/service apcid restart
    # /sbin/chkconfig apcid on
    # /sbin/service haldaemon start


