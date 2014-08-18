"""A monkey patch to zc.buildout.easy_install.develop that takes into
consideration eggs installed at both development and deployment directories."""

import os
import sys
import shutil
import logging
import tempfile
import subprocess
import pkg_resources
import zc.buildout.easy_install
from zc.buildout.buildout import bool_option

from . import tools
from .envwrapper import EnvironmentWrapper

logger = logging.getLogger("bob.buildout")

runsetup_template = """
import os
import sys
for k in %(paths)r.split(os.pathsep): sys.path.insert(0, k)
sys.path.insert(0, %(setupdir)r)

import os, setuptools

__file__ = %(__file__)r

os.chdir(%(setupdir)r)
sys.argv[0] = %(setup)r

exec(compile(open(%(setup)r).read(), %(setup)r, 'exec'))
"""

def get_latest_egg_paths(path):
  """Returns a list of paths in eggs-dir with the latest versions
  of installed distributions."""

  distros = []
  for k in os.listdir(path):
     distros += pkg_resources.find_distributions(os.path.join(path, k))

  distros.sort(key=lambda x: x.parsed_version, reverse=True)

  distro_path = {}
  for k in distros: distro_path.setdefault(k.key, k.location)

  return list(distro_path.values())

def prepend_path(path, paths):
  """Prepends a path to the list of paths making sure it remains unique"""

  if path in paths: paths.remove(path)
  paths.insert(0, path)

class Installer:

  def __init__(self, mix_eggs, verbose, eggs_dir, dev_eggs_dir):

    self.mix_eggs = mix_eggs
    self.verbose = verbose
    self.eggs_dir = eggs_dir
    self.dev_eggs_dir = dev_eggs_dir

  def __call__(self, spec, ws, dest, dist):
    """We will replace the default easy_install call by this one"""

    tmp = tempfile.mkdtemp(dir=dest)

    try:

        # setup the path to be used
        paths = get_latest_egg_paths(self.eggs_dir)
        if self.mix_eggs: prepend_path(self.dev_eggs_dir, paths)
        if hasattr(zc.buildout.easy_install, 'distribute_loc'):
            prepend_path(zc.buildout.easy_install.distribute_loc, paths)
        else:
            prepend_path(zc.buildout.easy_install.setuptools_loc, paths)
        paths = os.pathsep.join(paths)

        args = [sys.executable, '-c',
            zc.buildout.easy_install._easy_install_cmd, '-mZUNxd', tmp]
        if self.verbose:
            args.append('-v')
        else:
            args.append('-q')

        args.append(spec)

        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.debug('Running easy_install:\n"%s"\npath=%s\n',
                         '" "'.join(args), paths)

        sys.stdout.flush() # We want any pending output first

        exit_code = subprocess.call(list(args),
            env=dict(os.environ, PYTHONPATH=paths))

        dists = []
        env = pkg_resources.Environment([tmp])
        for project in env:
            dists.extend(env[project])

        if exit_code:
            logger.error(
                "An error occurred when trying to install %s. "
                "Look above this message for any errors that "
                "were output by easy_install.",
                dist)

        if not dists:
            raise zc.buildout.UserError("Couldn't install: %s" % dist)

        if len(dists) > 1:
            logger.warn("Installing %s\n"
                        "caused multiple distributions to be installed:\n"
                        "%s\n",
                        dist, '\n'.join(map(str, dists)))
        else:
            d = dists[0]
            if d.project_name != dist.project_name:
                logger.warn("Installing %s\n"
                            "Caused installation of a distribution:\n"
                            "%s\n"
                            "with a different project name.",
                            dist, d)
            if d.version != dist.version:
                logger.warn("Installing %s\n"
                            "Caused installation of a distribution:\n"
                            "%s\n"
                            "with a different version.",
                            dist, d)

        result = []
        for d in dists:
            newloc = os.path.join(dest, os.path.basename(d.location))
            if os.path.exists(newloc):
                if os.path.isdir(newloc):
                    shutil.rmtree(newloc)
                else:
                    os.remove(newloc)
            os.rename(d.location, newloc)

            [d] = pkg_resources.Environment([newloc])[d.project_name]

            result.append(d)

        return result

    finally:
        shutil.rmtree(tmp)

class Extension:

  def __init__(self, buildout):

      self.buildout = buildout

      # where to place the egg
      self.dev_eggs_dir = self.buildout['buildout']['develop-eggs-directory']
      self.eggs_dir = self.buildout['buildout']['eggs-directory']

      self.verbose = bool_option(self.buildout['buildout'], 'verbose', 'false')
      self.mix_eggs = bool_option(self.buildout['buildout'], 'mix-eggs', 'false')

      # gets a personalized prefixes list or the one from buildout
      prefixes = tools.parse_list(buildout['buildout'].get('prefixes', ''))

      # shall we compile in debug mode?
      debug = self.buildout['buildout'].get('debug', False)
      if isinstance(debug, str):
        debug = bool_option(self.buildout['buildout'], 'debug', 'false')

      # has the user established an enviroment?
      environ_section = self.buildout['buildout'].get('environ', 'environ')
      environ = self.buildout.get(environ_section, {})

      # finally builds the environment wrapper
      self.envwrapper = EnvironmentWrapper(logger, debug, prefixes, environ)
      self.envwrapper.set()

      # and we replace the installer by our modified version
      self.installer = Installer(self.mix_eggs, self.verbose,
          self.eggs_dir, self.dev_eggs_dir)

  def develop(self, setup, dest, build_ext=None, executable=sys.executable):

      assert executable == sys.executable, (executable, sys.executable)
      if os.path.isdir(setup):
          directory = setup
          setup = os.path.join(directory, 'setup.py')
      else:
          directory = os.path.dirname(setup)

      undo = []

      try:

          # setup the path to be used
          paths = get_latest_egg_paths(self.eggs_dir)
          prepend_path(self.dev_eggs_dir, paths) #dev in front of mature eggs
          if hasattr(zc.buildout.easy_install, 'distribute_loc'):
              prepend_path(zc.buildout.easy_install.distribute_loc, paths)
          else:
              prepend_path(zc.buildout.easy_install.setuptools_loc, paths)
          paths = os.pathsep.join(paths)

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

          os.write(fd, (runsetup_template % dict(
              paths=paths,
              setup=setup,
              setupdir=directory,
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

    ext = Extension(buildout)
    zc.buildout.easy_install.develop = ext.develop
    zc.buildout.easy_install.Installer._call_easy_install = ext.installer
