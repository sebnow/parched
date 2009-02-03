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

import unittest
from mock import Mock
from datetime import datetime
import time
import parched

class FileMock(Mock):
    """A mock file object"""
    _lines = []
    name = None
    
    def __init__(self, content, name=None):
        self._lines = content
        self.name = name

    def readlines(self):
        return self._lines

    def __iter__(self):
        return self._lines.__iter__()


class TarFileMock(Mock):
    """A mock tarfile object"""
    _files = {}
    
    def add(self, fileobj):
        self._files[fileobj.name] = fileobj

    def extractfile(self, name):
        """Returns a :class:`FileMock` object"""
        return self._files[name]


class PackageGenerator(object):
    name = None
    version = None
    release = None
    description = None
    url = None
    groups = []
    licenses = []
    architectures = []
    replaces = []
    conflicts = []
    provides = []
    backup = []
    options = []

    def __init__(self):
        raise NotImplementedError


class PacmanPackageGenerator(PackageGenerator):
    builddate = datetime.utcnow()
    size = 0
    packager = None
    is_forced = False
    
    def __init__(self):
        pass
    
    def as_file(self, name=".PKGINFO"):
        content = []
        content.append("pkgname = %s" % self.name)
        content.append("pkgver = %s-%d" % (self.version, self.release))
        content.append("pkgdesc = %s" % self.description)
        content.append("url = %s" % self.url)
        lt = time.mktime(self.builddate.utctimetuple())
        utoffset = time.mktime(time.gmtime(lt)) - lt
        date = lt - utoffset
        content.append("builddate = %d" % date)
        content.append("packager = %s" % self.packager)
        content.append("size = %d" % self.size)
        content.append("force = %s" % (self.is_forced and "True" or "False"))
        for arch in self.architectures:
            content.append("arch = %s" % arch)
        for license in self.licenses:
            content.append("license = %s" % license)
        for replace in self.replaces:
            content.append("replaces = %s" % replace)
        for group in self.groups:
            content.append("group = %s" % group)
        for depend in self.depends:
            content.append("depend = %s" % depend)
        for optdepend in self.optdepends:
            content.append("optdepend = %s" % optdepend)
        for conflict in self.conflicts:
            content.append("conflict = %s" % conflict)
        for provide in self.provides:
            content.append("provides = %s" % provide)
        for path in self.backup:
            content.append("backup = %s" % path)
        for option in self.options:
            content.append("makepkgopt = %s" % option)
        return FileMock(content, name)


class PacmanPackageTest(unittest.TestCase):
    def setUp(self):
        self.package = PacmanPackageGenerator()
        self.package.name = "test"
        self.package.version = "1.0"
        self.package.release = 1
        self.package.description = "Test package"

    def test_sane_package(self):
        self.package.builddate = datetime.utcfromtimestamp(1231575886)
        self.package.packager = "John Doe"
        self.package.size = 8417280
        self.package.url = "http://www.test.com"
        self.package.architectures = ['i686', 'x86_64']
        self.package.licenses = ['MIT']
        self.package.replaces = ['foo', 'bar']
        self.package.groups = ['test', 'development']
        self.package.depends = ['baz', 'eggs']
        self.package.optdepends = ['ham']
        self.package.conflicts = ['gem']
        self.package.provides = ['lulz']
        self.backup = ['/etc/test/test.conf']
        self.options = ['!strip', '!info']

        tarfile = TarFileMock()
        tarfile.add(self.package.as_file())
        target = parched.PacmanPackage(tarfileobj=tarfile)

        self.assertEquals(self.package.name, target.name)
        self.assertEquals(self.package.version, target.version)
        self.assertEquals(self.package.release, target.release)
        self.assertEquals(self.package.description, target.description)
        self.assertEquals(self.package.url, target.url)
        self.assertEquals(self.package.builddate, target.builddate)
        self.assertEquals(self.package.size, target.size)
        self.assertEquals(self.package.packager, target.packager)
        self.assertEquals(self.package.is_forced, target.is_forced)
        self.assertEquals(self.package.groups, target.groups)
        self.assertEquals(self.package.licenses, target.licenses)
        self.assertEquals(self.package.architectures, target.architectures)
        self.assertEquals(self.package.replaces, target.replaces)
        self.assertEquals(self.package.conflicts, target.conflicts)
        self.assertEquals(self.package.provides, target.provides)
        self.assertEquals(self.package.backup, target.backup)
        self.assertEquals(self.package.options, target.options)


if __name__ == "__main__":
    unittest.main()
