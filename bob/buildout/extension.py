"""A monkey patch to zc.buildout.easy_install.develop that takes into
consideration eggs installed at both development and deployment directories."""

import os
import sys
import shutil
import logging
import tempfile
import zc.buildout.easy_install
from zc.buildout.buildout import bool_option

from . import tools
from .envwrapper import EnvironmentWrapper

logger = logger = logging.getLogger("bob.buildout")

runsetup_template = """
import sys
sys.path.insert(0, %(setupdir)r)
sys.path.insert(0, %(setuptools)r)
sys.path.insert(0, %(deveggsdir)r)
sys.path.insert(0, %(eggsdir)r)

import os, setuptools

__file__ = %(__file__)r

os.chdir(%(setupdir)r)
sys.argv[0] = %(setup)r

exec(compile(open(%(setup)r).read(), %(setup)r, 'exec'))
"""

class Extension:

  def __init__(self, buildout):

      self.buildout = buildout

      # where to place the egg
      self.deveggsdir = self.buildout['buildout']['develop-eggs-directory']
      self.eggsdir = self.buildout['buildout']['eggs-directory']

      self.verbose = bool_option(self.buildout['buildout'], 'verbose', 'false')

      # gets a personalized prefixes list or the one from buildout
      prefixes = tools.parse_list(buildout['buildout'].get('prefixes', ''))

      # shall we compile in debug mode?
      debug = self.buildout['buildout'].get('debug', None)
      if isinstance(debug, str):
        debug = bool_option(self.buildout['buildout'], 'debug', 'false')

      # has the user established an enviroment?
      environ_section = self.buildout['buildout'].get('environ', 'environ')
      environ = self.buildout.get(environ_section, {})

      # finally builds the environment wrapper
      self.envwrapper = EnvironmentWrapper(logger, debug, prefixes, environ)
      self.envwrapper.set()

  def develop(self, setup, dest, build_ext=None, executable=sys.executable):

      assert executable == sys.executable, (executable, sys.executable)
      if os.path.isdir(setup):
          directory = setup
          setup = os.path.join(directory, 'setup.py')
      else:
          directory = os.path.dirname(setup)

      undo = []
      try:
          if build_ext:
              setup_cfg = os.path.join(directory, 'setup.cfg')
              if os.path.exists(setup_cfg):
                  os.rename(setup_cfg, setup_cfg+'-develop-aside')
                  def restore_old_setup():
                      if os.path.exists(setup_cfg):
                          os.remove(setup_cfg)
                      os.rename(setup_cfg+'-develop-aside', setup_cfg)
                  undo.append(restore_old_setup)
              else:
                  open(setup_cfg, 'w')
                  undo.append(lambda: os.remove(setup_cfg))
              setuptools.command.setopt.edit_config(
                  setup_cfg, dict(build_ext=build_ext))

          fd, tsetup = tempfile.mkstemp()
          undo.append(lambda: os.remove(tsetup))
          undo.append(lambda: os.close(fd))

          if hasattr(zc.buildout.easy_install, 'distribute_loc'):
            setuptools_loc = zc.buildout.easy_install.distribute_loc
          else:
            setuptools_loc = zc.buildout.easy_install.setuptools_loc

          os.write(fd, (runsetup_template % dict(
              setuptools=setuptools_loc,
              setupdir=directory,
              setup=setup,
              deveggsdir=self.deveggsdir,
              eggsdir=self.eggsdir,
              __file__ = setup,
              )).encode())

          tmp3 = tempfile.mkdtemp('build', dir=dest)
          undo.append(lambda : shutil.rmtree(tmp3))

          args = [executable,  tsetup, '-q', 'develop', '-mxN', '-d', tmp3]
          if self.verbose: args[2] = '-v'

          logger.debug("in: %r\n%s", directory, ' '.join(args))

          zc.buildout.easy_install.call_subprocess(args)

          return zc.buildout.easy_install._copyeggs(tmp3, dest, '.egg-link', undo)

      finally:
          undo.reverse()
          [f() for f in undo]

def extension(buildout):
    """Monkey patches zc.buildout.easy_install.develop"""

    zc.buildout.easy_install.develop = Extension(buildout).develop
