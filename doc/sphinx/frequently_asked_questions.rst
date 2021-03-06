Frequently Asked Questions
==========================

.. contents::

General
-------

Is it free?
^^^^^^^^^^^

Yes, it is. You may use Karesansui for business or personal use for free.

What kind of the license is Karesansui under?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Karesansui is mainly under MIT License. See `README <http://github.com/karesansui/karesansui/blob/master/README.md>`_ for details.

Does Karesansui support full-virtualization?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. Karesansui supports full-virtualization with KVM hypervisor.

I'm not used to Linux. Is the installation easy?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We have prepared detailed installation guide allowing you easily to install.
Please follow `INSTALL <http://github.com/karesansui/karesansui/blob/master/INSTALL.md>`_.

There are already many virtualization management consoles around there. What are the pros of Karesansui?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We are working hard. Please take a look at our Karesansui's full ajax web control panel.

I'd like to introduce Karesansui to others.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes! Thank you! Take the `Get Karesansui Badge <http://karesansui-project.info/karesansui_pages/badges>`_ if you like it.

I'd like to use Karesansui in our company's network. Is there any license problems?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

No. Nothing. It's MIT License so there's no problem.

Application
-----------

What happens when the database, which Karesansui refers, stops? Does the guest stop?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

No. Karesansui uses the database to keep information for its user interface. Guests don't stop if when the database stops, but you will have problems to access Karesansui control panel.

I'll get "You need Java installed" errors when I try to access the guest console.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We use `TightVNC <http://www.tightvnc.com/>`_ Java applet for guest console. So you need Java installed for your browser.

Guest console doesn't show up. What can I do?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, Check if you can access your host. From your client's console, type

.. code-block:: bash

    > ping {Karesansui server IP address or name}

Next, Check if the VNC port is open on your Karesansui host.

.. code-block:: bash

    # netstat -nalt

If all above are OK, then try to connect the guest from the client, using standard VNC viewer applications.

Guest console keymap is garbled.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Select 'Graphics' from guest device tab, and set 'Graphics Keymap'. Choose appropriate keymap.

I can't shutdown/stop guests.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Try the following instructions. First check if acpid is running. On the guest console, do as shown below.

.. code-block:: bash

    # ps auxww | grep acpid
    root        34  0.0  0.0      0     0 ?        S<   10:50   0:00 [kacpid]
    68        2420  0.0  0.0  12320   876 ?        S    10:51   0:00 hald-addon-acpi: listening on acpi kernel interface /proc/acpi/event
    root      4082  0.0  0.0  65372   868 pts/0    S+   12:15   0:00 grep acpid

If /usr/sbin/acpid is not installed, install it. If /usr/sbin/acpid is not running, start it.

.. code-block:: bash

    # rpm -q acpid 2>/dev/null || yum -y install acpid
    # /etc/init.d/acpid start
    # chkconfig acpid on

if acpid fails with error like "acpid: can't open /proc/acpi/event: Device or resource busy", try as following.

.. code-block:: bash

    # /etc/init.d/haldaemon stop
    # /etc/init.d/acpid start
    # /etc/init.d/haldaemon start
    # chkconfig acpid on

Check if acpid is running on guest again.

.. code-block:: bash

    # ps auxww | grep acpi
    root        34  0.0  0.0      0     0 ?        S<   10:50   0:00 [kacpid]
    root      4107  0.0  0.0   3800   576 ?        Ss   12:18   0:00 /usr/sbin/acpid
    68        4122  0.0  0.0  12320   880 ?        S    12:18   0:00 hald-addon-acpi: listening on acpid socket /var/run/acpid.socket

After acpid is started, try to shutdown/stop the guest.

It doesn't work.
^^^^^^^^^^^^^^^^

Go and ask your question in the `Karesansui Forum <http://karesansui-project.info/projects/karesansui/boards>`_ . Somebody may answer you.

Logging
-------

I want to change the log file rotation cycle, size, path, etc..
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change "args" in the "[handler_*" category of log.conf

ex: Set size of log file to 10M.

.. code-block:: bash

    args=('/var/log/karesansui/application.log', 'a', (10 * 1024 * 1024), 5)

ex: Rename log file to 'server.log'.

.. code-block:: bash

    args=('/var/log/karesansui/server.log', 'a', (5 * 1024 * 1024), 5)

ex: Change the number of rotated log files to 10.

.. code-block:: bash

    args=('/var/log/karesansui/application.log', 'a', (5 * 1024 * 1024), 10)

I found an error on the Karesansui control panel, but can't find corresponding message in the error log.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

May be the message is filtered by the log level. Check the level in "[logger_*" category of log.conf.

Log levels (From high to low. Higher level include lower level.)

 - DEBUG: Debug messages
 - INFO: Informational messages
 - WARNING: Warnings that don't cause an actual error (recommended)
 - ERROR: Non-fatal errors.
 - CRITICAL: Fatal errors that cause the process to die.
 - EXCEPTION: Errors that cause an exception.

After modifying log.conf, you need to restart the web server.

Can I change the log output style?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We use python logging. Check python logging instructions.

Where are the log files stored?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Where defined in "args" of  "[handler_*" category of log.conf.

I have several log files. What are these?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Karesansui writes log in several files.

 - General log of Karesansui: /var/log/karesansui/application.log
 - Program trace for errors: /var/log/karesansui/error.log
 - SQL committed by Karesansui: /var/log/karesansui/sql.log

Open Sources
------------

Does Karesansui support any other database system other than SQLite?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes. It supports MySQL, PostgreSQL, or any database that SQLAlchemy can work with.

You need to change 'database.bind' parameter in karesansui's configuration file(/etc/karesansui/application.conf).
Please see `Configurations - database.bind <configurations.html#database-bind>`_ for details.

After modifying the setting, please refer to the URL below and initialize database.

http://github.com/karesansui/karesansui/blob/master/INSTALL.md#creating_database_for_karesansui
