=========
Easy Menu
=========

Super Simple Terminal Command Launcher Generator

.. image:: https://badge.fury.io/py/easy-menu.svg
   :target: http://badge.fury.io/py/easy-menu
   :alt: PyPI version

.. image:: https://travis-ci.org/mogproject/easy-menu.svg?branch=master
   :target: https://travis-ci.org/mogproject/easy-menu
   :alt: Build Status

.. image:: https://coveralls.io/repos/mogproject/easy-menu/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/mogproject/easy-menu?branch=master
   :alt: Coverage Status

.. image:: https://img.shields.io/badge/license-Apache%202.0-blue.svg
   :target: http://choosealicense.com/licenses/apache-2.0/
   :alt: License

.. image:: https://badge.waffle.io/mogproject/easy-menu.svg?label=ready&title=Ready
   :target: https://waffle.io/mogproject/easy-menu
   :alt: 'Stories in Ready'

--------
Features
--------

*Simplify your daily terminal operations!*

Do you have any routine tasks such as login to your servers, deploying, troubleshooting or something like that?

This small tool would help to speed up your operations and prevent human errors.
It should be helpful not only for salted engineers but unskilled operators.

.. image:: https://raw.githubusercontent.com/wiki/mogproject/easy-menu/img/demo.gif

------------
Dependencies
------------

* Python: 2.6 / 2.7 / 3.2 / 3.3 / 3.4
* pyyaml
* six

----------
Quickstart
----------

You can try Easy Menu by just two command lines.

::

    pip install easy-menu
    easy-menu http://git.io/vGWla

Note: ``http://git.io/vGWla`` will redirect to ``https://raw.githubusercontent.com/mogproject/easy-menu/master/easy-menu.example.yml``

------------
Installation
------------

* ``pip`` command may need ``sudo``

+-------------------------+---------------------------------------+
| Operation               | Command                               |
+=========================+=======================================+
| Install                 |``pip install easy-menu``              |
+-------------------------+---------------------------------------+
| Upgrade                 |``pip install --upgrade easy-menu``    |
+-------------------------+---------------------------------------+
| Uninstall               |``pip uninstall easy-menu``            |
+-------------------------+---------------------------------------+
| Check installed version |``easy-menu --version``                |
+-------------------------+---------------------------------------+
| Help                    |``easy-menu -h``                       |
+-------------------------+---------------------------------------+

* Then, write your configuration to the file ``easy-menu.yml``.

See an example below.

---------------------
Configuration Example
---------------------

``easy-menu.example.yml``::

    Main Menu:
      - Service health check: "echo Condition all green!"
      - Check hardware resources: "echo Hardware resources OK."
      - Server Login Menu:
        - Login to server-1: "echo logging into server-1"
        - Login to server-2: "echo logging into server-2"
        - Login to server-3: "echo logging into server-3"
      - Web Service Management Menu:
        - Check the status of web service: "echo Check web service status"
        - Start web service: "echo Start web service"
        - Stop web service: "echo Stop web service"
      - Reboot this server: "echo Reboot OS"

Each menu (i.e. root menu and sub menu) and each item is represented as *Mapping* which contains just one key-value pair.
In case its value is a *Sequence*, the sub menu will be generated.

The general syntax is like this.

::

    meta:                            # Some meta variables are available
      META_KEY: META_VALUE

    ROOT_MENU_TITLE:
      - ITEM_DESCRIPTION: COMMAND
      - ITEM_DESCRIPTION: COMMAND
      - SUB_MENU_TITLE:              # You can create sub menu if you need.
        - ITEM_DESCRIPTION: COMMAND
        - ITEM_DESCRIPTION: COMMAND
        - SUB_MENU_TITLE:            # More nested menu
          - ITEM_DESCRIPTION: COMMAND
          - ITEM_DESCRIPTION: COMMAND
      - include: INCLUDE_FILE_PATH   # "include" keyword enables to load
                                     #   another configuration file.
      - eval: COMMAND                # "eval" keyword will execute command line
                                     #   and use its output as configuration YAML string.

Remember these commands are executed after changing the current directory to the directory which holds the configuration file by default.

You can find more examples in `this directory <https://github.com/mogproject/easy-menu/tree/master/tests/resources>`_.

-----------
Lookup Path
-----------

Similar to `Vagrant <https://docs.vagrantup.com/v2/vagrantfile/>`_, when you run any ``easy-menu`` command, Easy Menu climbs up the directory tree looking for the first ``easy-menu.yml`` it can find, starting first in the current directory.
So if you run ``easy-menu`` in ``/home/mogproject/projects/foo``, it will search the following paths in order for a ``easy-menu.yml``, until it finds one:

::

    /home/mogproject/projects/foo/easy-menu.yml
    /home/mogproject/projects/easy-menu.yml
    /home/mogproject/easy-menu.yml
    /home/easy-menu.yml
    /easy-menu.yml

This feature lets you run ``easy-menu`` from any directory in your project.

You can change default name of the configuration file by setting the ``EASY_MENU_CONFIG`` environmental variable to some other name.

-------------
Audit Logging
-------------

Anytime you execute the command, the result (return code) will be recorded to the syslog facility in your operating system.
This feature is not available on Windows OS.

Example::

    Aug 31 00:09:59 ullr.local easy-menu[28802]: [INFO] Command started: echo Condition all green!
    Aug 31 00:09:59 ullr.local easy-menu[28802]: [INFO] Command ended with return code: 0

--------------
Meta Variables
--------------

You can overwrite options by writing ``meta`` variables in the root configuration file.

+-------------------------+---------------------------------------+
| Option                  | Description                           |
+=========================+=======================================+
| work_dir                | Path to the working directory         |
+-------------------------+---------------------------------------+


----

Looking for legacy version? Please refer to `v0.0 <https://github.com/mogproject/easy-menu/tree/v0.0>`_.
