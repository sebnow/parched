#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from __future__ import unicode_literals

import time
import unittest

from collections import OrderedDict
from datetime import datetime
from io import StringIO

import parched

try:
    unicode
except NameError:
    unicode = None


class FileMock(StringIO):
    def __init__(self, buffer=None, name=None, encoding='utf-8'):
        self._name = name
        self._encoding = encoding
        super(FileMock, self).__init__(buffer)

    @property
    def name(self):
        return self._name

    def read(self, *args):
        value = super(FileMock, self).read(*args)
        if unicode and isinstance(value, unicode):
            value = value.encode(self._encoding)
        return value


class TarFileMock(object):
    """A mock tarfile object"""
    def __init__(self, *args, **kwargs):
       self._files = OrderedDict()

    def add(self, fileobj):
        self._files[fileobj.name] = fileobj

    def extractfile(self, name):
        """Returns a :class:`FileMock` object"""
        return self._files[name]

    def getnames(self):
        """Return the members as a list of their names"""
        return [self._files[k].name for k in self._files]


class PackageGenerator(object):
    def __init__(self):
        super(PackageGenerator, self).__init__()
        self.name = None
        self.version = None
        self.release = None
        self.description = None
        self.url = None
        self.groups = []
        self.licenses = []
        self.architectures = []
        self.replaces = []
        self.conflicts = []
        self.provides = []
        self.backup = []
        self.options = []

    def as_file(self, name):
        raise NotImplementedError


class PacmanPackageGenerator(PackageGenerator):
    def __init__(self):
        super(PacmanPackageGenerator, self).__init__()
        self.builddate = datetime.utcnow()
        self.size = 0
        self.packager = None
        self.is_forced = False
    
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
        return FileMock("\n".join(content), name)

class PKGBUILDGenerator(PackageGenerator):
    def __init__(self):
        super(PKGBUILDGenerator, self).__init__()
        self.install = None
        self.makedepends = []
        self.sources = []
        self.checksums = {
            'md5': [],
            'sha1': [],
            'sha256': [],
            'sha384': [],
            'sha512': [],
        }
        self.noextract = []

    def as_file(self, name="PKGBUILD"):
        content = []
        content.append('pkgname=%s' % self.name)
        content.append('pkgver=%s' % self.version)
        content.append('pkgrel=%d' % self.release)
        content.append('pkgdesc="%s"' % self.description)
        content.append('arch=(%s)' % " ".join(self.architectures))
        content.append('url=%s' % self.url)
        content.append('license=(%s)' % " ".join(self.licenses))
        content.append('groups=(%s)' % " ".join(self.groups))
        content.append('depends=(%s)' % " ".join(self.depends))
        content.append('makedepends=(%s)' % " ".join(self.makedepends))
        content.append('optdepends=(%s)' % " ".join(self.optdepends))
        content.append('provides=(%s)' % " ".join(self.provides))
        content.append('conflicts=(%s)' % " ".join(self.conflicts))
        content.append('replaces=(%s)' % " ".join(self.replaces))
        backup = ""
        if len(self.backup) > 0:
            backup = " ".join(['"%s"' % x for x in self.backup])
        content.append('backup=(%s)' % backup)
        content.append('options=(%s)' % " ".join(self.options))
        content.append('install="%s"' % self.install)
        source = ""
        if len(self.sources) > 0:
            source = " ".join(['"%s"' % x for x in self.sources])
        content.append('source=(%s)' % source)
        content.append('noextract=(%s)' % " ".join(self.noextract))
        for k in self.checksums.keys():
            content.append('%ssums=(%s)' % (k, " ".join(self.checksums[k])))
        return FileMock("\n".join(content), name)


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
        self.package.backup = ['/etc/test/test.conf']
        self.package.options = ['!strip', '!info']

        tarfile = TarFileMock()
        tarfile.add(self.package.as_file())
        tarfile.add(FileMock("foo", "foo.txt"))
        target = parched.PacmanPackage(tarfileobj=tarfile)

        self.assertEqual(self.package.name, target.name)
        self.assertEqual(self.package.version, target.version)
        self.assertEqual(self.package.release, target.release)
        self.assertEqual(self.package.description, target.description)
        self.assertEqual(self.package.url, target.url)
        self.assertEqual(self.package.builddate, target.builddate)
        self.assertEqual(self.package.size, target.size)
        self.assertEqual(self.package.packager, target.packager)
        self.assertEqual(self.package.is_forced, target.is_forced)
        self.assertEqual(self.package.groups, target.groups)
        self.assertEqual(self.package.licenses, target.licenses)
        self.assertEqual(self.package.architectures, target.architectures)
        self.assertEqual(self.package.replaces, target.replaces)
        self.assertEqual(self.package.conflicts, target.conflicts)
        self.assertEqual(self.package.provides, target.provides)
        self.assertEqual(self.package.backup, target.backup)
        self.assertEqual(self.package.options, target.options)
        self.assertEqual(target.files, [".PKGINFO", "foo.txt"])

