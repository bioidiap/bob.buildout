#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 13 Aug 2012 09:49:00 CEST

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

setup(
    name='bob.buildout',
    version=version,
    description="zc.buildout recipes to perform a variety of tasks required by Bob satellite packages",
    keywords=['buildout', 'sphinx', 'nose', 'recipe', 'eggs', 'bob'],
    url='http://github.com/bioidiap/bob.buildout',
    license='GPLv3',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,



    entry_points = {
      'zc.buildout': [
        'develop = bob.buildout.develop:Recipe',
        'scripts = bob.buildout.scripts:Recipe',
        'python = bob.buildout.scripts:PythonInterpreter',
        'gdb-python = bob.buildout.scripts:GdbPythonInterpreter',
        'ipython = bob.buildout.scripts:IPythonInterpreter',
        'pylint = bob.buildout.scripts:PyLint',
        'nose = bob.buildout.scripts:NoseTests',
        'coverage = bob.buildout.scripts:Coverage',
        'sphinx = bob.buildout.scripts:Sphinx',
        'egg.scripts = bob.buildout.scripts:UserScripts',
        ],
      'zc.buildout.extension': [
        'extension = bob.buildout.extension:extension',
        ],
      },

    install_requires=[
      'setuptools',
      'zc.recipe.egg',
      'six',
      ],

    classifiers=[
      'Framework :: Bob',
      'Development Status :: 4 - Beta',
      'Environment :: Plugins',
      'Framework :: Buildout :: Recipe',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Topic :: Software Development :: Build Tools',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      ],

    )
