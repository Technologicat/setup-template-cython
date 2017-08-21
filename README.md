## setup-template-cython

Setuptools-based `setup.py` template for Cython projects

### Introduction

Setuptools[[1]][setuptools] has become the tool of choice[[2]][packaging] for packaging Python projects, yet not much documentation is available on how to use setuptools in Cython projects. As of this writing (Cython 0.25), Cython's [official packaging instructions](http://cython.readthedocs.io/en/latest/src/reference/compilation.html#distributing-cython-modules) are based on distutils.

For packages to be distributed (especially through [PyPI](https://pypi.python.org/pypi)), setuptools is preferable, since the documentation on distributing packages[[3]][distributing] assumes that is what the developer uses. Also, [setuptools adds dependency resolution](http://stackoverflow.com/questions/25337706/setuptools-vs-distutils-why-is-distutils-still-a-thing) (over distutils), which is an essential feature of `pip`.

This very minimal project documents the author's best guess at current best practices for the packaging and distribution of Cython projects, by piecing together information from various sources. Possible corrections, if any, are welcome.

This is intended as a template [`setup.py`](setup.py) for new Cython projects. For completeness, a minimal Cython-based example library is included, containing examples of things such as absolute cimports, subpackages, [NumPyDoc](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt) style docstrings, and using [memoryviews](http://cython.readthedocs.io/en/latest/src/userguide/memoryviews.html) for passing arrays (for the last two, see [compute.pyx](mylibrary/compute.pyx)). The example in the [test/](test/) subdirectory demonstrates usage of the example library after it is installed.

A pruned-down version of setup.py for pure Python projects, called [`setup-purepython.py`](setup-purepython.py), is also provided for comparison.

This project is placed under The Unlicense so as to allow its use anywhere. Code snippets based on StackOverflow answers are credited by providing the original links.

This is similar to [simple-cython-example](https://github.com/thearn/simple-cython-example), but different. Here the focus is on numerical scientific projects, where a custom Cython extension (containing all-new code) can bring a large speedup.

The aim is to help open-sourcing such extensions in a manner that lets others effortlessly compile them (also in practice), thus advancing the openness and repeatability of science.


### Features

Our [`setup.py`](setup.py) features the following:

 - The most important fields of `setup()`
   - If this is all you need, [simple-cython-example](https://github.com/thearn/simple-cython-example) is much cleaner.
   - If this is all you need, and you somehow ended up here even though your project is pure Python, [PyPA's sampleproject](https://github.com/pypa/sampleproject/blob/master/setup.py) (as mentioned in [[4]][setup-py]) has more detail on this.
 - How to get `absolute_import` working in a Cython project
   - For compatibility with both Python 3 and Python 2.7 (with `from __future__ import absolute_import`)
   - For scientific developers used to Python 2.7, this is perhaps the only tricky part in getting custom Cython code to play nicely with Python 3. (As noted elsewhere[[a]](http://www.python3statement.org/)[[b]](http://python-3-for-scientists.readthedocs.io/en/latest/), it is time to move to Python 3.)
 - How to automatically grab `__version__` from `mylibrary/__init__.py` (using AST; no import or regexes), so that you can declare your package version [OnceAndOnlyOnce](http://wiki.c2.com/?OnceAndOnlyOnce) (based on [[5]][getversion])
 - Hopefully appropriate compiler and linker flags for math and non-math modules on `x86_64`, in production and debug configurations.
   - Also compiler and linker flags for OpenMP, to support `cython.parallel.prange`.
 - How to make `setup.py` pick up non-package data files, such as your documentation and usage examples (based on [[6]][datafolder])
 - How to make `setup.py` pick up data files inside your Python packages
 - How to enforce that `setup.py` is running under a given minimum Python version ([considered harmful](http://stackoverflow.com/a/1093331), but if duck-checking for individual features is not an option for a reason or another) (based on [[7]][enforcing])
 - Disabling `zip_safe`. Having `zip_safe` enabled (which will in practice happen by default) is a bad idea for Cython projects, because:
   - Cython (as of this writing, version 0.25) will not see `.pxd` headers inside installed `.egg` files. Thus other libraries cannot `cimport` modules from yours if it has `zip_safe` set.
   - At (Python-level) `import` time, the OS's dynamic library loader usually needs to have the `.so` unzipped (from the `.egg`) to a temporary directory anyway.


### Usage

See the [setuptools manual](http://setuptools.readthedocs.io/en/latest/setuptools.html#command-reference). Perhaps the most useful commands are:

```bash
python setup.py build_ext
python setup.py build    # copies .py files in the Python packages
python setup.py install  # will automatically "build" and "bdist"
python setup.py sdist
```

Substitute `python2` or `python3` for `python` if needed.

For `build_ext`, the switch `--inplace` may be useful for one-file throwaway projects, but packages to be installed are generally much better off by letting setuptools create a `build/` subdirectory.

For `install`, the switch `--user` may be useful. As can, alternatively, running the command through `sudo`, depending on your installation.

#### Uninstalling

Sometimes it is useful to uninstall the installed copy of your project (e.g. during development/testing of the install step for a new version). Whereas `setuptools` itself does not know how to uninstall packages, `pip` does. This applies also to `setuptools`-based packages not installed by `pip` itself.

For example, to uninstall `mylibrary` that is provided in this template project:

```bash
pip uninstall mylibrary
```

Note that `pip` will automatically check also the user directory (packages installed with `python setup.py install --user`) for the package to uninstall; there is no need to specify any options for that.

Substitute `pip2` or `pip3` for `pip` as needed; run through `sudo` if needed.

To check whether your default `pip` manages your Python 2 or Python 3 packages, use `pip --version`.

#### Binary distributions

As noted in the [Python packaging guide](https://packaging.python.org/distributing/#platform-wheels), PyPI accepts platform wheels (platform-specific binary distributions) for Linux only if they conform to [the `manylinux1` ABI](https://www.python.org/dev/peps/pep-0513/), so running `python setup.py bdist_wheel` on an arbitrary development machine is generally not very useful for the purposes of distribution.

For the adventurous, PyPA provides [instructions](https://github.com/pypa/manylinux) along with a Docker image.

For the less adventurous, just make an sdist and upload that; scientific Linux users are likely not scared by an automatic compilation step.


### Notes

 0. This project assumes the end user will have Cython installed, which is likely the case for people writing and interacting with numerics code in Python. Indeed, our [`setup.py`](setup.py) has Cython set as a requirement, and hence the eventual `pip install mylibrary` will pull in Cython if it is not installed.  

    The Cython extensions are always compiled using Cython. Or in other words, regular-end-user-friendly logic for conditionally compiling only the Cython-generated C source, or the original Cython source, has **not** been included. If this is needed, see [this StackOverflow discussion](http://stackoverflow.com/questions/4505747/how-should-i-[5]-a-python-package-that-contains-cython-code) for hints. See also item 2 below.  

    The generated C source files, however, are included in the resulting distribution (both sdist and bdist).

 1. In Cython projects, it is preferable to always use absolute module paths when `absolute_import` is in use, even if the module to be cimported is located in the same directory (as the module that is doing the cimport). This allows using the same module paths for imports and cimports.  
 
    The reason for this recommendation is that the relative variant (`from . cimport foo`), although in line with [PEP 328](https://www.python.org/dev/peps/pep-0328/), is difficult to get to work properly with Cython's include path.  

    Our [`setup.py`](setup.py) adds `.`, the top-level directory containing `setup.py`, to Cython's include path, but does not add any of its subdirectories. This makes the cimports with absolute module paths work correctly[[8]][packagehierarchy] (also when pointing to the library being compiled), assuming `mylibrary` lives in a `mylibrary/` subdirectory of the top-level directory that contains `setup.py`. See the included example.

 2. Historically, it was common practice in `setup.py` to import Cython's replacement for distutils' `build_ext`, in order to make `setup()` recognize `.pyx` source files.  

    Instead, we let setuptools keep its `build_ext`, and call `cythonize()` explicitly in the invocation of `setup()`. As of this writing, this is the approach given in [Cython's documentation](http://cython.readthedocs.io/en/latest/src/reference/compilation.html#compiling-with-distutils), albeit it refers to distutils instead of setuptools.  

    This gives us some additional bonuses:
      - Cython extensions can be compiled in debug mode (for use with [cygdb](http://cython.readthedocs.io/en/latest/src/userguide/debugging.html)).
      - We get `make`-like dependency resolution; a `.pyx` source file is automatically re-cythonized, if a `.pxd` file it cimports, changes.
      - We get the nice `[1/4] Cythonizing mylibrary/main.pyx` progress messages when `setup.py` runs, whenever Cython detects it needs to compile `.pyx` sources to C.
      - By requiring Cython, there is no need to store the generated C source files in version control; they are not meant to be directly human-editable.

    The setuptools documentation gives advice that, depending on interpretation, [may be in conflict with this](https://setuptools.readthedocs.io/en/latest/setuptools.html#distributing-extensions-compiled-with-pyrex) (considering Cython is based on Pyrex). We do not import Cython's replacement for `build_ext`, but following the Cython documentation, we do import `cythonize` and call it explicitly.  

    Because we do this, setuptools sees only C sources, so we miss setuptools' [automatic switching](https://setuptools.readthedocs.io/en/latest/setuptools.html#distributing-extensions-compiled-with-pyrex) of Cython and C compilation depending on whether Cython is installed (see the source code for `setuptools.extension.Extension`). Our approach requires having Cython installed even if the generated C sources are up to date (in which case the Cython compilation step will no-op, skipping to the C compilation step).  

    Note that as a side effect, `cythonize()` will run even if the command-line options given to `setup.py` are nonsense (or more commonly, contain a typo), since it runs first, before control even passes to `setup()`. (I.e., don't go grab your coffee until the build starts compiling the generated C sources.)  

    For better or worse, the chosen approach favors Cython's own mechanism for handling `.pyx` sources over the one provided by setuptools.

 3. Old versions of Cython may choke on the `cythonize()` options `include_path` and/or `gdb_debug`. If `setup.py` gives mysterious errors that can be traced back to these, try upgrading your Cython installation.  

    Note that `pip install cython --upgrade` gives you the latest version. (You may need to add `--user`, or run it through `sudo`, depending on your installation.)

 4. Using setuptools with Cython projects needs `setuptools >= 18.0`, to correctly support Cython in `requires`[[9]][setuptools18].  

    In practice this is not a limitation, as `18.0` is already a very old version (`35.0` being current at the time of this writing). In the unlikely event that it is necessary to support versions of setuptools even older than `18.0`, it is possible[[9]][setuptools18] to use [setuptools-cython](https://pypi.python.org/pypi/setuptools_cython/) from PyPI. (This package is not needed if `setuptools >= 18.0`.)

 5. If you are familiar with distutils, but new to setuptools, see [the list of new and changed keywords](https://setuptools.readthedocs.io/en/latest/setuptools.html#new-and-changed-setup-keywords) in the setuptools documentation.


### Distributing your package

If you choose to release your package for distribution:

 0. See the [distributing](https://packaging.python.org/distributing/) section of the packaging guide, and especially the subsection on [uploading to PyPI](https://packaging.python.org/distributing/#uploading-your-project-to-pypi).  

    Especially if your package has dependencies, it is important to get at least an sdist onto PyPI to make the package easy to install (via `pip install`).  

      - Also, keep in mind that outside managed environments such as Anaconda, `pip` is the preferred way for installing scientific Python packages, even though having multiple package managers on the same system could be considered harmful. Scientific packages are relatively rapidly gaining new features, thus making access to the latest release crucial.  

        (Debian-based Linux distributions avoid conflicts between the two sets of managed files by making `sudo pip install` install to `/usr/local`, while the system `apt-get` installs to `/usr`. This does not, however, prevent breakage caused by overrides (loading a newer version from `/usr/local`), if it happens that some Python package is not fully backward-compatible. A proper solution requires [one of the virtualenv tools](http://stackoverflow.com/questions/41573587/what-is-the-difference-between-venv-pyvenv-pyenv-virtualenv-virtualenvwrappe) at the user end.)  

 1. Be sure to use `twine upload`, **not** ~~`python -m setup upload`~~, since the latter may transmit your password in plaintext.  

    ~~Before the first upload of a new project, use `twine register`.~~ As of August 2017, pre-registration of new packages is no longer needed or supported; just proceed to upload. See [new instructions](https://packaging.python.org/guides/migrating-to-pypi-org/#uploading).  

    [Official instructions for twine](https://pypi.python.org/pypi/twine).

 2. Generally speaking, it is [a good idea to disregard old advice](http://stackoverflow.com/a/14753678) on Python packaging. By 2020 when Python 2.7 support ends, that probably includes this document.  

    For example, keep in mind that `pip` has replaced `ez_setup`, and nowadays `pip` (in practice) comes with Python.  

    Many Python distribution tools have been sidelined by history, or merged back into the supported ones (see [the StackOverflow answer already linked above](http://stackoverflow.com/a/14753678)). Distutils and setuptools remain, nowadays [fulfilling different roles](http://stackoverflow.com/a/40176290).


### License

[The Unlicense](LICENSE.md)

[setuptools]: https://packaging.python.org/key_projects/#easy-install
[packaging]: https://packaging.python.org/current/#packaging-tool-recommendations
[distributing]: https://packaging.python.org/distributing/
[setup-py]: https://packaging.python.org/distributing/#setup-py
[getversion]: http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
[datafolder]: http://stackoverflow.com/questions/13628979/setuptools-how-to-make-package-contain-extra-data-folder-and-all-folders-inside
[enforcing]: http://stackoverflow.com/questions/19534896/enforcing-python-version-in-setup-py
[packagehierarchy]: https://github.com/cython/cython/wiki/PackageHierarchy
[setuptools18]: http://stackoverflow.com/a/27420487

