from distutils.core import setup
from distutils.extension import Extension
from Pyrex.Distutils import build_ext

setup(name='parched',
    version='0.1',
    description="Pacman package and PKGBUILD parser",
    author="Sebastian Nowicki",
    author_email="sebnow@gmail.com",
    url="http://www.github.com/sebnow/parched/",
    ext_modules=[
      Extension("parched", ["parched.pyx"], libraries=["pkgparse"])
    ],
    cmdclass = {'build_ext': build_ext},
    classifiers=['Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Interpreters',
    ],
)