#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Tue 17 Apr 19:16:46 2012 

"""A simple recipe to let buildout add external eggs (as egg-links).
"""

import os
import fnmatch
import logging
import zc.buildout

class Recipe(object):
  """Sets up links to egg installations depending on user configuration
  """

  def __init__(self, buildout, name, options):

    self.name = name
    self.options = options
    self.logger = logging.getLogger(self.name)
    
    self.logger.debug("Initializing '%s'" % self.name)

    self.eggdirs = options.get('egg-directories', [])
    if isinstance(self.eggdirs, (str, unicode)):
      self.eggdirs = [self.eggdirs]

    remove = []
    for k in self.eggdirs:
      d = os.path.abspath(k)
      if not os.path.exists(d):
        self.logger.warn("Ignoring unknown egg directory '%s'" % d)
        remove.append(k)

    self.eggdirs = [os.path.abspath(k) for k in self.eggdirs if k not in remove]

    self.logger.debug("Found %d valid egg directory(ies)" % len(self.eggdirs))

    self.only_glob = options.get('include-glob', '*.egg')
      
    self.buildout_eggdir = \
        buildout['buildout'].get('eggs-directory', '').split()

    self.recurse = buildout['buildout'].get('recurse', '1') in ('1', 'true')

    self.eggs = []
    if self.recurse:
      for path in self.eggdirs:
        for (dirpath, dirnames, filenames) in os.walk(path):
          names = fnmatch.filter(dirnames, self.only_glob) + \
              fnmatch.filter(filenames, self.only_glob)
          self.eggs += [os.path.join(dirpath, k) for k in names]
    else:
      for path in self.eggdirs:
        names = fnmatch.filter(os.listdir(path), self.only_glob)
        self.eggs += [os.path.join(path, k) for k in names]

    self.logger.debug("Found %d valid egg(s)" % len(self.eggs))

    for k in self.eggs: self.logger.info("Found external egg %s" % k)

  def install(self):

    def create_egg_link(path):
      '''Generates the egg-link file'''

      basename = os.path.splitext(os.path.basename(path))[0]
      link = os.path.join(self.buildout_eggdir, basename) + '.egg-link'
      f = open(link, 'wt')
      f.write(path + '\n')
      f.close()
      self.options.created(link)

    self.logger.debug("Installing '%s'..." % self.name)
    
    for k in self.eggs: create_egg_link(k)

    return self.options.created()

  update = install
