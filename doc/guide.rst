.. bob.buildout.guide:

=========================================
 Local development of |project| packages
=========================================

Very often, developers of |project| packages are confronted with the need to
clone repositories locally and develop installation/build and runtime code.
While it is possible to use conda_ for such, the use of `zc.buildout`_ offers
an quick and easy alternative to achieve this. It allows the creation of
isolated, directory-based python development environments that can be modulated
based on the development needs of the current package(s) one needs to work on. 

The steps involved in creating a development environment are the following:

1. Checkout from gitlab_ the package the user wants to develop
2. Create a conda installation containing base packages that the current
   package being developed requires
3. *Optionally*, create a buildout configuration that allows the
   cross-development of packages
4. Run the application ``buildout`` to set-up the desired development
   environment

Some of these steps can be automated. ``bob.devtools`` is a Bob_ package that helps with setting up the proper environment. A detailed guide for performing the mentioned steps using ``buildout`` and ``bob.devtools`` is available in `bob development tools`_.

.. include:: links.rst