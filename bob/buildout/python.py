#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon  4 Feb 14:12:24 2013

"""Builds a custom python script interpreter
"""

import os
import sys
import time

from . import tools
from .script import Recipe as Script

class Recipe(Script):
  """Just creates a python interpreter with the "correct" paths
  """

  def __init__(self, buildout, name, options):

    # Preprocess some variables
    self.interpreter = options.setdefault('interpreter', 'python')

    # initializes the script infrastructure
    super(Recipe, self).__init__(buildout, name, options)

    # Python interpreter script template
    self.template = """#!%(interpreter)s
# %(date)s

'''Booting interpreter - starts a new one with a proper environment'''

import os

existing = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = "%(paths)s" + os.pathsep + existing
os.environ["PYTHONPATH"] = os.environ["PYTHONPATH"].strip(os.pathsep)

import sys
os.execvp("%(interpreter)s", ["%(interpreter)s"] + sys.argv[1:])
"""

  def set_template(self, template):
    self.template = template

  def install_on_wrapped_env(self):
    eggs, ws = self.working_set()
    retval = os.path.join(self.buildout['buildout']['bin-directory'],
        self.interpreter)
    self._write_executable_file(retval, self.template % {
      'date': time.asctime(),
      'paths': os.pathsep.join(tools.get_pythonpath(ws, self.buildout, self.prefixes)),
      'interpreter': sys.executable,
      })
    self.logger.info("Generated script '%s'." % retval)
    return (retval,)

  def _write_executable_file(self, name, content):
    f = open(name, 'w')
    current_umask = os.umask(0o022) # give a dummy umask
    os.umask(current_umask)
    perms = 0o777 - current_umask
    try:
      f.write(content)
    finally:
      f.close()
      os.chmod(name, perms)
