# -*- coding: utf-8 -*-
#
"""setuptools-based setup.py template for Cython projects.

Main setup for the library.

Supports Python 2.7 and 3.4.

Usage as usual with setuptools:
    python setup.py build_ext
    python setup.py build
    python setup.py install
    python setup.py sdist

For details, see
    http://setuptools.readthedocs.io/en/latest/setuptools.html#command-reference
"""

from __future__ import division, print_function, absolute_import

try:
    # Python 3
    MyFileNotFoundError = FileNotFoundError
except:  # FileNotFoundError does not exist in Python 2.7
    # Python 2.7
    # - open() raises IOError
    # - remove() (not currently used here) raises OSError
    MyFileNotFoundError = (IOError, OSError)

#########################################################
# General config
#########################################################

# Name of the top-level package of your library.
#
# This is also the top level of its source tree, relative to the top-level project directory setup.py resides in.
#
libname="mylibrary"

# Choose build type.
#
build_type="optimized"
#build_type="debug"

# Short description for package list on PyPI
#
SHORTDESC="setuptools template for Cython projects"

# Long description for package homepage on PyPI
#
DESC="""setuptools-based setup.py template for Cython projects.

The focus of this template is on numerical scientific projects,
where a custom Cython extension (containing all-new code) can bring a large speedup.

For completeness, a minimal Cython module is included.

Supports Python 2.7 and 3.4.
"""

# Set up data files for packaging.
#
# Directories (relative to the top-level directory where setup.py resides) in which to look for data files.
datadirs  = ("test",)

# File extensions to be considered as data files. (Literal, no wildcards.)
dataexts  = (".py",  ".pyx", ".pxd",  ".c", ".cpp", ".h",  ".sh",  ".lyx", ".tex", ".txt", ".pdf")

# Standard documentation to detect (and package if it exists).
#
standard_docs     = ["README", "LICENSE", "TODO", "CHANGELOG", "AUTHORS"]  # just the basename without file extension
standard_doc_exts = [".md", ".rst", ".txt", ""]  # commonly .md for GitHub projects, but other projects may use .rst or .txt (or even blank).


#########################################################
# Init
#########################################################

# check for Python 2.7 or later
# http://stackoverflow.com/questions/19534896/enforcing-python-version-in-setup-py
import sys
if sys.version_info < (2,7):
    sys.exit('Sorry, Python < 2.7 is not supported')

import os

from setuptools import setup
from setuptools.extension import Extension

try:
    from Cython.Build import cythonize
except ImportError:
    sys.exit("Cython not found. Cython is needed to build the extension modules.")


#########################################################
# Definitions
#########################################################

# Define our base set of compiler and linker flags.
#
# This is geared toward x86_64, see
#    https://gcc.gnu.org/onlinedocs/gcc-4.6.4/gcc/i386-and-x86_002d64-Options.html
#
# Customize these as needed.
#
# Note that -O3 may sometimes cause mysterious problems, so we limit ourselves to -O2.

# Modules involving numerical computations
#
extra_compile_args_math_optimized    = ['-march=native', '-O2', '-msse', '-msse2', '-mfma', '-mfpmath=sse']
extra_compile_args_math_debug        = ['-march=native', '-O0', '-g']
extra_link_args_math_optimized       = []
extra_link_args_math_debug           = []

# Modules that do not involve numerical computations
#
extra_compile_args_nonmath_optimized = ['-O2']
extra_compile_args_nonmath_debug     = ['-O0', '-g']
extra_link_args_nonmath_optimized    = []
extra_link_args_nonmath_debug        = []

# Additional flags to compile/link with OpenMP
#
openmp_compile_args = ['-fopenmp']
openmp_link_args    = ['-fopenmp']


#########################################################
# Helpers
#########################################################

# Make absolute cimports work.
#
# See
#     https://github.com/cython/cython/wiki/PackageHierarchy
#
my_include_dirs = ["."]


