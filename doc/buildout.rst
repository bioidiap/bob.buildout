.. bob.buildout.recipes:


=======================
 Extension and Recipes
=======================

This package is composed of an extension to zc.buildout_ and a recipe. We
recommend you use both during the creation of your own package-based recipes.
Here is a typical ``buildout.cfg`` file that can be used to setup the
development of your own package, and which we normally ship with all
|project|-based packages:


.. code-block:: ini

   [buildout]
   parts = scripts
   develop = .
   eggs = <PACKAGE>
   extensions = bob.buildout
   newest = false
   verbose = true

   [scripts]
   recipe = bob.buildout:scripts
   dependent-scripts = true


Replace ``<PACKAGE>`` by your package name and you should be ready to run the
``buildout`` application. If you're curious about zc.buildout_ and how to
structure your recipe to take full advantage of it, we advise you seek
documentation on that package on its website or by searching the internet.

The above setup will include all required material for building both simple
python or python/C/C++ packages from |project|.

By using extension ``bob.buildout`` on the ``buildout`` section of your recipe,
you ensure the current package will be built taking into consideration all
required environment/compiler settings required by |project|. This extension is
strictly required for packages containing C/C++ bindings, but it is harmless to
include it in Python-only packages.

The section ``scripts`` define a list of scripts that will be installed on the
``bin`` directory. By default, we make sure all packages listed in
``buildout.eggs`` are available, as well as typical packages required for
development such as ``sphinx``, for documentation building, ``nose`` for
running your test suite and ``coverage``, for code coverage reporting. You may
augment the ``eggs`` entry on the ``buildout`` section if you'd like further
packages to be installed on your development environment. It is your call. An
example package that is often listed there is ``ipdb`` - the iPython based
python debugger. The syntax of the ``eggs`` entry on the ``buildout`` section
is one package per line.

The entry ``develop`` on the ``buildout`` section indicates to buildout the
root directories of packages that it should take, prioritarily, before
considering potential versions installed on base python (conda) environment. It
typically says just ``.`` (dot), as we're typically willing to *only* make
buildout aware of our local checkout. It can include more directories (one per
line), if we'd like to cross-develop more packages. That is what we do, for
example, when using the extension ``mr.developer`` (see:
:ref:`bob.extension` development). For each package listed in ``develop``,
buildout will run the equivalent of ``cd <dir> && python setup.py develop`` on
each package **before** trying to resolve the dependencies in ``eggs``. It will
then consider those locally installed packages in final load-path scheme for
your applications.

In case you're curious, the ``buildout.newest`` flag is internal to
zc.buildout_. It instructs the setuptools_ machinery to consider or not
versions of packages currently installed. If ``newest=true``, then only the
absolute newest packages in PyPI_ can satisfy the build. By default, we let
this setting to ``false`` indicating that what is currently installed will be
sufficient. Only change it if you know the implications. Note, for example, in
this case, you may not be testing anymore, exclusively, against a
|project|-agreed set of dependencies.

The remainder flags and options are explained next.


Supported extension options
---------------------------

Here is a list of supported options for the ``bob.buildout``. They should
appear in the ``buildout`` section of your recipe. They are considered for as
long as ``bob.buildout`` is listed as an extension.


``verbose``

  If set, buildout it will output the compilation commands while compiling the
  module. This flag should go into the ``buildout`` section of your recipe.
  Accepted values are ``true`` or ``false``.(the default).


``prefixes``

  A list of directories where this recipe will look for installed software,
  such as compiled libraries and header files. It is important if you're
  compiling a package that requires external software such as ffmpeg or blitz++
  header files to be available. It is the same as setting the environment
  variable ``BOB_PREFIX_PATH`` to a list of paths containing externally
  installed software. As a side-effect, setting ``BOB_PREFIX_PATH`` also sets,
  internally, ``PKG_CONFIG_PATH`` to a list of directories following where to
  search for pkg-config files.

  You typically don't need to set this manually since ``bob.extension`` is
  smart enough to figure out where to find external libraries. This is even
  more true if you're using conda-based installations as the bootstrapping
  environment of your buildout.


