.. |travisci| image:: https://img.shields.io/travis/partmor/ezaero/master.svg?style=flat-square&logo=travis
   :target: https://travis-ci.org/partmor/ezaero
   
.. |appveyor| image:: https://img.shields.io/appveyor/ci/partmor/ezaero/master.svg?style=flat-square&logo=appveyor
   :target: https://ci.appveyor.com/project/partmor/ezaero/branch/master

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
   :target: https://github.com/partmor/ezaero/raw/master/LICENSE

ezaero
======

|travisci| |appveyor| |license|

[Under construction - see `Motivation`_]

ezaero *(easy-aero)* is an open source Python package oriented to implement numerical
methods for Aerodynamics, such as the 3D Vortex lattice Method for lifting surfaces.

.. image:: https://github.com/partmor/ezaero/raw/master/docs/source/examples/cl_distribution.png
   :align: center
   :width: 200px

Installation
------------

To install the package, clone the repo and pip install it:

.. code-block::

    $ git clone https://github.com/partmor/ezaero.git && cd ezaero
    $ pip install . # the dot means this directory

*[Still not available in PyPI, sorry for that!]*

Motivation
----------

This library is a free-time project. I am using it as an excuse to:

1) Experiment the performance of several scientific computing packages and tools (NumPy, Numba, etc.) applied to a computation-intensive application.
2) Learn how to properly test and package an open source Python library.
3) Redo *properly* (in terms of performance optimization, SW best practices, ...) a project I enjoyed a lot during my Master Thesis, back in 2014. I was curious to know how much could I improve the code performance.


My thesis covered the analysis of the aeroelastic response of an UAV in a gust scenario.

My plan is to implement the following modules in order:

+ 3D steady VLM
+ 3D then unsteady VLM
+ Wing motion equation solver (aeroelastic response)

If for some reason you run across this project, and find it useful or have suggestions,
don't be shy! feel free to contribute or `drop me a line <mailto:part.morales@gmail.com>`_.
