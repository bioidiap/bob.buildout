#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Tue 17 Apr 19:16:46 2012 

"""A simple recipe to easily generate sphinx documentation
"""

import os
import re
import sys
import shutil
import logging
import zc.buildout
import zc.recipe.egg
from datetime import datetime
from fnmatch import fnmatch

from .tools import *

class Recipe(object):
  """zc.buildout recipe"""

  def __init__(self, buildout, name, options):

    self.buildout = buildout
    self.name = name
    self.options = options
    self.logger = logging.getLogger(self.name)

    self.buildout_dir = self.buildout['buildout']['directory']
    self.bin_dir = self.buildout['buildout']['bin-directory']
    self.parts_dir = self.buildout['buildout']['parts-directory']

    self.interpreter = options.get('interpreter')
    self.outputs = options.get('outputs', 'html')
    
    self.eggs = parse_list(options.get('eggs', ''))

    if 'Sphinx' not in self.eggs: self.eggs.append('Sphinx')
    options['eggs'] = '\n'.join(self.eggs)
    self.egg = zc.recipe.egg.Egg(buildout, name, options)

    self.build_dir = os.path.join(self.buildout_dir, 
        options.get('build', 'sphinx'))
    self.source_dir = options.get('source',
        os.path.join(self.build_dir, 'docs'))
    self.extra_paths = self.options.get('extra-paths', None)

    self.script_name = options.get('script', name)
    self.script_path = os.path.join(self.bin_dir, self.script_name)
    self.makefile_path = os.path.join(self.build_dir, 'Makefile')
    self.batchfile_path = os.path.join(self.build_dir, 'make.bat')

    self.re_sphinxbuild = re.compile(r'^SPHINXBUILD .*$', re.M)
    self.build_command = os.path.join(self.bin_dir, 'sphinx-build')
    if self.interpreter:
        self.build_command = ' '.join([self.interpreter, self.build_command])

  def install(self):
    """Installer"""

    # Creates the build folder
    if not os.path.exists(self.build_dir): os.makedirs(self.build_dir)

    # Resolves source path
    if not os.path.isabs(self.source_dir):
      self.source_dir = self._resolve_path(self.source_dir)
    
    # We need extra_paths, e.g for docutils via fake-eggs
    # most probably this should be really fixed in buildout or the way
    # fake-zope-eggs messes with buildout - until then: This enables sphinx
    # to coexist in a buildout with fake-zope-eggs.
    extra_paths = []
    if self.extra_paths:
      for extra_path in self.extra_paths.split():
        dir = os.path.dirname(extra_path)
        for filename in os.listdir(dir):
          filename = os.path.join(dir, filename)
          if fnmatch(filename, extra_path):
            extra_paths.append(filename)
        sys.path.extend(extra_paths)

    from sphinx.quickstart import MAKEFILE
    from sphinx.quickstart import BATCHFILE
    from sphinx.util import make_filename

    # and cleanup again
    if extra_paths:
      sys.path.reverse()
      for x in extra_paths:
        sys.path.remove(x)
      sys.path.reverse()

    # Creates the Makefile
    self.logger.info('writing Makefile...')
    self._write_file(self.makefile_path,
        self.re_sphinxbuild.sub(r'SPHINXBUILD = %s' % (self.build_command),
          MAKEFILE % dict( rsrcdir = self.source_dir,
            rbuilddir = self.build_dir,
            project_fn = self.script_name )))

    # Creates the batch file
    #self.logger.info('writing BATCHFILE..')
    #self._write_file(self.batchfile_path,
    #    self.re_sphinxbuild.sub(r'SPHINXBUILD = %s' % (self.build_command),
    #        BATCHFILE % dict( rsrcdir = self.source_dir,
    #                          rbuilddir = self.build_dir,
    #                          project_fn = self.script_name )))

    # 4. CREATE CUSTOM "sphinx-build" SCRIPT
    self.logger.info('writing custom sphinx-builder script...')
    script = ['cd %s' % self.build_dir]
    if 'doctest' in self.outputs: script.append('make doctest')
    if 'html' in self.outputs: script.append('make html')
    if 'latex' in self.outputs: script.append('make latex')
    if 'epub' in self.outputs: script.append('make epub')
    if 'pdf' in self.outputs:
      latex = ''
      if 'latex' not in self.outputs: latex = 'make latex && '
      script.append(latex+'cd %s && make all-pdf' % \
          os.path.join(self.build_dir, 'latex'))
    self._write_file(self.script_path, '\n'.join(script))
    os.chmod(self.script_path, 0777)

    # Installs Sphinx with script and extra paths
    egg_options = {}
    if extra_paths:
      self.logger.info('inserting extra-paths..')
      egg_options['extra_paths'] = extra_paths

    # WEIRD: this is needed for doctest to pass
    # :write gives error
    #       -> ValueError: ('Expected version spec in',
    #               'collective.recipe.sphinxbuilder:write', 'at', ':write')
    requirements, ws = self.egg.working_set()
    zc.buildout.easy_install.scripts(
        [('sphinx-quickstart', 'sphinx.quickstart', 'main'),
          ('sphinx-build', 'sphinx', 'main')], ws,
        self.buildout[self.buildout['buildout']['python']]['executable'],
        self.bin_dir, **egg_options)

    return [self.script_path, self.makefile_path, self.batchfile_path]

  update = install

  def _resolve_path(self, source):
    source = source.split(':')
    dist, ws = self.egg.working_set([source[0]])
    source_directory = ws.by_key[source[0]].location

    # check for namespace name (eg: my.package will resolve as my/package)
    # TODO
    namespace_packages = source[0].split('.')
    if len(namespace_packages)>=1:
      source_directory = os.path.join(source_directory, *namespace_packages)

    if len(source)==2:
      source_directory = os.path.join(source_directory, source[1])
    return source_directory

  def _write_file(self, name, content):
    f = open(name, 'w')
    try: f.write(content)
    finally: f.close()
