#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon  4 Feb 14:12:24 2013

"""Builds custom interpreters with the right paths for external Bob
"""

import os
import logging
import pkg_resources
import zc.buildout
from . import tools
from .script import Recipe as Script
from .python import Recipe as PythonInterpreter
from .gdbpy import Recipe as GdbPythonInterpreter
from .envwrapper import EnvironmentWrapper

def version_is_lessthan(name, version):
  """Checks if the version of a package is at least..."""

  if not is_available(name): return False
  else:
    from distutils.version import LooseVersion
    return LooseVersion(pkg_resources.require(name)[0].version) < version

class UserScripts(Script):
  """Installs all user scripts from the eggs"""

  def __init__(self, buildout, name, options):

    self.logger = logging.getLogger(name)

    if 'interpreter' in options: del options['interpreter']
    if 'scripts' in options: del options['scripts']
    Script.__init__(self, buildout, name, options)

  def install(self):

    return Script.install(self)

  update = install

class IPythonInterpreter(Script):
  """Installs all user scripts from the eggs"""

  def __init__(self, buildout, name, options):

    self.name = name
    self.buildout = buildout
    self.logger = logging.getLogger(name)
    self.options = options
    self.egglist = options.get('eggs', buildout['buildout']['eggs'])

    # adds ipython interpreter into the mix
    interpreter = self.options.setdefault('interpreter', 'python')
    del self.options['interpreter']
    self.options['entry-points'] = 'i%s=IPython.frontend.terminal.ipapp:launch_new_instance' % interpreter
    self.options['scripts'] = 'i%s' % interpreter
    self.options['dependent-scripts'] = 'false'
    self.options.setdefault('panic', 'false')
    self.options['eggs'] = tools.add_eggs(self.egglist, ['ipython'])

    # initializes base class
    Script.__init__(self, self.buildout, self.name, self.options)

  def install(self):

    return Script.install(self)

  update = install

class PyLint(Script):
  """Installs PyLint infrastructure"""

  def __init__(self, buildout, name, options):

    self.logger = logging.getLogger(name)

    # Initializes nosetests, if it is available - don't panic!
    if 'interpreter' in options: del options['interpreter']
    if 'pylint-flags' in options:
      if version_is_lessthan('pylint', '1.0'):
        # use 'options' instead of 'self.options' to force use
        flags = tools.parse_list(options['pylint-flags'])
        init_code = ['sys.argv.append(%r)' % k for k in flags]
        options['initialization'] = '\n'.join(init_code)
      else:
        self.logger.warn('the option pylint-flags for this recipe is only available for older versions of pylint < 1.0')
    options['entry-points'] = 'pylint=pylint.lint:Run'
    options['arguments'] = 'sys.argv[1:]'
    options['scripts'] = 'pylint'
    options['dependent-scripts'] = 'false'
    options.setdefault('panic', 'false')
    eggs = options.get('eggs', buildout['buildout']['eggs'])
    options['eggs'] = tools.add_eggs(eggs, ['pylint'])
    Script.__init__(self, buildout, name, options)

  def install(self):

    return Script.install(self)

  update = install

class NoseTests(Script):
  """Installs Nose infrastructure"""

  def __init__(self, buildout, name, options):

    self.logger = logging.getLogger(name)

    # Initializes nosetests, if it is available - don't panic!
    if 'interpreter' in options: del options['interpreter']
    if 'nose-flags' in options:
      # use 'options' instead of 'options' to force use
      flags = tools.parse_list(options['nose-flags'])
      init_code = ['sys.argv.append(%r)' % k for k in flags]
      options['initialization'] = '\n'.join(init_code)
    options['entry-points'] = 'nosetests=nose:run_exit'
    options['scripts'] = 'nosetests'
    options['dependent-scripts'] = 'false'
    options.setdefault('panic', 'false')
    eggs = options.get('eggs', buildout['buildout']['eggs'])
    options['eggs'] = tools.add_eggs(eggs, ['nose'])
    Script.__init__(self, buildout, name, options)

  def install(self):

    return Script.install(self)

  update = install

