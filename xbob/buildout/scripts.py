#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon  4 Feb 14:12:24 2013 

"""Builds custom interpreters with the right paths for external Bob
"""

import os
import logging
import zc.buildout
from . import tools
from .script import Recipe as Script
from distutils.sysconfig import get_python_lib

class Recipe(object):
  """Just creates a given script with the "correct" paths
  """

  def __init__(self, buildout, name, options):

    self.logger = logging.getLogger(name.capitalize())

    bopts = buildout['buildout']

    # Gets a personalized eggs list or the one from buildout
    self.eggs = tools.parse_list(options.get('eggs', ''))
    if not self.eggs: 
      self.eggs = tools.parse_list(bopts.get('eggs', ''))

    if not self.eggs: # Cannot proceed without eggs...
      raise MissingOption("Referenced option does not exist for section nor it could be found on the global 'buildout' section:", name, 'eggs')
    
    # Gets a personalized prefixes list or the one from buildout
    prefixes = tools.parse_list(options.get('prefixes', ''))
    if not prefixes: prefixes = tools.parse_list(bopts.get('prefixes', ''))
    prefixes = [os.path.abspath(k) for k in prefixes if os.path.exists(k)]

    # Computes the final user paths that need consideration, set that back on
    # the buildout section
    user_paths = ''
    if prefixes:
      user_paths = []
      for k in prefixes:
        candidate = os.path.realpath(get_python_lib(prefix=k))
        if os.path.exists(candidate) and candidate not in user_paths: 
          self.logger.info("Adding prefix '%s'" % candidate)
          user_paths.append(candidate)
      user_paths = '\n'.join(user_paths)

    # Initializes interpreter
    python_options = zc.buildout.buildout.Options(buildout, name + '+python',
        options.copy())
    interpreter = python_options.setdefault('interpreter', 'python')
    if python_options.has_key('scripts'): del python_options['scripts']
    python_options['eggs'] = '\n'.join(self.eggs)
    python_options['user-paths'] = user_paths
    self.python = Script(buildout, name, python_options)

    # Initializes local eggs
    script_options = zc.buildout.buildout.Options(buildout, name + '+scripts', 
        options.copy())
    if script_options.has_key('interpreter'): del script_options['interpreter']
    if script_options.has_key('scripts'): del script_options['scripts']
    python_options['eggs'] = '\n'.join(self.eggs)
    script_options['user-paths'] = user_paths
    self.scripts = Script(buildout, name + '+scripts', script_options)

    # Initializes ipython, if it is available - don't panic!
    ipy_options = zc.buildout.buildout.Options(buildout, name + '+ipython', 
        options.copy())
    if ipy_options.has_key('interpreter'): del ipy_options['interpreter']
    ipy_options['entry-points'] = 'i%s=IPython.frontend.terminal.ipapp:launch_new_instance' % interpreter
    ipy_options['scripts'] = 'i%s' % interpreter
    if 'ipython' not in self.eggs: self.eggs.append('ipython')
    ipy_options['eggs'] = '\n'.join(self.eggs)
    ipy_options['user-paths'] = user_paths
    ipy_options['dependent-scripts'] = 'false'
    ipy_options.setdefault('panic', 'false')
    self.ipython = Script(buildout, name + '+ipython', ipy_options)

    # Initializes nosetests, if it is available - don't panic!
    nose_options = zc.buildout.buildout.Options(buildout, name + '+nosetests', 
        options.copy())
    if nose_options.has_key('interpreter'): del nose_options['interpreter']
    if options.has_key('nose-flags'):
      # use 'options' instead of 'nose_options' to force use
      flags = tools.parse_list(options['nose-flags'])
      init_code = ['sys.argv.append(%r)' % k for k in flags]
      nose_options['initialization'] = '\n'.join(init_code)
    nose_options['entry-points'] = 'nosetests=nose:run_exit'
    nose_options['scripts'] = 'nosetests'
    if 'nose' not in self.eggs: self.eggs.append('nose')
    nose_options['eggs'] = '\n'.join(self.eggs)
    nose_options['user-paths'] = user_paths
    nose_options['dependent-scripts'] = 'false'
    nose_options.setdefault('panic', 'false')
    self.nose = Script(buildout, name + '+nosetests', nose_options)

    # Initializes the sphinx document generator - don't panic!
    sphinx_options = zc.buildout.buildout.Options(buildout, name + '+sphinx', 
        options.copy())
    if sphinx_options.has_key('interpreter'): del sphinx_options['interpreter']
    sphinx_options['scripts'] = '\n'.join([
      'sphinx-build',
      'sphinx-apidoc', 
      'sphinx-autogen', 
      'sphinx-quickstart',
      ])
    if sphinx_options.has_key('entry-points'): 
      del sphinx_options['entry-points']
    if 'sphinx' not in self.eggs: self.eggs.append('sphinx')
    sphinx_options['eggs'] = '\n'.join(self.eggs)
    sphinx_options['user-paths'] = user_paths
    sphinx_options.setdefault('panic', 'false')
    sphinx_options['dependent-scripts'] = 'false'
    self.sphinx = Script(buildout, name + '+sphinx', sphinx_options)

  def install(self):
    return \
        self.python.install() + \
        self.scripts.install() + \
        self.ipython.install() + \
        self.nose.install() + \
        self.sphinx.install()

  update = install
