install
url --url ftp://ftp.riken.jp/Linux/centos/5/os/i386/
#url --url ftp://172.16.0.10/
lang ja_JP.UTF-8
keyboard jp106
xconfig --startxonboot
network --device eth0 --bootproto dhcp
#rootpw --iscrypted $1$hxgA34Vz$E/781by1lbNk1pz4Mh0Lc41
rootpw password
firewall --disabled
authconfig --enableshadow --enablemd5
selinux --disabled
timezone Asia/Tokyo
bootloader --location=mbr --driveorder=xvda --append="console=xvc0"
# The following is the partition information you requested
# Note that any partitions you deleted are not expressed
# here so unless you clear all partitions first, this is
# not guaranteed to work
zerombr yes
clearpart --linux --drives=xvda
part /boot --fstype ext3 --size=100 --ondisk=xvda
part pv.2 --size=0 --grow --ondisk=xvda
volgroup VolGroup00 --pesize=32768 pv.2
logvol swap --fstype swap --name=LogVol01 --vgname=VolGroup00 --size=272 --grow --maxsize=544
logvol / --fstype ext3 --name=LogVol00 --vgname=VolGroup00 --size=2048 --grow
reboot

%packages
@base
@core
@dns-server
@editors
@ftp-server
@japanese-support
@legacy-network-server
@mail-server
@mysql
@smb-server
@system-tools
@web-server

%post

