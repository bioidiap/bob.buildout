==========================
 Buildout Recipes for Bob
==========================

This package contains a number of recipes to be used to build `Satellite
Packages
<https://github.com/idiap/bob/wiki/Virtual-Work-Environments-with-Buildout>`_
for `Bob <http://idiap.github.com/bob/>`_, a signal-processing and machine
learning toolbox originally developed by the Biometrics Group at Idiap, in
Switzerland.

.. note::

  You normally don't need to download this package directly. It will be done by
  Buildout automatically, if you followed our recipe to build `Satellite
  Packages
  <https://github.com/idiap/bob/wiki/Virtual-Work-Environments-with-Buildout>`.

Sphinx Recipe
-------------

Recipe for sphinx/buildout integration. To
use it, add something like the following to your buildout configuration::

  [sphinx]
  recipe = bob.buildout.recipes:sphinx
  eggs = ${buildout:eggs}
  source = ${buildout:directory}/docs ; where documentation is
  build = ${buildout:directory}/sphinx ; where results will be put at
  ;script = sphinxgen.py

The main difference between this package and the original is the addition of
the ``eggs`` parameter which obsoletes the use of ``interpreter`` in many
cases.

After running ``buildout`` you should get a ``sphinx`` executable script in
your ``bin`` directory you can use to scan and generate your documentation in
various formats. The name of the script generated matches the section name, but
you can overwrite it with the ``script`` parameter.

.. note::

  This recipe is heavily based on `collective.recipe.sphinxbuilder
  <http://pypi.python.org/pypi/collective.recipe.sphinxbuilder>`_.

Supported Options
=================

The recipe supports the following options::

  build (default: `sphinx`)
    Specify the build documentation root.

  source (default: `{build-directory}/docs`)
    Speficy the source directory of documentation.

  outputs (default: `html`)
    Multiple-line value that defines what kind of output to produce.  Can be
    `doctest`, `html`, `latex`, `pdf` or `epub`.

  script (default: name of buildout section)
    The name of the script generated

  interpreter
    Path to python interpreter to use when invoking sphinx-builder.

  extra-paths
    One or more extra paths to include in the generated test script. The paths
    are appended.

External Eggs Recipe
--------------------

This recipe receives as input a list of directories that it recursively scans
for eggs. If an egg is found, a similar `.egg-link` file is created in the
`buildout:eggs-directory` linking that egg to the current installation. 

To use this recipe, add something like the following to your buildout
configuration::

  [external]
  recipe = bob.buildout.recipes:external
  egg-directories = ../bob/build/lib

Supported Options
=================

The recipe supports the following options::

  egg-directories
    A list of directories that we will scan for eggs

  include-globs
    A list of globbing expression (``*.egg`` or ``bla-*.egg-info``, for
    example) for path names that will be considered for inclusion. Defaults to
    ``bob*.egg-info``.

  recurse
    If set to ``1`` or ``true``, recurses into all subdirectories (the default
    behavior). Else, if set to ``0`` or ``false``, does not, just looks what is
    available in the given directories.

  strict-version
    If set to ``1`` or ``true``, only consider packages with strictly valid
    version numbers in the sense of ``distutils.version.StrictVersion``. This
    parameter is set to ``true`` by default.

Nose Test Generator Recipe
--------------------------

Recipe to generate a test scanner for your package and dependencies (if you
would like to test them). To use this recipe,
just create a section on your ``buildout.cfg`` file like the following::

  [tests]
  recipe = bob.buildout.recipes:nose
  eggs = ${buildout:eggs}
  ;script = runtests.py

This run all tests declared in the ``buildout:eggs`` entry. You can specify
more entries in the ``tests:eggs`` entry if you need to do so. After running
buildout you should be left with a script called ``bin/tests`` that can run
all the tests for you. The name of the script generated matches the section
name, but you can overwrite it with the ``script`` parameter.

.. note::

  This recipe is heavily based on `pbp.recipe.noseruner package
  <http://pypi.python.org/pypi/pbp.recipe.noserunner/>`_.

Supported Options
=================

The recipe supports the following options::

  eggs
    The eggs option specified a list of eggs to test given as one ore more
    setuptools requirement strings.  Each string must be given on a separate
    line.

  script
    The script option gives the name of the script to generate, in the buildout
    bin directory.  Of the option isn't used, the part name will be used.

  extra-paths
    One or more extra paths to include in the generated test script. The paths
    are appended.

  defaults
    The defaults option lets you specify testrunner default options. These are
    specified as Python source for an expression yielding a list, typically a
    list literal.

  working-directory
    The working-directory option lets to specify a directory where the tests
    will run. The testrunner will change to this directory when run. If the
    working directory is the empty string or not specified at all, the recipe
    will not change the current working directory.

  environment
    A set of environment variables that should be exported before starting the
    tests.