# Choose the base set of compiler and linker flags.
#
if build_type == 'optimized':
    my_extra_compile_args_math    = extra_compile_args_math_optimized
    my_extra_compile_args_nonmath = extra_compile_args_nonmath_optimized
    my_extra_link_args_math       = extra_link_args_math_optimized
    my_extra_link_args_nonmath    = extra_link_args_nonmath_optimized
    my_debug = False
    print( "build configuration selected: optimized" )
elif build_type == 'debug':
    my_extra_compile_args_math    = extra_compile_args_math_debug
    my_extra_compile_args_nonmath = extra_compile_args_nonmath_debug
    my_extra_link_args_math       = extra_link_args_math_debug
    my_extra_link_args_nonmath    = extra_link_args_nonmath_debug
    my_debug = True
    print( "build configuration selected: debug" )
else:
    raise ValueError("Unknown build configuration '%s'; valid: 'optimized', 'debug'" % (build_type))


def declare_cython_extension(extName, use_math=False, use_openmp=False):
    """Declare a Cython extension module for setuptools.

Parameters:
    extName : str
        Absolute module name, e.g. use `mylibrary.mymodule.submodule`
        for the Cython source file `mylibrary/mymodule/submodule.pyx`.

    use_math : bool
        If True, set math flags and link with ``libm``.

    use_openmp : bool
        If True, compile and link with OpenMP.

Return value:
    Extension object
        that can be passed to ``setuptools.setup``.
"""
    extPath = extName.replace(".", os.path.sep)+".pyx"

    if use_math:
        compile_args = list(my_extra_compile_args_math) # copy
        link_args    = list(my_extra_link_args_math)
        libraries    = ["m"]  # link libm; this is a list of library names without the "lib" prefix
    else:
        compile_args = list(my_extra_compile_args_nonmath)
        link_args    = list(my_extra_link_args_nonmath)
        libraries    = None  # value if no libraries, see setuptools.extension._Extension

    # OpenMP
    if use_openmp:
        compile_args.insert( 0, openmp_compile_args )
        link_args.insert( 0, openmp_link_args )

    # See
    #    http://docs.cython.org/src/tutorial/external.html
    #
    # on linking libraries to your Cython extensions.
    #
    return Extension( extName,
                      [extPath],
                      extra_compile_args=compile_args,
                      extra_link_args=link_args,
                      libraries=libraries
                    )


# Gather user-defined data files
#
# http://stackoverflow.com/questions/13628979/setuptools-how-to-make-package-contain-extra-data-folder-and-all-folders-inside
#
datafiles = []
getext = lambda filename: os.path.splitext(filename)[1]
for datadir in datadirs:
    datafiles.extend( [(root, [os.path.join(root, f) for f in files if getext(f) in dataexts])
                       for root, dirs, files in os.walk(datadir)] )


# Add standard documentation (README et al.), if any, to data files
#
detected_docs = []
for docname in standard_docs:
    for ext in standard_doc_exts:
        filename = "".join( (docname, ext) )  # relative to the directory in which setup.py resides
        if os.path.isfile(filename):
            detected_docs.append(filename)
datafiles.append( ('.', detected_docs) )


# Extract __version__ from the package __init__.py
# (since it's not a good idea to actually run __init__.py during the build process).
#
# http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
#
import ast
init_py_path = os.path.join(libname, '__init__.py')
version = '0.0.unknown'
try:
    with open(init_py_path) as f:
        for line in f:
            if line.startswith('__version__'):
                version = ast.parse(line).body[0].value.s
                break
        else:
            print( "WARNING: Version information not found in '%s', using placeholder '%s'" % (init_py_path, version), file=sys.stderr )
except MyFileNotFoundError:
    print( "WARNING: Could not find file '%s', using placeholder version information '%s'" % (init_py_path, version), file=sys.stderr )


#########################################################
# Set up modules
#########################################################

