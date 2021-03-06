.. jsonextended documentation master file, created by
   sphinx-quickstart on Sat Jun  3 02:06:22 2017.

JSON Extended
========================================

|Build Status| |Coverage Status| |PyPI| |Conda|

A module to extend the python json package functionality:

-  Treat a directory structure like a nested dictionary

-  **Lightweight plugin system**: define bespoke classes for parsing
   different file extensions (in-the-box: .json, .csv, .hdf5) and
   encoding/decoding objects.

-  **Lazy Loading**: read files only when they are indexed into

-  **Tab Completion**: index as tabs for quick exploration of data

-  **Manipulation of nested structures**, including; filter, merge, diff, flatten, unflatten

-  **Enhanced pretty printer**

-  **Output to directory structure** (of n folder levels)

-  **On-disk indexing** option for large json files (using the ijson
   package)

-  **Units schema** concept to apply and convert physical quantities (using the
   pint package)

- All functions are thoroughly documented with tested examples.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   readme
   functions_summary
   package_api
   releases

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |Build Status| image:: https://travis-ci.org/chrisjsewell/jsonextended.svg?branch=master
   :target: https://travis-ci.org/chrisjsewell/jsonextended
.. |Coverage Status| image:: https://coveralls.io/repos/github/chrisjsewell/jsonextended/badge.svg?branch=master
   :target: https://coveralls.io/github/chrisjsewell/jsonextended?branch=master
.. |PyPI| image:: https://img.shields.io/pypi/v/jsonextended.svg
   :target: https://pypi.python.org/pypi/jsonextended/
.. |Conda| image:: https://anaconda.org/conda-forge/jsonextended/badges/version.svg
   :target: https://anaconda.org/conda-forge/jsonextended