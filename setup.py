#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 13 Aug 2012 09:49:00 CEST

from setuptools import setup, find_packages

setup(
    name='xbob.buildout',
    version='0.3.6',
    description="zc.buildout recipes to perform a variety of tasks required by Bob satellite packages",
    keywords=['buildout', 'sphinx', 'nose', 'recipe', 'eggs', 'bob'],
    url='http://github.com/bioidiap/xbob.buildout',
    license='GPLv3',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    namespace_packages = [
      'xbob',
    ],

    entry_points = {
      'zc.buildout': [
        'develop = xbob.buildout.develop:Recipe',
        'scripts = xbob.buildout.scripts:Recipe',
        'python = xbob.buildout.scripts:PythonInterpreter',
        'gdb-python = xbob.buildout.scripts:GdbPythonInterpreter',
        'ipython = xbob.buildout.scripts:IPythonInterpreter',
        'nose = xbob.buildout.scripts:NoseTests',
        'sphinx = xbob.buildout.scripts:Sphinx',
        'egg.scripts = xbob.buildout.scripts:UserScripts',
        ],
      },

    install_requires=[
      'setuptools',
      'zc.recipe.egg',
      ],

    classifiers=[
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
