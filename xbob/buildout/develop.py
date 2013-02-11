#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon  4 Feb 09:24:35 2013 CET

"""Compiles a Python/C++ egg extension for Bob
"""

import os
import sys
import stat
import shutil
import tempfile
import logging
from . import tools
from .script import Recipe as Script
import zc.buildout.easy_install

class Recipe(object):
  """Compiles a Python/C++ egg extension for Bob
  """

  def __init__(self, buildout, name, options):

    self.name, self.options = name, options
    self.logger = logging.getLogger(self.name)
    self.buildout = buildout

    # finds the setup script or use the default
    options['setup'] = os.path.join(buildout['buildout']['directory'],
        options.get('setup', '.'))

    # calculates required eggs - parse setup file?
    eggs = tools.parse_list(options.get('eggs', ''))
    if 'xbob.extension' not in eggs: eggs.append('xbob.extension')

    # Initializes interpreter
    builder_options = zc.buildout.buildout.Options(buildout, name + '+xbuilder',
        options.copy())
    builder_options['interpreter'] = 'xbuilder'
    builder_options['dependent-scripts'] = 'false'
    builder_options['eggs'] = '\n'.join(eggs)
    self.xbuilder = Script(buildout, name+'xbuilder', builder_options)

    # gets a personalized prefixes list or the one from buildout
    prefixes = tools.parse_list(options.get('prefixes', ''))
    if not prefixes:
      prefixes = tools.parse_list(buildout['buildout'].get('prefixes', ''))

    # set the pkg-config paths to look at
    pkgcfg = [os.path.join(k, 'lib', 'pkgconfig') for k in prefixes]
    self.pkgcfg = [os.path.abspath(k) for k in pkgcfg if os.path.exists(k)]

    # where to put the compiled egg
    self.buildout_eggdir = buildout['buildout'].get('develop-eggs-directory')

  def _set_environment(self):
    """Sets the current environment for variables needed for the setup of the
    package to be compiled"""

    self._saved_environment = {}

    if self.pkgcfg:

      self._saved_environment['PKG_CONFIG_PATH'] = os.environ.get('PKG_CONFIG_PATH', None)

      tools.prepend_env_paths('PKG_CONFIG_PATH', self.pkgcfg)
      self.logger.debug('PKG_CONFIG_PATH=%s' % os.environ['PKG_CONFIG_PATH'])
      for k in reversed(self.pkgcfg):
        self.logger.info("Adding pkg-config path '%s'" % k)

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

  # a modified copy of zc.buildout.easy_install.develop
  def install(self):

    setup = self.options['setup']
    dest=self.buildout_eggdir

    if os.path.isdir(setup):
      directory = setup
      setup = os.path.join(directory, 'setup.py')
    else:
      directory = os.path.dirname(setup)

    undo = []
    try:

      # creates the script that is able to install the package
      xbuilder = self.xbuilder.install()

      fd, tsetup = tempfile.mkstemp()
      undo.append(lambda: os.remove(tsetup))
      undo.append(lambda: os.close(fd))

      os.write(fd, (zc.buildout.easy_install.runsetup_template % dict(
          distribute=zc.buildout.easy_install.distribute_loc,
          setupdir=directory,
          setup=setup,
          __file__ = setup,
          )).encode())

      tmp3 = tempfile.mkdtemp('build', dir=dest)
      undo.append(lambda : shutil.rmtree(tmp3))

      args = [xbuilder[0],  tsetup, '-q', 'develop', '-mxN', '-d', tmp3]

      log_level = self.logger.getEffectiveLevel()
      if log_level <= 0:
        if log_level == 0:
          del args[2]
        else:
          args[2] == '-v'
      if log_level < logging.DEBUG:
        self.logger.debug("in: %r\n%s", directory, ' '.join(args))

      self._set_environment()
      zc.buildout.easy_install.call_subprocess(args)
      self._restore_environment()

      return xbuilder + (zc.buildout.easy_install._copyeggs(tmp3, dest, '.egg-link', undo),)

    finally:
      undo.reverse()
      [f() for f in undo]

  update = install
