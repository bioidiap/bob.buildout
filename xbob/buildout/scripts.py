#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon  4 Feb 14:12:24 2013

"""Builds custom interpreters with the right paths for external Bob
"""

import os
import logging
import zc.buildout
from . import tools
from .script import Recipe as Script
from .python import Recipe as PythonInterpreter
from .gdbpy import Recipe as GdbPythonInterpreter
from .envwrapper import EnvironmentWrapper

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

    self.logger = logging.getLogger(name)

    interpreter = options.setdefault('interpreter', 'python')
    del options['interpreter']
    options['entry-points'] = 'i%s=IPython.frontend.terminal.ipapp:launch_new_instance' % interpreter
    options['scripts'] = 'i%s' % interpreter
    options['dependent-scripts'] = 'false'
    options.setdefault('panic', 'false')
    eggs = options.get('eggs', buildout['buildout']['eggs'])
    options['eggs'] = tools.add_eggs(eggs, ['nose', 'coverage'])
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
    options['eggs'] = tools.add_eggs(eggs, ['nose', 'coverage'])
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
    if 'entry-points' in options: del options['entry-points']
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
    self.ipython = IPythonInterpreter(buildout, 'IPython', options.copy())
    self.nose = NoseTests(buildout, 'Nose', options.copy())
    self.sphinx = Sphinx(buildout, 'Sphinx', options.copy())

  def install(self):
    self.envwrapper.set()
    retval = \
        self.python.install_on_wrapped_env() + \
        self.gdbpy.install_on_wrapped_env() + \
        self.scripts.install_on_wrapped_env() + \
        self.ipython.install_on_wrapped_env() + \
        self.nose.install_on_wrapped_env() + \
        self.sphinx.install_on_wrapped_env()
    self.envwrapper.unset()
    return retval

  update = install
