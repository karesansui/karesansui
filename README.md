Karesansui
==========

Karesansui is an open-source virtualization management application made in Japan.

* Simple, easy web-based interface.
* Free for all. Distributed with the MIT license.
* Supports Kernel-based Virtual Machine(KVM) hypervisor. Other hypervisors/virtualization support on future plan.

Requirements
------------

Karesansui requires (or is dependent on) other software.

To install Karesansui, you will need:

* [Python](http://www.python.org/) 2.6 (2.4 might work?)
* [libvirt](http://libvirt.org/) 0.9.4 (or better)
* [RRDtool](http://oss.oetiker.ch/rrdtool/) 1.3 (or better)
* [Mako](http://www.makotemplates.org/) 0.3.2 (or better)
* [SQLAlchemy](http://www.sqlalchemy.org/) 0.5 (or better)
* [PyXML](http://sourceforge.net/projects/pyxml/) 0.8 (or better)
* [PySqlite](http://trac.edgewall.org/wiki/PySqlite) 2.3.5 (or better)
* [flup](http://trac.saddi.com/flup) 1.0.2 (or better)
* [collectd](http://collectd.org/) 4.10.3 (or better)
* [TightVNC Java Viewer](http://www.tightvnc.com/) 1.3.10 (or better)
* [web.py](http://webpy.org/) 0.35 (or better)

The [INSTALL](http://github.com/karesansui/karesansui/blob/master/INSTALL.md) document also describes a whole series of additional installation steps, including an easier way to install the required software listed above.

If you want to hack the source, you will also probably need:

* [Git](http://git-scm.com/)
* [setuptools](http://pypi.python.org/pypi/setuptools)

Installation
------------
See [INSTALL](http://github.com/karesansui/karesansui/blob/master/INSTALL.md).

License
-------
Karesansui is released under the MIT license to reduce problems for re-using. All source code has license notice, so you should clearly know what license to follow.

For exception, some Karesansui files don't have license notice for technical problems.
We can only mention about files we distribute, so consult the original author for such files.
Please see TRADEMARKS.TXT included with this distribution for information about Karesansui's trademark and logo usage policy.

This Karesansui source tree includes other open source projects work, which may come with its own distribution rule. Please consult each license notice for these projects.


### Javascript libraries under karesansui/static/js/lib ###

* [jquery](http://jquery.com/) - License MIT or GPL
* [jquery.form.js](http://malsup.com/jquery/form/) - License MIT or GPL
* [jquery-tablesort](http://tablesorter.com/docs/) - License  MIT or GPL
* [jquery-plugin-autocomplete](http://bassistance.de/jquery-plugins/jquery-plugin-autocomplete/) - License  MIT or GPL
* [jCarousel](http://sorgalla.com/jcarousel/) - License  MIT or GPL
* [ajax-upload](http://valums.com/ajax-upload/) - License  MIT

Acknowledgements
----------------
We want to thank so much the contributors of these projects: Python, libvirt, webpy, flup, psycopg2, tightvncviewer, jquery, jquery.form.js, jquery-tablesort, jquery-plugin-autocomplete, jCarousel, ajax-upload.

Contact Info
------------
http://karesansui-project.info

