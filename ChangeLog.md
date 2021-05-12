## 4.0.0 (May 12, 2021

Changes:

  - Changes needed to support Python 3.6+
  - Changed to using SqlAlchemy 1.4
  - Switched XML library from PyXML to lxml

Known Issues:

  - All documentation is out of date and needs updated
  - Network storage support is currently broken
  - Adding guest virts is currently broken, create input validation fails when assigning an ISO image and the graphic keymap drop down is not loading
  - Some static assets are not loading properly

## 3.0.2 (Sep 12, 2012)

Bugfixes:

  - Added remote libvirt URI support.[#18]
  - Fixed a check to ensure that the netmask pattern is valid in check_ipaddr().[#20]
  - Ignore the image type of cdrom device when determining whether the domain supports for snapshot.
  - Added __cmd__.py as a static file.[#19]
  - Don't create a symbolic link to Karesansui's directory automatically.[#19]
  - Access from multiple threads can be enabled via optional argument check_same_thread. [#17]
  - Avoid AttributeError.[#18]
  - Fixed SADeprecationWarning - Use session.add().[#15]
  - Fixed ImportError: No module named ext in "from xml.dom.ext import PrettyPrint"[#12][#13]
  - Fixed No translation file found for domain: 'messages'[#14]
  - Changed attributes of network's qemu config xml file again after defining domain.
  - Fixed undefined local variable 'source_attribute' error.[#9][#10]
rest: If 'HTTP_AUTHORIZATION' environ variable not found, 'Authorization' is used instead of it.
  - Added the directory for java applet to %files tag of RPM spec.
  - Fixed some typos.


## 3.0.1 (Jun 22, 2012)

Features:

  - Add libvirt's connection URI management.
  - Add a gadget for initializing Karesansui database.

Bugfixes:

  - Use XMLDesc() with a flag VIR_DOMAIN_XML_INACTIVE instead of reading an existing XML file.

Documentation:

  - Add instructions to install on Debian GNU/Linux.
  - Add a description regarding mod_fcgid configurations.
  - Add ChangeLog.
  - Fix several typo.

