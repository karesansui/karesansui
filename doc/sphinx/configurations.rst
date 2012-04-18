==============
Configurations
==============

Overview
========

This section describes configuration parameters for Karesansui and other services related to Karesansui.

Configuring Karesansui
======================

Here are the files used to configure Karesansui.

Main Configuration Files - /etc/karesansui/application.conf
-----------------------------------------------------------

application.search.path
^^^^^^^^^^^^^^^^^^^^^^^
Search path for Python modules.

Multiple values are comma-separated.

ex.

.. code-block:: bash

   application.search.path=/usr/lib/python,/usr/lib/python2.6,/usr/lib/python2.6/site-packages


application.log.config
^^^^^^^^^^^^^^^^^^^^^^
Log file path.

ex.

.. code-block:: bash

    application.log.config=/etc/karesansui/log.conf

application.url.prefix
^^^^^^^^^^^^^^^^^^^^^^
Prefix of the URL for Karesansui management console.

ex.

.. code-block:: bash

    application.url.prefix=/karesansui/v3

application.default.locale
^^^^^^^^^^^^^^^^^^^^^^^^^^
Default locale.

.. note::
    As of this writing, only ja_JP or en_US can be specified.

ex.

.. code-block:: bash

    application.default.locale=ja_JP

application.template.theme
^^^^^^^^^^^^^^^^^^^^^^^^^^
Default theme for Karesansui management console.

ex.

.. code-block:: bash

    application.template.theme=default

application.tmp.dir
^^^^^^^^^^^^^^^^^^^
Directory where Karesansui should store its cache and temporary files. 

ex.

.. code-block:: bash

    application.tmp.dir=/tmp

application.bin.dir
^^^^^^^^^^^^^^^^^^^
Directory where job commands executed by Karesansui are located. 

The directory need to be writable for Karesansui owner.

ex.

.. code-block:: bash

    application.bin.dir=/usr/share/karesansui/bin

application.mail.email
^^^^^^^^^^^^^^^^^^^^^^
E-mail address of Karesansui Administrator.

ex.

.. code-block:: bash

    application.mail.email=karesansui@example.com

application.mail.port
^^^^^^^^^^^^^^^^^^^^^
Port number of an SMTP server which Karesansui connects.

ex.

.. code-block:: bash

    application.mail.port=25

application.mail.server
^^^^^^^^^^^^^^^^^^^^^^^
FQDN or IP address of an SMTP server which Karesansui connects.

ex.

.. code-block:: bash

    application.mail.server=localhost

application.proxy.status
^^^^^^^^^^^^^^^^^^^^^^^^
Either 1 or 0.
This tells Karesansui whether or not it need to connect the Internet via proxy.

ex.

.. code-block:: bash

    application.proxy.status=0

application.proxy.server
^^^^^^^^^^^^^^^^^^^^^^^^
FQDN or IP address of a proxy server which Karesansui uses.

ex.

.. code-block:: bash

    application.proxy.server=localhost

application.proxy.port
^^^^^^^^^^^^^^^^^^^^^^^^^^
Port number of a proxy server which Karesansui uses.

ex.

.. code-block:: bash

    application.proxy.port=9080

application.proxy.user
^^^^^^^^^^^^^^^^^^^^^^
Username for authentication on a proxy server which Karesansui uses.

ex.

.. code-block:: bash

    application.proxy.user=bar

application.proxy.password
^^^^^^^^^^^^^^^^^^^^^^^^^^
Password for authentication on a proxy server which Karesansui uses.

ex.

.. code-block:: bash

    application.proxy.password=foo

database.bind
^^^^^^^^^^^^^
The database URI that should be used for the connection.

.. note::

    This value must be specified in RFC-1738 style URL.
    See 'SQLAlchemy - Engine Configuration <http://docs.sqlalchemy.org/en/latest/core/engines.html>'_ for further information.

* MySQL

.. code-block:: none

    mysql://localhost/<database name>
    mysql://<user>:<password>@<hostname>/<database name>
    mysql://<user>:<password>@<hostname>:<port>/<database name>

* PostgreSQL

.. code-block:: none

    postgres://<user>:<password>@<hostname>:<port>/<database name>

* SQLite

The database must be writable for Karesansui owner.

.. code-block:: none

    sqlite:////path/to/database

ex.

.. code-block:: bash

    database.bind=sqlite:////var/opt/karesansui/karesansui.db

database.pool.status
^^^^^^^^^^^^^^^^^^^^
Either 1 or 0.
This tells Karesansui whether or not it uses connection pools.

ex.

.. code-block:: bash

    database.pool.status=0

database.pool.size
^^^^^^^^^^^^^^^^^^
The number of connection pools.

If you use SQLite database, this will be ignored.

ex.

.. code-block:: bash

    database.pool.size=1

database.pool.max.overflow
^^^^^^^^^^^^^^^^^^^^^^^^^^
The maximum number of connection pools.

ex.

.. code-block:: bash

    database.pool.max.overflow=10

pysilhouette.conf.path
^^^^^^^^^^^^^^^^^^^^^^
Pysilhouette configuration file.

The configuration file must be readable for Karesansui owner.

ex.

.. code-block:: bash

    pysilhouette.conf.path=/etc/pysilhouette/silhouette.conf

