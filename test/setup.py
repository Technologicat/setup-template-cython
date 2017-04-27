# -*- coding: utf-8 -*-
#
"""setuptools-based setup.py template for Cython projects.

Setup for local modules in this directory, that are not installed as part of the library.

Supports Python 2.7 and 3.4.

Usage:
    python setup.py build_ext --inplace
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

# Choose build type.
#
build_type="optimized"
#build_type="debug"


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
        Absolute module name, e.g. use `mylibrary.mypackage.subpackage`
        for the Cython source file `mylibrary/mypackage/subpackage.pyx`.

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


#########################################################
# Set up modules
#########################################################

# declare Cython extension modules here
#
ext_module_cythonmodule = declare_cython_extension( "cython_module", use_math=False, use_openmp=False )

# this is mainly to allow a manual logical ordering of the declared modules
#
cython_ext_modules = [ext_module_cythonmodule]

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
    # See
    #    http://setuptools.readthedocs.io/en/latest/setuptools.html
    #
    setup_requires = ["cython", "numpy"],
    install_requires = ["numpy"],

    # All extension modules (list of Extension objects)
    #
    ext_modules = my_ext_modules
)

