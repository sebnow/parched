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
from StringIO import StringIO # cStringIO.StringIO can't be subclassed

import parched

class FileMock(StringIO):
    def __init__(self, buffer, name=None):
        self._name = name
        StringIO.__init__(self, buffer)

    @property
    def name(self):
        return self._name


class TarFileMock(Mock):
    """A mock tarfile object"""
    def __init__(self, *args, **kwargs):
       self._files = {}

    def add(self, fileobj):
        self._files[fileobj.name] = fileobj

    def extractfile(self, name):
        """Returns a :class:`FileMock` object"""
        return self._files[name]


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
        content.append('url=%s' % self.name)
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
        self.assertEquals(self.package.name, target.name)
        self.assertEquals(self.package.version, target.version)
        self.assertEquals(self.package.release, target.release)
        self.assertEquals(self.package.description, target.description)
        self.assertEquals(self.package.url, target.url)
        self.assertEquals(self.package.groups, target.groups)
        self.assertEquals(self.package.licenses, target.licenses)
        self.assertEquals(self.package.architectures, target.architectures)
        self.assertEquals(self.package.replaces, target.replaces)
        self.assertEquals(self.package.conflicts, target.conflicts)
        self.assertEquals(self.package.provides, target.provides)
        self.assertEquals(self.package.backup, target.backup)
        self.assertEquals(self.package.options, target.options)
        self.assertEquals(self.package.noextract, target.noextract)
        self.assertEquals(self.package.makedepends, target.makedepends)
        self.assertEquals(self.package.sources, target.sources)
        self.assertEquals(self.package.optdepends, target.optdepends)
        self.assertEquals(self.package.checksums, target.checksums)
        self.assertEquals(self.package.install, target.install)

    def test_multiline(self):
        pkgbuild = StringIO()
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
        self.assertEquals(['foo', 'baz'], target.sources)
        self.assertEquals(['eggs', 'spam', 'pancakes'], target.depends)

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
        self.assertEquals(parsed_sources, target.sources)

    def test_non_standard_variable_substitution(self):
        pkgbuild = StringIO("""
            _pkgname=Foobar
            sources=($_pkgname.tar.gz)
        """)
        target = parched.PKGBUILD(fileobj=pkgbuild)
        self.assertEquals(["Foobar.tar.gz"], target.sources)

if __name__ == "__main__":
    unittest.main()
