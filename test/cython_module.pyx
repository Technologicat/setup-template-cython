# -*- coding: utf-8 -*-
#
# cython: wraparound  = False
# cython: boundscheck = False
# cython: cdivision   = True
"""Example Cython module."""  # this is the Python-level docstring

from __future__ import division, print_function, absolute_import

# Silly example: check if input is 42, return True or False.
#
def g(int x):
    return (x == 42)

