# -*- coding: utf-8 -*-
#
# cython: wraparound  = False
# cython: boundscheck = False
# cython: cdivision   = True
"""Example Cython module."""  # this is the Python-level docstring

from __future__ import division, print_function, absolute_import

# Echo the string s.
#
cdef void hello(str s):
    print(s)  # this is really, really silly (Python print() in a cdef function)

