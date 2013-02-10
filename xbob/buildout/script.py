#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon  4 Feb 14:12:24 2013 

"""Builds custom scripts with the right paths for external dependencies
installed on different prefixes.
"""

import os
import sys
import logging
from . import tools

from zc.buildout.buildout import bool_option
import zc.buildout.easy_install
from zc.recipe.egg import Scripts
#from z3c.recipe.scripts import Scripts #does not work as expected...

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

class Recipe(Scripts):
  """Just creates a given script with the "correct" paths
  """

  def __init__(self, buildout, name, options):

    self.buildout = buildout
    self.name = name
    self.options = options

    self.logger = logging.getLogger(self.name)

    # Preprocess some variables
    self.newest = bool_option(buildout['buildout'], 'newest')
    self.offline = bool_option(buildout['buildout'], 'offline')
    self.options['bin-directory'] = buildout['buildout']['bin-directory']

    # This defines which paths should be prepended to the path search. The
    # order is always respected
    self.user_paths = tools.parse_list(options.get('user-paths', ''))

    # Tries to get personalized eggs list or use the one from the buildout
    self.eggs = tools.parse_list(options.get('eggs', ''))
    if not self.eggs:
      self.eggs = tools.parse_list(buildout['buildout'].get('eggs', ''))

    # Shall we panic or ignore if we cannot find all eggs?
    self.panic = options.get('error-on-failure', 'true').lower() == 'true'

    # initializes the script infrastructure
    super(Recipe, self).__init__(buildout, name, options)

  def working_set(self, extra=()):
    """Separate method to just get the working set - overriding zc.recipe.egg

    This is intended for reuse by similar recipes.
    """

    options = self.options
    b_options = self.buildout['buildout']

    distributions = self.eggs + list(extra)

    # Backward compat. :(
    options['executable'] = sys.executable

    try:

      if self.offline:

        # In this case, we just check if the distributions that are required,
        # are available locally

        paths = self.user_paths + [
            b_options['egg-directory'],
            b_options['develop-egg-directory'],
            ]

        # Checks each distribution individually, to avoid that easy_install
        # summarizes the output directories and get us with a directory set
        # which already contains dependencies that should be taken from
        # 'prefixes' instead!

        ws = None
        for d in distributions:
          tws = zc.buildout.easy_install.working_set([d], paths)
          if ws is None: 
            ws = tws
          else: 
            for k in tws: ws.add(k)

      else:

        # In this case we first check locally. If distributions are installed
        # locally and are up-to-date (newest is 'true'), then nothing is
        # downloaded. If not, required distributions are updated respecting the
        # flag 'prefer-final', naturally.

        paths = self.user_paths + [
            options['develop-eggs-directory'],
            ]

        # Checks each distribution individually, to avoid that easy_install
        # summarizes the output directories and get us with a directory set
        # which already contains dependencies that should be taken from
        # 'prefixes' instead!

        ws = None
        for d in distributions:
          tws = zc.buildout.easy_install.install([d,], 
              options['eggs-directory'], links=self.links, index=self.index,
              path=paths, newest=self.newest, allow_hosts=self.allow_hosts)

          if ws is None: 
            ws = tws
          else: 
            for k in tws: ws.add(k)

    except zc.buildout.easy_install.MissingDistribution, e:
      if self.panic: 
        raise
      else:
        self.logger.info('Discarding entry-points for section "%s": %s' % \
            (self.name, e))

    return self.eggs, ws

  def install(self):
    return tuple(super(Recipe, self).install())

  update = install
