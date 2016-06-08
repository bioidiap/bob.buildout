#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon  4 Feb 09:24:35 2013 CET

"""A wrapper for defining environment variables for the compilation
"""

import os
import string
import logging
import platform


def substitute(value, d):
  """Substitutes ${} expressions on ``value`` with values from ``d``, using
  string.Template"""

  return string.Template(value).substitute(**d)

class EnvironmentWrapper(object):
  """Provides methods for wrapping other install() methods with environment
  settings from initialization.
  """

  DEBUG_FLAGS = '-O0 -g -DBOB_DEBUG'
  RELEASE_FLAGS = '-O3 -g0 -DNDEBUG -mtune=native'
  # Note: CLang does not work well with BZ_DEBUG\n
  if platform.system() != 'Darwin':
    DEBUG_FLAGS += " -DBZ_DEBUG"

  def __init__(self, logger, debug=None, prefixes=None, environ=None):

    self.debug = debug
    self.environ = dict(environ) if environ else {}

    # do environment variable substitution on user dictionary
    for key in self.environ:
      self.environ[key] = substitute(self.environ[key], self.environ)

    # if PKG_CONFIG_PATH is set on self.environ, then prefix it
    pkgcfg = []
    if 'PKG_CONFIG_PATH' in self.environ:
      pkgcfg += self.environ['PKG_CONFIG_PATH'].split(os.pathsep)

    # set the pkg-config paths to look at, environment settings in front
    prefixes = prefixes if prefixes else []
    if 'BOB_PREFIX_PATH' in self.environ:
      prefixes = self.environ['BOB_PREFIX_PATH'].split(os.pathsep) + prefixes
    pkgcfg += [os.path.join(k, 'lib', 'pkgconfig') for k in prefixes]
    pkgcfg += [os.path.join(k, 'lib64', 'pkgconfig') for k in prefixes]
    pkgcfg += [os.path.join(k, 'lib32', 'pkgconfig') for k in prefixes]

    # joins all paths
    if prefixes:
      self.environ['BOB_PREFIX_PATH'] = os.pathsep.join(prefixes)
    if pkgcfg:
      self.environ['PKG_CONFIG_PATH'] = os.pathsep.join(pkgcfg)

    # reset the CFLAGS and CXXFLAGS depending on the user input
    cflags = None
    if self.debug is True: cflags = str(EnvironmentWrapper.DEBUG_FLAGS)
    elif self.debug is False: cflags = str(EnvironmentWrapper.RELEASE_FLAGS)
    # else: pass

    if cflags:
      self.environ['CFLAGS'] = cflags + ' ' + \
          self.environ.get('CFLAGS', '') + os.environ.get('CFLAGS', '')
      self.environ['CFLAGS'] = self.environ['CFLAGS'].strip() #clean-up
      self.environ['CXXFLAGS'] = cflags + ' ' + \
          self.environ.get('CXXFLAGS', '') + os.environ.get('CXXFLAGS', '')
      self.environ['CXXFLAGS'] = self.environ['CXXFLAGS'].strip() #clean-up


  def set(self):
    """Sets the current environment for variables needed for the setup of the
    package to be compiled"""

    self._saved_environment = dict(os.environ) #copy
    os.environ.update(self.environ)

  def unset(self):
    """Resets the environment back to its previous state"""

    # cleanup
    if self._saved_environment:
      os.environ = self._saved_environment
      self._saved_environment = {}

  def __enter__(self):
    self.set()

  def __exit__(self, *exc_details):
    self.unset()
