#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Tue 17 Apr 19:16:46 2012 

"""A simple recipe to enable nose to search and execute our tests.
"""

import os
import sys
import logging
import pkg_resources
import zc.buildout.easy_install
import zc.recipe.egg

from .tools import *

INITIALIZATION_TEMPLATE = """\
import os

sys.argv[0] = os.path.abspath(sys.argv[0])
os.chdir(%r)
"""

ENV_TEMPLATE = """os.environ['%s'] = %r
"""

class Recipe(object):

  def __init__(self, buildout, name, options):
    
    self.buildout = buildout
    self.name = name
    self.options = options
    
    self.logger = logging.getLogger(self.name)
    
    self.logger.debug("Initializing '%s'" % self.name)

    options['script'] = os.path.join(buildout['buildout']['bin-directory'],
                     options.get('script', self.name),
                     )

    wd = options.get('working-directory', '').strip()
    if wd == '':
      options['location'] = os.path.join(
        buildout['buildout']['parts-directory'], name)

    self.eggs = parse_list(options.get('eggs', ''))

    if 'nose' not in self.eggs: self.eggs.append('nose')

    options['eggs'] = '\n'.join(self.eggs)
    self.egg = zc.recipe.egg.Egg(buildout, name, options)

  def install(self):
    '''Installation routine'''

    eggs, ws = self.egg.working_set()

    defaults = self.options.get('defaults', '').strip()
    if defaults:
      defaults = ['nose'] + defaults.split()
      defaults = "argv=%s+sys.argv[1:]" % defaults
    else:
      defaults = "argv=['nose']+sys.argv[1:]"

    wd = self.options.get('working-directory', '').strip()
    if wd != '':
      if os.path.exists(wd):
        assert os.path.isdir(wd)
      else:
        os.mkdir(wd)
      initialization = INITIALIZATION_TEMPLATE % wd
    else:
      initialization = ''

    env_section = self.options.get('environment', '').strip()
    if env_section:
      env = self.buildout[env_section]
      for key, value in env.items():
        initialization += ENV_TEMPLATE % (key, value)
      initialization = 'import os\n%s' % initialization

    initialization_section = self.options.get('initialization', '').strip()
    if initialization_section:
      initialization += initialization_section

    script = zc.buildout.easy_install.scripts(
        reqs=[(self.options['script'], 'nose', 'main')],
        working_set=ws,
        executable=self.options['executable'],
        dest=self.buildout['buildout']['bin-directory'],
        extra_paths=self.egg.extra_paths,
        arguments = defaults,
        initialization = initialization,
        )

    for k in script: self.options.created(k)

    return self.options.created()
    
  update = install