class PKGBUILDTest(unittest.TestCase):
    def setUp(self):
        self.package = PKGBUILDGenerator()
        self.package.name = "test"
        self.package.version = "1.0"
        self.package.release = 1
        self.package.description = "Test package"
        self.package.url = "http://www.test.com"
        self.package.architectures = ['i686', 'x86_64']
        self.package.licenses = ['MIT']
        self.package.replaces = ['foo', 'bar']
        self.package.groups = ['test', 'development']
        self.package.depends = ['baz', 'eggs']
        self.package.optdepends = ['ham']
        self.package.conflicts = ['gem']
        self.package.provides = ['lulz']
        self.package.makedepends = ['glibc']
        self.package.sources = [
            'http://www.test.org/files/%s-%s.tar.gz' % (self.package.name, self.package.version),
            'http://www.test.org/files/data.tar.gz',
        ]
        self.package.checksums['md5'] = [
            '6caefe06c7a0fc9a5e03497c7106cc56',
            '4c593db82677c01e7fbe9febf0b95475'
        ]
        self.package.backup = ['/etc/test/test.conf']
        self.package.options = ['!strip', '!info']
        self.package.noextract = ['data.tar.gz']
        self.package.install = 'test.install'

    def test_sane_package(self):
        target = parched.PKGBUILD(fileobj=self.package.as_file())
        self.assertEqual(self.package.name, target.name)
        self.assertEqual(self.package.version, target.version)
        self.assertEqual(self.package.release, target.release)
        self.assertEqual(self.package.description, target.description)
        self.assertEqual(self.package.url, target.url)
        self.assertEqual(self.package.groups, target.groups)
        self.assertEqual(self.package.licenses, target.licenses)
        self.assertEqual(self.package.architectures, target.architectures)
        self.assertEqual(self.package.replaces, target.replaces)
        self.assertEqual(self.package.conflicts, target.conflicts)
        self.assertEqual(self.package.provides, target.provides)
        self.assertEqual(self.package.backup, target.backup)
        self.assertEqual(self.package.options, target.options)
        self.assertEqual(self.package.noextract, target.noextract)
        self.assertEqual(self.package.makedepends, target.makedepends)
        self.assertEqual(self.package.sources, target.sources)
        self.assertEqual(self.package.optdepends, target.optdepends)
        self.assertEqual(self.package.checksums, target.checksums)
        self.assertEqual(self.package.install, target.install)

    def test_multiline(self):
        pkgbuild = FileMock()
        pkgbuild.write("""
            source=(foo \\
            baz)
            depends=(eggs \\
                spam\\
                pancakes)
            makedepends(funky_town # got to get funky!
                pan)
        """)
        target = parched.PKGBUILD(fileobj=pkgbuild)
        self.assertEqual(['foo', 'baz'], target.sources)
        self.assertEqual(['eggs', 'spam', 'pancakes'], target.depends)

    def test_substitution(self):
        self.package.sources = [
            '$url/files/$pkgname-$pkgver.tar.gz',
            '${url}/files/${pkgname}_doc-$pkgver.tar.gz'
        ]
        target = parched.PKGBUILD(fileobj=self.package.as_file())
        values = (self.package.url, self.package.name, self.package.version)
        parsed_sources = [
            '%s/files/%s-%s.tar.gz' % values,
            '%s/files/%s_doc-%s.tar.gz' % values,
        ]
        self.assertEqual(parsed_sources, target.sources)

    def test_non_standard_variable_substitution(self):
        pkgbuild = FileMock("""
            _pkgname=Foobar
            sources=($_pkgname.tar.gz)
        """)
        target = parched.PKGBUILD(fileobj=pkgbuild)
        self.assertEqual(["Foobar.tar.gz"], target.sources)

    def test_skip_function(self):
        pkgbuild = FileMock("""
            pkgname=foo
            build() {
                pkgname=bar
            }
        """)
        target = parched.PKGBUILD(fileobj=pkgbuild)
        self.assertEqual("foo", target.name)

    def test_quoted_value(self):
        """Right-hand side of assignment in quotes is parsed correctly."""
        self.package.description = "Someone's package"
        self.package.url = "'http://domain.tld/foo'"
        target = parched.PKGBUILD(fileobj=self.package.as_file())
        pkgbuild = self.package.as_file().read()
        self.assertTrue("pkgdesc=\"Someone's package\"" in pkgbuild)
        self.assertTrue("url='http://domain.tld/foo'" in pkgbuild)
        self.assertEqual(self.package.description, "Someone's package")
        self.assertEqual(self.package.url.strip("'"), target.url)


if __name__ == "__main__":
    unittest.main()
