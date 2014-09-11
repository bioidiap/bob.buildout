#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon  4 Feb 14:12:24 2013

"""Builds custom scripts with the right paths for external dependencies
installed on different prefixes.
"""

import sys
import logging
from . import tools
from .envwrapper import EnvironmentWrapper

import zc.buildout.easy_install
from zc.recipe.egg import Scripts

# Fixes python script template
zc.buildout.easy_install.py_script_template = \
    zc.buildout.easy_install.py_script_template.replace(
    """__import__("code").interact(banner="", local=globals())""",
    """
    import os
    if os.environ.has_key('PYTHONSTARTUP') and os.environ['PYTHONSTARTUP']:
      execfile(os.environ['PYTHONSTARTUP'])
    __import__('code').interact(banner=('Python ' + sys.version + ' on ' + sys.platform + '\\nType "help", "copyright", "credits" or "license" for more information.'), local=globals())
  """)

# Fixes buildout search path for external packages
if hasattr(zc.buildout.easy_install, 'buildout_and_distribute_path'):
  zc.buildout.easy_install.buildout_and_distribute_path += sys.path
else:
  zc.buildout.easy_install.buildout_and_setuptools_path += sys.path

class Recipe(Scripts):
  """Just creates a given script with the "correct" paths
  """

  def __init__(self, buildout, name, options):

    self.buildout = buildout
    self.name = name
    self.options = options

    self.logger = logging.getLogger(self.name)

    # Preprocess some variables
    self.options['bin-directory'] = buildout['buildout']['bin-directory']

    # Gets a personalized eggs list or the one from buildout
    self.eggs = tools.eggs(buildout['buildout'], options, name)

    # Gets a personalized prefixes list or the one from buildout
    self.prefixes = tools.get_prefixes(buildout['buildout'])
    self.user_paths = tools.find_site_packages(self.prefixes)

    # Builds an environment wrapper, in case dependent packages need to be
    # compiled
    self.envwrapper = EnvironmentWrapper(self.logger,
        tools.debug(buildout['buildout']), self.prefixes)

    # initializes the script infrastructure
    super(Recipe, self).__init__(buildout, name, options)

  def working_set(self, extra=()):
    """Separate method to just get the working set - overriding zc.recipe.egg

    This is intended for reuse by similar recipes.
    """

    distributions = self.eggs + list(extra)

    if tools.offline(self.buildout['buildout']):

      ws = tools.working_set(self.buildout['buildout'], self.prefixes)
      ws = tools.filter_working_set_hard(ws, distributions)

    else:

      ws = tools.working_set(self.buildout['buildout'], self.prefixes)

      if tools.newest(self.buildout['buildout']):
        to_install = distributions
      else: #only installs packages which are not yet installed
        ws, to_install = tools.filter_working_set_soft(ws, distributions)

      for d in to_install: tools.install_package(self.buildout['buildout'], d, ws)

    return self.eggs, ws

  def install_on_wrapped_env(self):
    return tuple(super(Recipe, self).install())

  def install(self):
    self.envwrapper.set()
    retval = self.install_on_wrapped_env()
    self.envwrapper.unset()
    return retval

  update = install
