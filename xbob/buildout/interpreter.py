#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon  4 Feb 14:12:24 2013 

"""Builds custom interpreters with the right paths for external Bob
"""

import os
import logging
import zc.buildout.easy_install
from zc.recipe.egg import Scripts
#from z3c.recipe.scripts import Scripts #does not work as expected...

zc.buildout.easy_install.py_script_template = \
    zc.buildout.easy_install.py_script_template.replace(
    """__import__("code").interact(banner="", local=globals())""",
    """
    import os
    if os.environ.has_key('PYTHONSTARTUP') and os.environ['PYTHONSTARTUP']:
      execfile(os.environ['PYTHONSTARTUP'])
    __import__('code').interact(banner=('Python ' + sys.version + ' on ' + sys.platform + '\\nType "help", "copyright", "credits" or "license" for more information.'), local=globals())
  """)

from .tools import *

class Recipe(Scripts):
  """Just creates a given script with the "correct" paths
  """

  def __init__(self, buildout, name, options):
    
    self.name = name
    self.options = options
    self.logger = logging.getLogger(self.name)
    self.buildout = buildout
    self.eggdirs = []

    options['interpreter'] = options.get('name', name)
    
    options['include-site-packages'] = options.get('include-site-packages', 'true')
    options['executable'] = options.get('executable', buildout['buildout']['executable'])

    # try to get personalized eggs list or from the buildout
    self.eggs = parse_list(options.get('eggs', ''))
    if not self.eggs: 
      self.eggs = parse_list(buildout['buildout'].get('eggs', ''))

    # try to get personalized prefixes list or from the the buildout
    self.prefixes = parse_list(buildout['buildout'].get('prefixes', ''))
    if not self.prefixes: 
      self.prefixes = parse_list(buildout['buildout'].get('prefixes', ''))
    self.prefixes = [os.path.abspath(k) for k in self.prefixes if os.path.exists(k)]

    if self.prefixes:
      # Add that to the eggdirs that will be used for finding packages as well
      self.eggdirs[0:0] = [os.path.join(k, 'lib') for k in self.prefixes]

    self.only_glob = parse_list(options.get('include-globs', 'bob*.egg-info'))

    self.recurse = buildout['buildout'].get('recurse', '1') in ('1', 'true')
    
    self.user_paths = [os.path.dirname(k) for k in find_eggs(self.eggdirs, self.only_glob, self.recurse)]

    # initializes the script infrastructure
    super(Scripts, self).__init__(buildout, name, options)

  def working_set(self, extra=()):
    """Separate method to just get the working set - overriding zc.recipe.egg

    This is intended for reuse by similar recipes.
    """

    options = self.options
    b_options = self.buildout['buildout']

    distributions = self.eggs
    orig_distributions = distributions[:]
    distributions.extend(extra)

    if b_options.get('offline') == 'true':

      paths = self.user_paths + [
          options['develop-eggs-directory'],
          options['eggs-directory']
          ]

      # checks each distribution individually, to avoid that easy_install
      # summarizes the output directories and get us with a directory set which
      # already contains dependencies that should be taken from 'prefixes'
      # instead!
      ws = None
      for d in distributions:
        tws = zc.buildout.easy_install.working_set(
            [d,], options['executable'], paths,
            include_site_packages=self.include_site_packages,
            allowed_eggs_from_site_packages=self.allowed_eggs,
            )
        if ws is None: 
          ws = tws
        else: 
          for k in tws: ws.add(k)

      # tries to check if ipython is available
      try:
        tws = zc.buildout.easy_install.working_set(
            ['ipython',], options['executable'], paths,
            include_site_packages=self.include_site_packages,
            allowed_eggs_from_site_packages=self.allowed_eggs,
            )
        # hooks in ipython
        if ws is None:
          ws = tws
        else:
          for k in tws: ws.add(k)
        self.options['entry-points'] = 'i%s=IPython.frontend.terminal.ipapp:launch_new_instance' % self.name

      except zc.buildout.easy_install.MissingDistribution, e:
        self.logger.info('Could not find ipython - not installing specific interpreter')
        pass


    else:
      kw = {}
      if 'unzip' in options:
          kw['always_unzip'] = options.query_bool('unzip', None)

      paths = self.user_paths + [
          options['develop-eggs-directory'],
          ]

      # checks each distribution individually, to avoid that easy_install
      # summarizes the output directories and get us with a directory set which
      # already contains dependencies that should be taken from 'prefixes'
      # instead!
      ws = None
      for d in distributions:
        tws = zc.buildout.easy_install.install(
            [d,], options['eggs-directory'],
            links=self.links,
            index=self.index,
            executable=options['executable'],
            path=paths,
            newest=b_options.get('newest') == 'true',
            include_site_packages=self.include_site_packages,
            allowed_eggs_from_site_packages=self.allowed_eggs,
            allow_hosts=self.allow_hosts,
            **kw)

        if ws is None: 
          ws = tws
        else: 
          for k in tws: ws.add(k)

      # tries to check if ipython is available
      try:
        tws = zc.buildout.easy_install.install(
            ['ipython',], options['eggs-directory'],
            links=self.links,
            index=self.index,
            executable=options['executable'],
            path=paths,
            newest=b_options.get('newest') == 'true',
            include_site_packages=self.include_site_packages,
            allowed_eggs_from_site_packages=self.allowed_eggs,
            allow_hosts=self.allow_hosts,
            **kw)
        # hooks in ipython
        if ws is None:
          ws = tws
        else:
          for k in tws: ws.add(k)
        self.options['entry-points'] = 'i%s=IPython.frontend.terminal.ipapp:launch_new_instance' % self.name

      except zc.buildout.easy_install.MissingDistribution, e:
        self.logger.info('Could not find ipython - not installing specific interpreter')
        pass

    return orig_distributions, ws

  def install(self):
    return super(Scripts, self).install()

  update = install
