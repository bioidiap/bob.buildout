#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon  4 Feb 14:12:24 2013

"""Builds a custom python script interpreter that is executed inside gdb
"""

from .python import Recipe as Script

# Python interpreter script template
class Recipe(Script):
  """Just creates a gdb executable running a python interpreter with the
  "correct" paths
  """

  def __init__(self, buildout, name, options):

    # Preprocess some variables
    self.interpreter = options.setdefault('interpreter', 'gdb-python')

    # initializes the script infrastructure
    super(Recipe, self).__init__(buildout, name, options)

    self.set_template("""#!%(interpreter)s
# %(date)s

'''Dummy program - only starts a new one with a proper environment'''

import os

existing = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = "%(paths)s" + os.pathsep + existing
os.environ["PYTHONPATH"] = os.environ["PYTHONPATH"].strip(os.pathsep)

import sys
if sys.argv[1] in ('-?', '-h', '--help'):
  os.execvp("gdb", sys.argv)
else:
  args = [sys.argv[0], "--ex", "r", "--args", "%(interpreter)s"] + sys.argv[1:]
  os.execvp("gdb", args)
""")