``debug``

  If set, the module will be compiled with debugging symbols and with
  optimization turned off. If ``debug`` is set to ``true``, this is equivalent
  to appending the environment variables ``CFLAGS`` and ``CXXFLAGS`` with ``-O0
  -g``. By default, the value is ``false``. This setting is advised if you are
  compiling python C/C++ bindings and would like to debug C/C++ code locally.


``environ``

  The name of another section on your configuration file that contains the
  names and values of environment variables that should be set before any
  possible build takes place. This section is named, by default, ``environ``.
  That is, if you provide a section named ``environ`` on your buildout recipe,
  then you don't need to explicitly specify its name using this flag.

  If a section named ``environ`` (or whatever lists the ``environ`` override on
  the ``buildout`` section of your recipe) exists, it is read and the
  environment variables are set **before** the specified packages are built.
  You can use variable substitution on this section. Here is an an example::

    [environ]
    CFLAGS = '-O0 -g -DNDEBUG'
    CXXFLAGS = ${CFLAGS}

  Notice there is some functionality overlap between the previous flags and the
  use of section ``environ``. While it is more flexible, you must understand
  the consequences of setting both ``prefixes`` and ``debug``, together with
  ``environ``. The rule is simple: values set on the ``environ`` section have
  **precedence** to ``debug`` and ``prefixes``. If you set ``debug`` and
  ``CFLAGS`` (or ``CXXFLAGS``) in the ``environ`` section, for example, then
  the values on the final ``CFLAGS`` variable would be ``-O0 -g`` followed by
  ``environ``'s ``CFLAGS`` settings. Analogously, the paths defined by
  ``environ``'s ``BOB_PREFIX_PATH`` and ``PKG_CONFIG_PATH`` are **prepended**
  to those listed in ``prefixes``, if that is also set.


The ``scripts`` recipe
----------------------

By using the recipe ``bob.buildout:scripts`` on one of the sections of your
recipe, you ensure the scripts generated by the recipe will be built taking
into consideration all installed packages from your base python environment
(typically a conda-based installation). If you don't use the
``bob.buildout:scripts`` recipe, zc.buildout_, by default, assumes no packages
are availabe on the python installation and may download/recompile all
dependencies from scratch.

By default, this recipe will use the eggs defined at the ``buildout`` section
called ``eggs``, but that can be overriden locally. It generates these scripts:

``python``
  A pre-configured python interpreter taking into consideration all eggs and
  development packages on your recipe.

``gdb-python`` or ``lldb-python``
  A pre-configured python interpreter, prefixed with ``gdb`` (or ``lldb`` on a
  MacOS system) to make debugging easier. Use it like you use ``python``.

``nosetests``
  A test runner called ``nosetests`` will be created on the bin directory of
  buildout.

``coverage``
  A test coverage application called ``coverage`` will be created on the
  ``bin`` directory of buildout.

``sphinx-build`` and friends
  Several sphinx utilities will be created on the bin directory of buildout.

Other package scripts
  Package scripts will be created taking into account the ``prefixes``
  established for this section or globally (as a second priority).


Supported recipe options
========================

The ``scripts`` recipe supports the following options (mostly for experts -
read don't use them unless you know what you're doing):

``prefixes``
  Overrides or sets the list of prefixes in ``buildout.prefixes``.  If not
  given, the value of this property defaults to ``buildout.prefixes``. Both can
  be empty, which makes this recipe default to using standard available paths.

``eggs``
  The eggs option specifies a list of eggs to use for **building** the scripts
  of this recipe. Each string must be given on a separate line. If not given,
  the value of this property defaults to ``buildout.eggs``.

``dependent-scripts``
  If set to the string ``true``, scripts will be generated for all required
  eggs in addition to the eggs specifically named. By default, it is ``false``
  to avoid the clutter it may cause on very high-level packages, with numerous
  dependencies exporting scripts.

``interpreter``
  The name of a script to generate that allows access to a Python interpreter
  that has the path set based on the eggs installed. If you don't specify
  anything, the default value ``python`` will be used.

``extra-paths``
  Extra paths to be appended in a generated script. To prepend, use the
  ``prefixes`` entry.

``nose-flags``
  These are extra flags that are **appended** to the given ``nosetests``
  command line, automatically. Use this to preset arguments you like running
  all the time like ``-v``, for example.


.. include:: links.rst
