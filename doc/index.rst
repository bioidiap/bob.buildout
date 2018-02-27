.. vim: set fileencoding=utf-8 :
.. Mon 17 Mar 09:23:45 2014 CET

.. _bob.buildout:

==============
 Bob Buildout
==============

This package includes an extension and a recipe to make it easy to create
local, directory-based complete development environments for |project|
packages. While |project| packages are distributed as conda-based installable
packages, the use of zc.buildout_ may greaty shorten development cycles as it
avoids the conda-build step, which can be somewhat lengthy (e.g. for packages
with C/C++ bindings).

zc.buildout_, unlike conda_, can *not* handle non-python-based packages. It is
therefore a tool to quickly create deployments or test changes on
**python-based distributable packages**. It follows that, in order to use
zc.buildout_, packages *need* to be python-based packages. Luckily, most of
|project| packages fit in this category, besides also being conda_ packages, so
zc.buildout_ can be used for development purposes in this context. Although
zc.buildout_ supports deployment, it is currently **not** used for this purpose
in the context of |project|. Our dependence list goes beyond Python-only
packages (e.g. ffmpeg or blitz++) and a full-stack software deployment cannot
be easily achieved relying only on this python development tool.

zc.buildout_ uses Python setuptools_ to create a directory structure that
contains scripts and dependencies which can defined in a *buildout recipe*.
Once a buildout recipe is interpreted, zc.buildout_ will make sure all listed
dependencies are satisfied and automatically instantiate scripts with changed
load paths that take in consideration all python packages. In order to satistfy
dependencies, zc.buildout_ may download missing python-based packages from
PyPI_, the Python Package Index. In the context of |project|-based package
development, we seldomly use this feature though.

Because zc.buildout_ is used for |project| package development since quite
sometime, most packages in the |project| ecosystem include a file called
``buildout.cfg`` that can be used by zc.buildout_ to build a quick,
*throw-away* development environment for the current package. A common
misconception is that one must checkout a |project| package in order to run
buildout. That is **not** true.  zc.buildout_ is an independent development
tool that just deployes a python-based software stack based on a *recipe*. If
the *recipe* mentions the code of a package on the current directory, the setup
will include this. If it doesn't, then it won't. We typically don't use
zc.buildout_ to create deployments for |project| packages - we normally defer
this task to conda_ as it can handle non-pythonic dependencies in a much better
and uniform way. That said, it is possible to create python-only based
deployments using zc.buildout_ *without* being necessarily in the root
directory of a |project| package.

This document explains how to use zc.buildout_ and ``bob.buildout``'s recipe
and extension to construct development environments for your |project|
packages.


Documentation
-------------

.. toctree::
   :maxdepth: 2

   guide
   buildout
   development
   py_api


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. include:: links.rst