class Coverage(Script):
  """Installs Coverage infrastructure"""

  def __init__(self, buildout, name, options):

    self.logger = logging.getLogger(name)

    # Initializes nosetests, if it is available - don't panic!
    if 'interpreter' in options: del options['interpreter']
    if 'coverage-flags' in options:
      # use 'options' instead of 'options' to force use
      flags = tools.parse_list(options['coverage-flags'])
      init_code = ['sys.argv.append(%r)' % k for k in flags]
      options['initialization'] = '\n'.join(init_code)
    options['entry-points'] = 'coverage=coverage:main'
    options['scripts'] = 'coverage'
    options['dependent-scripts'] = 'false'
    options.setdefault('panic', 'false')
    eggs = options.get('eggs', buildout['buildout']['eggs'])
    options['eggs'] = tools.add_eggs(eggs, ['coverage'])
    Script.__init__(self, buildout, name, options)

  def install(self):

    return Script.install(self)

  update = install

class Sphinx(Script):
  """Installs the Sphinx documentation generation infrastructure"""

  def __init__(self, buildout, name, options):

    self.logger = logging.getLogger(name)

    # Initializes the sphinx document generator - don't panic!
    if 'interpreter' in options: del options['interpreter']
    options['scripts'] = '\n'.join([
      'sphinx-build',
      'sphinx-apidoc',
      'sphinx-autogen',
      'sphinx-quickstart',
      ])
    options['entry-points'] = '\n'.join([
      'sphinx-build=sphinx:main',
      'sphinx-apidoc=sphinx.apidoc:main',
      'sphinx-autogen=sphinx.ext.autosummary.generate:main',
      'sphinx-quickstart=sphinx.quickstart:main',
      ])
    options.setdefault('panic', 'false')
    options['dependent-scripts'] = 'false'
    eggs = options.get('eggs', buildout['buildout']['eggs'])
    options['eggs'] = tools.add_eggs(eggs, ['sphinx', 'sphinx-pypi-upload'])
    Script.__init__(self, buildout, name, options)

  def install(self):

    return Script.install(self)

  update = install

class Recipe(object):
  """Just creates a given script with the "correct" paths
  """

  def __init__(self, buildout, name, options):

    self.logger = logging.getLogger(name.capitalize())

    # Gets a personalized prefixes list or the one from buildout
    prefixes = tools.parse_list(options.get('prefixes', ''))
    if not prefixes:
      prefixes = tools.parse_list(buildout['buildout'].get('prefixes', ''))
    prefixes = [os.path.abspath(k) for k in prefixes if os.path.exists(k)]

    # Builds an environment wrapper, in case dependent packages need to be
    # compiled
    self.envwrapper = EnvironmentWrapper(self.logger,
          zc.buildout.buildout.bool_option(options, 'debug', 'false'), prefixes)

    # Touch the options
    self.dependent_scripts = options.get('dependent-scripts')

    self.python = PythonInterpreter(buildout, 'Python', options.copy())
    self.gdbpy = GdbPythonInterpreter(buildout, 'GdbPython', options.copy())
    self.scripts = UserScripts(buildout, 'Scripts', options.copy())
    self.nose = NoseTests(buildout, 'Nose', options.copy())
    self.coverage = Coverage(buildout, 'Coverage', options.copy())
    self.sphinx = Sphinx(buildout, 'Sphinx', options.copy())

  def install(self):
    self.envwrapper.set()
    retval = \
        self.python.install_on_wrapped_env() + \
        self.gdbpy.install_on_wrapped_env() + \
        self.scripts.install_on_wrapped_env() + \
        self.nose.install_on_wrapped_env() + \
        self.coverage.install_on_wrapped_env() + \
        self.sphinx.install_on_wrapped_env()
    self.envwrapper.unset()
    return retval

  update = install
