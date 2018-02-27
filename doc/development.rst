.. _bob.buildout.dev:

=========================
 Developing bob.buildout
=========================

You can quickly test this package by running the following commands:

.. code-block:: sh

   $ buildout
   $ ./bin/nosetests -sv

Testing is limited to certain internal functionality. If you want to do an
extensive test and make sure changes are operating when you use this package to
create an environment for *another* package, please read on.


Cross-developing with another package
-------------------------------------

This is a chicken-and-egg problem as developing another package with a *new*
version of this package requires a working installation of ``bob.buildout``. In
order to break the loop, you'll need to first buildout with a simplified
version of ``buildout.cfg``, to tell buildout ``bob.buildout`` is being
developed alongside the test package. As an example, we'll develop
``bob.buildout`` in a ``bob.extension`` checkout:

.. code-block:: sh

   $ git clone https://gitlab.idiap.ch/bob/bob.extension
   $ cd bob.extension
   # create the file first.cfg with the following contents:
   $ cat first.cfg
   [buildout]
   parts =
   develop = src/buildout
   $ mkdir src
   $ git clone https://gitlab.idiap.ch/bob/bob.buildout src/bob.buildout

Setup your base conda-environment as usual and the, run ``buildout -c
first.cfg``:


.. code-block:: sh

   $ buildout -c first.cfg


The previous command should not download anything from PyPI_ and will create a
symbolic egg link in ``develop-eggs`` called ``bob.buildout.egg-link``. To make
sure your ``first.cfg`` bootstrap procedure worked, check there. Now, slightly
modify ``buildout.cfg`` from ``bob.extension`` to include a new line in the
``buildout.develop`` entry before ``.``, so the new buildout will also take the
bootstrapped buildout into consideration. It should look like this:


.. code-block:: sh

   $ cat buildout.cfg
   [buildout]
   parts = scripts
   develop = src/bob.buildout
             .
   eggs = bob.extension
   extensions = bob.buildout
   newest = false
   verbose = true

   [scripts]
   recipe = bob.buildout:scripts
   dependent-scripts = true


Now run buildout normally, against the modified ``buildout.cfg``:

.. code-block:: sh

   $ buildout
   ...


This last step should provide you with a setup as performed by the
bleeding-edge version of bob.buildout you have checked-out on the ``src``
directory. You can modify it and re-run ``buildout`` until everything looks in
order.


Releasing bob.buildout
----------------------

This is a standard |project| package and therefore you **must** follow the
standard releasing procedure using ``bob_new_version.py`` or any more recent
script available for such purpose.

You may create a ``bob.extension``-based environment for such as per
instructions above or start from a pure conda-based install which contains
``bob.extension`` and run that script from it.


.. include:: links.rst
