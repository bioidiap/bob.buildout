#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon  4 Feb 09:24:35 2013 CET

"""A wrapper for defining environment variables for the compilation
"""

import os
import logging
from . import tools

class EnvironmentWrapper(object):
  """Provides methods for wrapping other install() methods with environment
  settings from initialization.
  """

  def __init__(self, logger, debug, prefixes):

    self.debug = debug
    self.logger = logger

    # set the pkg-config paths to look at
    pkgcfg = [os.path.join(k, 'lib', 'pkgconfig') for k in prefixes]
    pkgcfg += [os.path.join(k, 'lib64', 'pkgconfig') for k in prefixes]
    pkgcfg += [os.path.join(k, 'lib32', 'pkgconfig') for k in prefixes]
    self.pkgcfg = [os.path.abspath(k) for k in pkgcfg if os.path.exists(k)]

  def set(self):
    """Sets the current environment for variables needed for the setup of the
    package to be compiled"""

    self._saved_environment = {}

    if self.pkgcfg:

      self._saved_environment['PKG_CONFIG_PATH'] = os.environ.get('PKG_CONFIG_PATH', None)

      tools.prepend_env_paths('PKG_CONFIG_PATH', self.pkgcfg)
      for k in reversed(self.pkgcfg):
        self.logger.info("Adding pkg-config path '%s'" % k)

      self.logger.debug('PKG_CONFIG_PATH=%s' % os.environ['PKG_CONFIG_PATH'])

    if 'CFLAGS' in os.environ:
      self._saved_environment['CFLAGS'] = os.environ['CFLAGS']
    else:
      self._saved_environment['CFLAGS'] = None

    if self.debug:
      # Disables optimization, enable debug symbols
      cflags = '-O0 -g'
      cxxflags = '-O0 -g'
      self.logger.info("Setting debug build options")

    else:
      # Disables debug symbols, enable extra optimizations
      cflags = '-O3 -g0'
      cxxflags = cflags
      self.logger.info("Setting release build options")

    # Disables optimization options for setuptools/distribute
    if 'CFLAGS' in os.environ: os.environ['CFLAGS'] += ' ' + cflags
    else: os.environ['CFLAGS'] = cflags
    self.logger.debug('CFLAGS=%s' % os.environ['CFLAGS'])

    if 'CXXFLAGS' in os.environ: os.environ['CXXFLAGS'] += ' ' + cxxflags
    else: os.environ['CXXFLAGS'] = cxxflags
    self.logger.debug('CXXFLAGS=%s' % os.environ['CXXFLAGS'])

  def unset(self):
    """Resets the environment back to its previous state"""

    for key in self._saved_environment:
      if self._saved_environment[key] is None:
        try:
          del os.environ[key]
        except KeyError:
          pass
      else:
        os.environ[key] = self._saved_environment[key]
