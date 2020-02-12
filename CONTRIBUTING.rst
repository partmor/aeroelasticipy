Contributing
============

For now, ezero is a personal free-time project and is still very small, hence all contributions are more than
welcome!

[Section shamelessly copied and adapted from `Poliastro`_]

.. _`Poliastro`: https://github.com/poliastro/poliastro

Bug reporting
-------------

Not only things break all the time, but also different people have different
use cases for the project. If you find anything that doesn't work as expected
or have suggestions, please refer to the `issue tracker`_ on GitHub.

.. _`issue tracker`: https://github.com/partmor/ezaero/issues

Documentation
-------------

Documentation can always be improved and made easier to understand for
newcomers. The docs are stored in text files under the `docs/`
directory, so if you think anything can be improved there please edit the
files and proceed in the same way as with `code writing`_.

The Python classes and methods also feature inline docs: if you detect
any inconsistency or opportunity for improvement, you can edit those too.

To build the docs, you must first create a development environment (see
below) and then in the ``docs/`` directory run the build command::

    $ cd docs
    $ make html

After this, the new docs will be inside ``_build/html``. You can open
them by running an HTTP server::

    $ cd _build/html
    $ python -m http.server
    Serving HTTP on 0.0.0.0 port 8000 ...

And point your browser to http://0.0.0.0:8000.

Code writing
------------

Code contributions are more than welcome!

If you are hesitant on what IDE or editor to use, just choose one that
you find comfortable and stick to it while you are learning. People have
strong opinions on which editor is better so I recommend you to ignore
the crowd for the time being - again, choose one that you like :)

If you ask me for a recommendation, I would suggest PyCharm (complete
IDE, free and gratis, RAM-hungry) or vim (powerful editor, very lightweight,
steep learning curve). Other people use Spyder, emacs, gedit, Notepad++,
Sublime, Atom...

You will also need to understand how git works. git is a decentralized
version control system that preserves the history of the software, helps
tracking changes and allows for multiple versions of the code to exist
at the same time. If you are new to git and version control, I recommend
following `the Try Git tutorial`_.

.. _`the Try Git tutorial`: https://try.github.io/

If you already know how all this works and would like to contribute new
features then that's awesome! Before rushing out though please make sure it
is within the scope of the library so you don't waste your time -
for the time being you can use the `issue tracker`_ to post your questions.

All new features should be thoroughly tested, and in the ideal case the
coverage rate should increase or stay the same. Automatic services will ensure
your code works on all the operative systems and package combinations
ezaero support - specifically, note that ezaero is a Python 3 only
library.

Development environment
-----------------------

These are some succint steps to set up a development environment and make your first pull request:

Setup the repository
~~~~~~~~~~~~~~~~~~~~
1. `Install git <https://git-scm.com/>`_ on your computer.
2. `Register to GitHub <https://github.com/>`_.
3. `Fork ezaero <https://help.github.com/articles/fork-a-repo/>`_.
4. `Clone your fork <https://help.github.com/articles/cloning-a-repository/>`_.

Create a virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Optional, but highly recommended. Using conda environments you have the advantage of pulling the Python version you need.

1. `Install conda <https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html>`_.
2. Create a conda environment named :code:`ezaero-dev` with Python 3.7: :code:`conda create -n ezaero-dev python=3.7`
3. `Activate the environment <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment>`_.
4. Install the development requirements: :code:`pip install -e /path/to/repo/[dev]`

Implement your changes
~~~~~~~~~~~~~~~~~~~~~~
1. Verify all checks and tests pass, with the command: :code:`tox`
2. Create a new branch.
3. Make your changes.
4. Run :code:`tox` again to execute style/formatting checks, unit tests, and documentation build. This will also test your latest changes.
5. Commit your changes.
6. `Push to your fork <https://help.github.com/articles/pushing-to-a-remote/>`_.
7. `Open a pull request! <https://help.github.com/articles/creating-a-pull-request/>`_
