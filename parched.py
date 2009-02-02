# Copyright (c) 2009 Sebastian Nowicki
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
.. moduleauthor:: Sebastian Nowicki <sebnow@gmail.com>

This module defines two classes which provide information about Pacman
packages and PKGBUILDs, :class:`PacmanPackage` and :class:`PKGBUILD`. These
classes iniherit from the :class:`Package` class, which provides the basic
metadata about package.
"""

import tarfile
from datetime import datetime

__all__ = ['Package', 'PacmanPackage', 'PKGBUILD']

class Package(object):
    """An abstract package class
    This class provides no functionality whatsoever. Use either
    :class:`PacmanPackage`, :class:`PKGBUILD`, or another subclass instead.
    
    The class provides attributes common to all packages. All attributes are
    supposed to be read-only.
    
    .. attribute:: name

        The name of the package.

    .. attribute:: version

        The version of the package, as a string.

    .. attribute:: release

        Release version of the package, i.e., version of the package itself.

    .. attribute:: description

        Description of the package.

    .. attribute:: url

        Package's website.

    .. attribute:: licenses

        A list of licenses.

    .. attribute:: groups

        A list of groups the package belongs to.

    .. attribute:: provides

        A list of "virtual provisions" that the package provides.

    .. attribute:: depends

        A list of the names of packages the package depends on.

    .. attribute:: optdepends

        A list of optional dependencies which are not required during runtime.

    .. attribute:: conflicts

        A list of packages the package conflicts with.

    .. attribute:: replaces

        A list of packages this package replaces.

    .. attribute:: architectures

        A list of architectures the package can be installed on.

    For more information about these attributes see :manpage:`PKGBUILD(5)`.

    """
    name = None
    version = None
    release = None
    description = None
    url = None
    licenses = []
    groups = []
    provides = []
    depends = []
    optdepends = []
    conflicts = []
    replaces = []
    architectures = []

    def __init__(self, pkgfile):
        raise NotImplementedError


class PacmanPackage(Package):
    """

    The :class:`PacmanPackage` class provides information about a package, by
    parsing a tarball in `pacman <http://www.archlinux.org/pacman>`_ package
    format. This tarball must have a `.PKGINFO` member. This member provides
    all metadata about the package.

    To instantiate a :class:`PacmanPackage` object, pass the package's file
    path in the constructor::

        >>> import parched
        >>> package = PacmanPackage("foo-1.0-1-any.tar.gz")

    If *tarfileobj* is specified, it is used as an alternative to a
    :class:`TarFile` like object opened for *name*. It is supposed to be
    at position 0. *tarfileobj* may be any object that has an
    :meth:`extractfile` method, which returns a file like object::

        >>> import tarfile
        >>> f = tarfile.open("foo-1.0-1-any.tar.gz", "r|gz")
        >>> package = PacmanPackage(tarfileobj=f)
        >>> f.close()

    .. note::

        *tarfileobj* is not closed.

    The packages metadata can then be accessed directly::
    
        >>> print package
        "foo 1.0-1"
        >>> print package.description
        "Example package"
    
    In addition to the attributes provided by :class:`Package`,
    :class:`PacmanPackage` provides the following attributes:
    
    .. attribute:: builddate

        A :class:`datetime` object indicating time at which the package was
        built.

    .. attribute:: packager

        The person who made the package, represented as a string in the format::
        
            First_name Last_name <email@domain.com>

    .. attribute:: is_force

        Indicates whether an upgrade is forced

    .. attribute:: backup

        A list of files which should be backed up on upgrades

    .. attribute:: makepkgopts

        Options used when building the package, represented as a list. This
        list is equivalent to that of `options` in a PKGBUILD. See
        :manpage:`PKGBUILD(5)` for more information.

    """
    builddate = None
    packager = None
    is_forced = False
    backup = []
    makepkgopts = []

    def __init__(self, name=None, tarfileobj=None):
        if not name and not tarfileobj:
            raise ValueError("nothing to open")
        should_close = False
        if not tarfileobj:
            tarfileobj = tarfile.open(str(name), "r|*")
            should_close = True
        pkginfo = tarfileobj.extractfile(".PKGINFO")
        self._parse(pkginfo)
        if should_close:
            tarfileobj.close()

    def __unicode__(self):
        print u'%s %s-%s' % (self.name, self.version, self.release)

    def _parse(self, pkginfo):
        """Parse the .PKGINFO file"""
        def handle_pkgver(v):
            self.version, _, self.release = v.rpartition('-')
        handlers = {
            'pkgname': lambda v: setattr(self, 'name', v),
            'pkgver': handle_pkgver,
            'pkgdesc': lambda v: setattr(self, 'description', v),
            'url': lambda v: setattr(self, 'url', v),
            'builddate': lambda v: setattr(self, 'builddate', datetime.utcfromtimestamp(int(v))),
            'packager': lambda v: setattr(self, 'packager', v),
            'size': lambda v: setattr(self, 'size', v),
            'arch': lambda v: self.architectures.append(v),
            'license': lambda v: self.licenses.append(v),
            'force': lambda v: setattr(self, 'is_forced', True),
            'replaces': lambda v: self.replaces.append(v),
            'group': lambda v: self.groups.append(v),
            'depend': lambda v: self.depends.append(v),
            'optdepend': lambda v: self.optdepends.append(v),
            'conflict': lambda v: self.conflicts.append(v),
            'provides': lambda v: self.provides.append(v),
            'backup': lambda v: self.backup.append(v),
            'makepkgopt': lambda v: self.makepkgopts.append(v),
        }
        for line in pkginfo:
            if line[0] == '#':
                continue
            var, _, value = line.strip().rpartition(' = ')
            if var not in handlers.keys():
                raise Exception('Uknown attribute "%s"' % var)
            # Is there a nicer way to do this?
            handlers[var](value)
        if self.packager == 'Uknown Packager':
            self.packager = None


class PKGBUILD(Package):
    build = None
    maintainer = None
    pass

