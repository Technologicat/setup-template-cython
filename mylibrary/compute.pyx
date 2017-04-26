# -*- coding: utf-8 -*-
#
# cython: wraparound  = False
# cython: boundscheck = False
# cython: cdivision   = True
"""Example Cython module."""

from __future__ import division, print_function, absolute_import


# import something from libm
from libc.math cimport sqrt as c_sqrt

# we use NumPy for memory allocation
import numpy as np


# The docstring conforms to the NumPyDoc style:
#
#    https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt
#
# See also
#    https://pypi.python.org/pypi/numpydoc
#    http://docutils.sourceforge.net/docs/user/rst/demo.txt
#
# We use the buffer protocol:
#    http://cython.readthedocs.io/en/latest/src/userguide/memoryviews.html
#
def f( double[::1] x ):
    """Example math function.

Take the square root, elementwise.

Parameters:
    x : rank-1 np.array of double
        Numbers to be square-rooted.

Return value:
    rank-1 np.array of double
        The square roots.
"""
    cdef int n = x.shape[0]

    # np.empty() is a pretty good mechanism for dynamic allocation of arrays,
    # as long as memory allocation can be done on the Python side,
    #
    # If you absolutely need to dynamically allocate memory in nogil code,
    # then "from libc.stdlib cimport malloc, free", and be ready for pain.
    #
    cdef double[::1] out = np.empty( (n,), dtype=np.float64, order="C" )

    # Memoryview slices don't do  out[:] = ...  assignments, so we loop.
    #
    # Everything is typed, though, so the loop will run at C speed.
    #
    # As a bonus, we release the GIL, so any other Python threads
    # can proceed while this one is computing.
    #
    # We could also "cimport cython.parallel" and "for j in cython.parallel.prange(n):"
    # if we wanted to link this with OpenMP.
    #
    cdef int j
    with nogil:
        for j in range(n):
            out[j] = c_sqrt(x[j])

    return np.asanyarray(out)  # return proper np.ndarray, not memoryview slice

