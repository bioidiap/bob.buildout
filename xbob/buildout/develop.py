#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon  4 Feb 09:24:35 2013 CET

"""Compiles a Python/C++ egg extension for Bob
"""

import os
import logging
import zc.buildout.easy_install
from zc.recipe.egg.egg import Scripts

from .tools import *

class Recipe(Scripts):
  """Compiles a Python/C++ egg extension for Bob
  """

  def __init__(self, buildout, name, options):

    self.name, self.options = name, options
    self.logger = logging.getLogger(self.name)
    self.buildout = buildout

    # configures the interpreter that will compile the package
    options['interpreter'] = 'xbob.builder.py'
    options['setup'] = options.get('setup', '.')

    eggs = parse_list(options.get('eggs', ''))
    if 'xbob.extension' not in eggs: eggs.append('xbob.extension')
    options['eggs'] = '\n'.join(eggs)

    Scripts.__init__(self, buildout, name, options)

    # finds the setup script
    options['setup'] = os.path.join(buildout['buildout']['directory'],
                                    options['setup'])

    # configures the prefixes that will be used for PKG_CONFIG_PATH
    self.prefixes = parse_list(buildout['buildout'].get('prefixes', ''))
    self.prefixes = [os.path.abspath(k) for k in self.prefixes if os.path.exists(k)]
   
    # where to put the compiled egg
    self.buildout_eggdir = buildout['buildout'].get('develop-eggs-directory')

  def _set_environment(self):
    """Sets the current environment for variables needed for the setup of the
    package to be compiled"""

    self._saved_environment = {}

    if self.prefixes:

      # Allows compilation of Boost.Python bindings
      pkgcfg = [os.path.join(k, 'lib', 'pkgconfig') for k in self.prefixes]
      pkgcfg = [k for k in pkgcfg if os.path.exists(k)]

      self._saved_environment['PKG_CONFIG_PATH'] = os.environ.get('PKG_CONFIG_PATH', None)

      prepend_env_paths('PKG_CONFIG_PATH', pkgcfg)
      self.logger.debug('PKG_CONFIG_PATH=%s' % os.environ['PKG_CONFIG_PATH'])
      for k in reversed(pkgcfg):
        self.logger.debug("Prepending pkg-config path %s" % k)

  def _restore_environment(self):
    """Resets the environment back to its previous state"""

    for key in self._saved_environment:
      if self._saved_environment[key] is None:
        try:
          del os.environ[key]
        except KeyError:
          pass
      else:
        os.environ[key] = self._saved_environment[key]
        del self._saved_environment[key]

  def install(self):
    """This is the method that buildout will actually call for installation"""

    scripts = Scripts.install(self) # script + egg installation

    # this will build the package
    self._set_environment()
    package = zc.buildout.easy_install.develop(
        setup=self.options['setup'], 
        dest=self.buildout_eggdir,
        executable=scripts[0],
        )
    self._restore_environment()

    return scripts + [package]

  update = install
