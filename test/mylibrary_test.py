# -*- coding: utf-8 -*-
"""Test mylibrary."""

from __future__ import division, print_function, absolute_import

import sys

import numpy as np

# This requires mylibrary to be compiled and installed first (using the top-level setup.py).
#
try:
    import mylibrary.dostuff as dostuff
    import mylibrary.compute as compute
except ImportError:
    print( "ERROR: mylibrary not found; is it installed (in this Python)?", file=sys.stderr )
    raise

# Import local Cython module.
#
# This module belongs to the tests, and is not part of mylibrary.
#
try:
    import cython_module
except ImportError:
    print( "ERROR: cython_module.pyx must be compiled first; run  'python -m setup build_ext --inplace'  to do this", file=sys.stderr )
    raise


def test():
    # Test the dostuff module in the installed mylibrary
    #
    # This should just print "Hello world" after jumping through all the API hoops
    dostuff.hello("Hello world")

    # Test the compute module in the installed mylibrary
    x  = np.arange(1000, dtype=np.float64)
    y1 = np.sqrt(x)
    y2 = compute.f(x)
    if np.allclose( y1, y2 ):
        print("**PASS** compute.f()")
    else:
        print("**FAIL** compute.f()")

    # Test the local Cython module
    b1 = cython_module.g(42)
    b2 = cython_module.g(23)
    if b1 and not b2:
        print("**PASS** cython_module.g()")
    else:
        print("**FAIL** cython_module.g()")


if __name__ == '__main__':
    test()

