#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 13 Aug 2012 09:49:00 CEST 

from setuptools import setup, find_packages

setup(
    name='bob.buildout.recipes',
    version='0.1',
    description="zc.buildout recipes to perform a variety of tasks required by Bob satellite packages",
    keywords=['buildout', 'sphinx', 'nose', 'recipe', 'eggs'],
    url='http://github.com/bioidiap/bob.buildout.recipes',
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
        'external = bob_buildout.external:Recipe',
        'sphinx = bob_buildout.sphx:Recipe',
        'nose = bob_buildout.nose:Recipe',
        ],
      },

    install_requires=[
      'Sphinx >= 1.0',
      'nose',
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
      ],

    )
