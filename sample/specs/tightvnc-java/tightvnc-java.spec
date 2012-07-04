%{!?signer:%define signer 0}

Summary:        A remote display system.
Name:           tightvnc-java
Version:        1.3.10
Release:        1%{?dist}
URL:            http://www.tightvnc.com/
Source0:        http://downloads.sourceforge.net/sourceforge/vnc-tight/tightvnc-%{version}_javabin.tar.gz
Source1:        http://downloads.sourceforge.net/sourceforge/vnc-tight/tightvnc-%{version}_javasrc.tar.gz
License:        GPL
Group:          User Interface/Desktops
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
%if %{signer}
BuildRequires:  jdk >= 1.5.0
%endif

%description
Virtual Network Computing (VNC) is a remote display system which
allows you to view a computing 'desktop' environment not only on the
machine where it is running, but from anywhere on the Internet and
from a wide variety of machine architectures. TightVNC is an enhanced
VNC distribution. This package contains a client which will allow you
to connect to other desktops running a VNC or a TightVNC server.

%prep
echo RPM_BUILD_ROOT=$RPM_BUILD_ROOT
%setup -q -c %{name}-%{version} 

%if %{signer}
cat << _EOT_>jarsigner.sh
#!/bin/sh

__jarsigner=/usr/lib/jvm/java-gcj/bin/jarsigner
__keytool=/usr/lib/jvm/java-gcj/bin/keytool  
__jarsigner=/usr/bin/gjarsigner
__keytool=/usr/bin/gkeytool
__jarsigner=`ls -1 /usr/java/jdk1.*/bin/jarsigner 2>/dev/null | head -1`
__keytool=`ls -1 /usr/java/jdk1*/bin/keytool 2>/dev/null | head -1`

if [ "x\$1" = "x" -o ! -f "\$1" ]; then
  echo "ERROR: jarfile '\$1' not found." >&2
  exit 1
fi
keystore=.keystore.dat
jarfile=\$1

/bin/rm -f \${keystore}
\${__keytool} -genkey -alias vncviewer -validity 3650 -keystore \${keystore} || exit 1
\${__jarsigner} -keystore \${keystore} \${jarfile} vncviewer || exit 1
/bin/rm -f \${keystore}

_EOT_

sh ./jarsigner.sh classes/VncViewer.jar
%endif

%build

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/usr/lib/tightvnc
mkdir -p $RPM_BUILD_ROOT/opt/oc4j/j2ee/home/applications/OVS/webapp1/Class

cp -aR classes $RPM_BUILD_ROOT/usr/lib/tightvnc
cp -a classes/VncViewer.jar $RPM_BUILD_ROOT/opt/oc4j/j2ee/home/applications/OVS/webapp1/Class 
cp -a $RPM_SOURCE_DIR/tightvnc-%{version}_javasrc.tar.gz $RPM_BUILD_ROOT/usr/lib/tightvnc

%clean
rm -rf $RPM_BUILD_ROOT 

%pre
rm -f /opt/oc4j/j2ee/home/applications/OVS/webapp1/Class/VncViewer.jar

%post
if [ "$1" = "2" ]; then
  (sleep 1;cp -p /usr/lib/tightvnc/classes/VncViewer.jar /opt/oc4j/j2ee/home/applications/OVS/webapp1/Class/VncViewer.jar) &
fi

%files
%defattr(-,root,root)
%doc LICENCE.TXT README WhatsNew ChangeLog index.html
/usr/lib/tightvnc/*
/opt/oc4j/j2ee/home/applications/OVS/webapp1/Class/*

%changelog
* Tue Mar 13 2012 Taizo ITO <taizo@karesansui-project.info> - 1.3.10-2
- rebuild on el6.

* Mon May 11 2009 Taizo ITO <taizo@karesansui-project.info> - 1.3.10-1
- Update version 1.3.10

* Tue Jan 27 2009 Taizo ITO <taizo@karesansui-project.info>
- initial package
