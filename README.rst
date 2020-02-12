.. |travisci| image:: https://img.shields.io/travis/partmor/ezaero/master.svg?style=flat-square&logo=travis
   :target: https://travis-ci.org/partmor/ezaero
   
.. |appveyor| image:: https://img.shields.io/appveyor/ci/partmor/ezaero/master.svg?style=flat-square&logo=appveyor
   :target: https://ci.appveyor.com/project/partmor/ezaero/branch/master

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
   :target: https://github.com/partmor/ezaero/raw/master/LICENSE
   
.. |docs| image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat-square
   :target: https://ezaero.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
   
.. |pypi_v| image:: https://img.shields.io/pypi/v/ezaero.svg
   :target: https://pypi.org/project/ezaero/
   :alt: Latest PyPI version
   
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/ezaero.svg
   :target: https://pypi.org/project/ezaero/
   :alt: Python versions
   
.. |codecov| image:: https://img.shields.io/codecov/c/github/partmor/ezaero.svg?style=flat-square
   :target: https://codecov.io/github/partmor/ezaero?branch=master

ezaero
======

|travisci| |appveyor| |codecov| |docs| |license| |pypi_v| |pyversions| 

ezaero *(easy-aero)* is an open source Python package oriented to implement numerical
methods for Aerodynamics, such as the 3D Vortex lattice Method for lifting surfaces.

.. image:: https://github.com/partmor/ezaero/raw/master/docs/examples/cl_distribution.png
   :align: center
   :width: 200px

Documentation
-------------
|docs|

API documentation and examples can be found on https://ezaero.readthedocs.io.

Examples
--------

You can check out the examples in the `gallery`_, and export them as .py scripts or Jupyter notebooks to continue exploring!

.. _`gallery`: https://ezaero.readthedocs.io/en/latest/auto_examples/

Requirements
------------
ezaero has the following dependencies:

* Python (>=3.6)
* NumPy
* matplotlib

ezaero is tested on Linux, Windows and OS X on Python 3.6 and 3.7.

==============  ============  ===================
Platform        Site          Status
==============  ============  ===================
Linux / OS X    Travis CI     |travisci|
Windows x64     Appveyor      |appveyor|
==============  ============  ===================

Installation
------------

To install the package, simply use pip:

.. code-block::

    $ pip install ezaero


Contributing
------------

All contributions and suggestions are welcome! For more details, check out `CONTRIBUTING.rst`_.

.. _`CONTRIBUTING.rst`: https://github.com/partmor/ezaero/blob/master/CONTRIBUTING.rst

Motivation
----------

This library is a free-time project. I am using it as an excuse to:

1) Experiment the performance of several scientific computing packages and tools (NumPy, Numba, etc.) applied to a computation-intensive application.
2) Learn how to properly package an open source Python library, leveraging testing with the excelent free CI tools.
3) Redo *properly* (in terms of performance optimization, SW best practices, ...) a project I enjoyed a lot during my Master Thesis, back in 2014. I have always been curious to know how much could I improve the code performance.


My thesis covered the analysis of the aeroelastic response of an UAV in a gust scenario.

My plan is to implement the following modules in order:

+ 3D steady VLM
+ 3D then unsteady VLM
+ Wing motion equation solver (aeroelastic response)

If for some reason you run across this project, and find it useful or have suggestions,
don't be shy! feel free to contribute or `drop me a line <mailto:part.morales@gmail.com>`_.