# declare Cython extension modules here
#
ext_module_dostuff    = declare_cython_extension( "mylibrary.dostuff",              use_math=False, use_openmp=False )
ext_module_compute    = declare_cython_extension( "mylibrary.compute",              use_math=True,  use_openmp=False )
ext_module_helloworld = declare_cython_extension( "mylibrary.submodule.helloworld", use_math=False, use_openmp=False )

# this is mainly to allow a manual logical ordering of the declared modules
#
cython_ext_modules = [ext_module_dostuff,
                      ext_module_compute,
                      ext_module_helloworld]

# Call cythonize() explicitly, as recommended in the Cython documentation. See
#     http://cython.readthedocs.io/en/latest/src/reference/compilation.html#compiling-with-distutils
#
# This will favor Cython's own handling of '.pyx' sources over that provided by setuptools.
#
# Note that my_ext_modules is just a list of Extension objects. We could add any C sources (not coming from Cython modules) here if needed.
# cythonize() just performs the Cython-level processing, and returns a list of Extension objects.
#
my_ext_modules = cythonize( cython_ext_modules, include_path=my_include_dirs, gdb_debug=my_debug )


#########################################################
# Call setup()
#########################################################

setup(
    name = "setup-template-cython",
    version = version,
    author = "Juha Jeronen",
    author_email = "juha.jeronen@jyu.fi",
    url = "https://github.com/Technologicat/setup-template-cython",

    description = SHORTDESC,
    long_description = DESC,

    # CHANGE THIS
    license = "Unlicense",

    # free-form text field; http://stackoverflow.com/questions/34994130/what-platforms-argument-to-setup-in-setup-py-does
    platforms = ["Linux"],

    # See
    #    https://pypi.python.org/pypi?%3Aaction=list_classifiers
    #
    # for the standard classifiers.
    #
    # Remember to configure these appropriately for your project, especially license!
    #
    classifiers = [ "Development Status :: 4 - Beta",
                    "Environment :: Console",
                    "Intended Audience :: Developers",
                    "Intended Audience :: Science/Research",
                    "License :: Unlicense",  # not a standard classifier; CHANGE THIS
                    "Operating System :: POSIX :: Linux",
                    "Programming Language :: Cython",
                    "Programming Language :: Python",
                    "Programming Language :: Python :: 2",
                    "Programming Language :: Python :: 2.7",
                    "Programming Language :: Python :: 3",
                    "Programming Language :: Python :: 3.4",
                    "Topic :: Scientific/Engineering",
                    "Topic :: Scientific/Engineering :: Mathematics",
                    "Topic :: Software Development :: Libraries",
                    "Topic :: Software Development :: Libraries :: Python Modules"
                  ],

    # See
    #    http://setuptools.readthedocs.io/en/latest/setuptools.html
    #
    setup_requires = ["cython", "numpy"],
    install_requires = ["numpy"],
    provides = ["setup_template_cython"],

    # keywords for PyPI (in case you upload your project)
    #
    # e.g. the keywords your project uses as topics on GitHub, minus "python" (if there)
    #
    keywords = ["setuptools setup.py template example cython"],

    # All extension modules (list of Extension objects)
    #
    ext_modules = my_ext_modules,

    # Declare packages so that  python -m setup build  will copy .py files (especially __init__.py).
    #
    # This **does not** automatically recurse into subpackages, so they must also be declared.
    #
    packages = ["mylibrary", "mylibrary.submodule"],

    # Install also Cython headers so that other Cython modules can cimport ours
    #
    # Fileglobs relative to each package, **does not** automatically recurse into subpackages.
    #    
    # FIXME: force sdist, but sdist only, to keep the .pyx files (this puts them also in the bdist)
    package_data={'mylibrary': ['*.pxd', '*.pyx'],
                  'mylibrary.submodule': ['*.pxd', '*.pyx']},

    # Disable zip_safe, because:
    #   - Cython won't find .pxd files inside installed .egg, hard to compile libs depending on this one
    #   - dynamic loader may need to have the library unzipped to a temporary directory anyway (at import time)
    #
    zip_safe = False,

    # Custom data files not inside a Python package
    data_files = datafiles
)

