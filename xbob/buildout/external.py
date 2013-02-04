#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Tue 17 Apr 19:16:46 2012 

"""A simple recipe to let buildout add external eggs (as egg-links).
"""

import os
import sys
import logging
import zc.buildout

from .tools import *

class Recipe(object):
  """Sets up links to egg installations depending on user configuration
  """

  def __init__(self, buildout, name, options):

    self.name = name
    self.options = options
    self.logger = logging.getLogger(self.name)
    self.buildout = buildout
    
    self.logger.debug("Initializing '%s'" % self.name)

    self.eggdirs = parse_list(options.get('egg-directories', ''))
    self.eggdirs = [os.path.abspath(k) for k in self.eggdirs if os.path.exists(k)]

    self.prefixes = parse_list(buildout['buildout'].get('prefixes', ''))
    self.prefixes = [os.path.abspath(k) for k in self.prefixes if os.path.exists(k)]

    if self.prefixes:
      # Add that to the eggdirs that will be used for finding packages as well
      self.eggdirs[0:0] = [os.path.join(k, 'lib') for k in self.prefixes]

    self.logger.debug("Found %d valid egg directory(ies)" % len(self.eggdirs))

    self.only_glob = parse_list(options.get('include-globs', 'bob*.egg-info'))
      
    self.buildout_eggdir = buildout['buildout'].get('develop-eggs-directory')

    self.recurse = buildout['buildout'].get('recurse', '1') in ('1', 'true')
    
    self.strict_version = buildout['buildout'].get('strict-version', '1') in ('1', 'true')

    self.eggs = find_eggs(self.eggdirs, self.only_glob, self.recurse)
    
    for k in self.eggs:
      # Announce
      self.logger.info("Found external egg %s" % k)

  def install(self):

    def create_egg_link(distro):
      '''Generates the egg-link file'''

      basename, ext = os.path.splitext(os.path.basename(distro))
      link = os.path.join(self.buildout_eggdir, basename) + '.egg-link'
      f = open(link, 'wt')
      
      if ext.lower() == '.egg':
        f.write(distro + '\n')
      elif ext.lower() == '.egg-info':
        f.write(os.path.dirname(distro) + '\n')
      else:
        f.close()
        message = "Can't deal with extension %s (%s)" % (ext, distro)
        self.logger.error(message)
        raise RuntimeError, message

      f.close()
      self.options.created(link)

    for k in self.eggs:
      #self.logger.info("Linking external egg %s" % k)
      create_egg_link(k)

    return self.options.created()

  update = install
