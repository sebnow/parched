Overview
========

Parched aims at providing a python module capable of parsing pacman packages
and PKGBUILDs.

Dependencies
============

* `Pyrex <http://www.cosc.canterbury.ac.nz/greg.ewing/python/Pyrex/>`_
* `pkgparse <http://www.github.com/sebnow/pkgparse/>`_


Installing
==========

Pip
---

Parched is not currently registered with `PyPI <http://pypi.python.org>`_ due to it's
development status, however pip can install the module from a git repository::

    pip install -e git://github.com/sebnow/parched.git

Manual
------

First retrieve the source from the `git repository
<http://github.com/sebnow/parched/>`_, then follow the typical install
procedure::

    git clone git://github.com/sebnow/parched.git
    cd parched
    python setup.py install


Documentation
=============

The documentation is not available online, however, you can retrieve the
source and generate the documentation using sphinx::

    git clone git://github.com/sebnow/parched.git
    cd parched/docs
    make html

The code itself is also documented, so you can simply look at parched.py.


License
=======

Parched is MIT licensed. Do whatever you want.
