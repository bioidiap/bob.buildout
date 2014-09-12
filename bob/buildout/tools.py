#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Wed 22 Aug 10:20:07 2012

"""Generic tools for Bob buildout recipes
"""

import os
import sys
import pkg_resources
import zc.buildout
import zc.buildout.easy_install
from zc.buildout.buildout import bool_option, MissingOption

import logging
logger = logging.getLogger(__name__)

def uniq(seq, idfun=None):
  """Order preserving, fast de-duplication for lists"""

  if idfun is None:
    def idfun(x): return x

  seen = {}
  result = []

  for item in seq:
    marker = idfun(item)
    if marker in seen: continue
    seen[marker] = 1
    result.append(item)
  return result

def parse_list(l):
  """Parses a ini-style list from buildout and solves complex nesting"""

  return uniq([k.strip() for k in l.split() if len(k.strip()) > 0])

def add_eggs(eggs, l):
  """Adds eggs from a list into the buildout option"""

  egglist = parse_list(eggs)
  egglist = uniq(egglist + l)
  return '\n'.join(egglist)

def prepend_path(path, paths):
  """Prepends a path to the list of paths making sure it remains unique"""

  if path in paths: paths.remove(path)
  paths.insert(0, path)

def is_directory(filename):
  """Tells if the file is a directory"""

  return os.path.isdir(filename)

def directory_readlines(package, filename):
  """Read all lines of a given file in a directory"""

  try:
    return open(os.path.join(package, filename), 'rt').readlines()
  except:
    pass

  return []

def is_zipfile(filename):
  """Tells if the file is a zip file"""

  import zipfile

  return zipfile.is_zipfile(filename)

def zipfile_readlines(package, filename):
  """Read all lines of a given file in a tar ball"""

  import zipfile

  with zipfile.ZipFile(package) as f:
    try:
      package_dir = os.path.splitext(os.path.basename(package))[0]
      return f.open(os.path.join(package_dir, filename), 'rU').readlines()
    except:
      pass

  return []

def is_tarfile(filename):
  """Tells if the file is a tar ball"""

  import tarfile

  return tarfile.is_tarfile(filename)

def tarfile_readlines(package, filename):
  """Read all lines of a given file in tar ball"""

  import tarfile

  with tarfile.open(package) as f:
    try:
      package_dir = os.path.splitext(os.path.dirname(package))[0]
      if package_dir.endswith('.tar'): package_dir = package_dir[:-4]
      return f.extractfile(os.path.join(package_dir, filename)).readlines()
    except:
      pass

  return []

def package_readlines(package, filename):
  """Extracts a single file contents from a given package"""

  if is_directory(package):
    return directory_readlines(package, filename)
  elif is_zipfile(package):
    return zipfile_readlines(package, filename)
  elif is_tarfile(package):
    return tarfile_readlines(package, filename)
  else:
    raise RuntimeError("package format not recognized: `%s'" % package)

def requirement_is_satisfied(requirement, working_set, newest):
  """Checks if the specifications for a requirement are satisfied by the
  current working set"""

  if newest: return False

  try:
    working_set.require(requirement)
    return True
  except:
    pass

  return False

def unsatisfied_requirements(buildout, package, working_set):
  """Reads and extracts the unsatisfied requirements from the package
  """

  # read all lines from "requirements.txt"
  specs = [k.strip() for k in package_readlines(package, 'requirements.txt')]

  # discard empty lines and comments
  specs = [k for k in specs if k and k[0] != '#']

  # do not consider packages which are already installed, with a reasonable
  # version matching the user specification, either on the current working
  # set, the installed eggs or the system paths
  newest = bool_option(buildout, 'newest', 'true')

  left_over = []
  for k in specs:
    if requirement_is_satisfied(k, working_set, newest):
      dist = working_set.require(k)[0]
      logger.info("taking requirement `%s' (%s) from `%s'", dist.key,
          dist.version, dist.location)
    else:
      left_over.append(k)
  specs = left_over

  return left_over

def merge_working_sets(self, other):
  """Merge two working sets, results are put on the first one"""

  for dist in other.by_key.values(): self.add(dist)
  return self

def install_package(buildout, specification, working_set):
  """Installs a package on either the eggs directory or development-eggs
  directory. Updates the working set"""

  new_ws = zc.buildout.easy_install.install(
      specs = [specification],
      dest = buildout['eggs-directory'],
      links = buildout.get('find-links', '').split(),
      index = buildout.get('index', None),
      path = [buildout['develop-eggs-directory']],
      working_set = working_set,
      newest = bool_option(buildout, 'newest', 'true'),
      )

  merge_working_sets(working_set, new_ws)

  return working_set

def satisfy_requirements(buildout, package, working_set):
  """Makes sure all requirements from a given package are installed properly
  before we try to install the package itself."""

  requirements = unsatisfied_requirements(buildout, package, working_set)

  if not requirements: return

  # only installs if not on "offline" mode
  if offline(buildout):
    raise zc.buildout.UserError("We don't have a distribution for %s\n"
        "and can't install one in offline (no-install) mode.\n"
        % ','.join(requirements))

  # installs all missing dependencies, if required, updates working set
  for req in requirements:
    logger.info("Installing `%s' for package `%s'...", req, package)
    working_set = install_package(buildout, req, working_set)

def get_pythonpath(working_set):
  """Returns the PYTHONPATH setting for a particular working set"""

  # get all paths available in the current working set
  paths = list(working_set.entries)

  if hasattr(zc.buildout.easy_install, 'distribute_loc'):
    prepend_path(zc.buildout.easy_install.distribute_loc, paths)
  else:
    prepend_path(zc.buildout.easy_install.setuptools_loc, paths)

  return [k for k in working_set.entries if k not in sys.path]

def get_prefixes(buildout):
  """Returns a list of prefixes set on the buildout section"""

  prefixes = parse_list(buildout.get('prefixes', ''))
  return [os.path.abspath(k) for k in prefixes if os.path.exists(k)]

def find_site_packages(prefixes):
  """Finds python packages on prefixes"""

  from distutils.sysconfig import get_python_lib

  # Standard prefixes to check
  PYTHONDIR = 'python%d.%d' % sys.version_info[0:2]
  SUFFIXES = uniq([
      get_python_lib(prefix=''),
      os.path.join('lib', PYTHONDIR, 'site-packages'),
      os.path.join('lib32', PYTHONDIR, 'site-packages'),
      os.path.join('lib64', PYTHONDIR, 'site-packages'),
      ])

  retval = []

  for k in prefixes:
    for suffix in SUFFIXES:
      candidate = os.path.realpath(os.path.join(k, suffix))
      if os.path.exists(candidate) and candidate not in retval:
        retval.append(candidate)

  return retval

def working_set(buildout, prefixes):
  """Creates and returns a new working set based on user prefixes and existing
  packages already installed"""

  working_set = pkg_resources.WorkingSet([])

  # add development directory first
  working_set.add_entry(buildout['develop-eggs-directory'])

  # add all egg directories
  for path in os.listdir(buildout['eggs-directory']):
    full_path = os.path.join(buildout['eggs-directory'], path)
    working_set.add_entry(full_path)

  # adds the user paths
  for path in find_site_packages(prefixes):
    working_set.add_entry(full_path)

  # finally, adds the system path
  for path in sys.path: working_set.add_entry(path)

  return working_set

def filter_working_set_hard(working_set, requirements):
  """Returns a new working set which contains only the paths to the required
  packages. Raises if a requirement cannot be met."""

  retval = pkg_resources.WorkingSet([])

  for req in requirements:
    dists = working_set.require(req)
    for dist in dists: retval.add(dist)

  return retval

def filter_working_set_soft(working_set, requirements):
  """Returns a new working set which contains only the paths to the required
  packages. requirements that cannot be fulfilled are returned"""

  unmet_requirements = []

  retval = pkg_resources.WorkingSet([])

  for req in requirements:
    try:
      dists = working_set.require(req)
      for dist in dists: retval.add(dist)
    except:
      unmet_requirements.append(req)

  return retval, unmet_requirements

def newest(buildout):
  return bool_option(buildout, 'newest', 'true')

def offline(buildout):
  return bool_option(buildout, 'offline', 'false')

def debug(buildout):
  return bool_option(buildout, 'debug', 'false')

def verbose(buildout):
  return bool_option(buildout, 'verbose', 'false')

def eggs(buildout, options, name):
  retval = options.get('eggs', buildout.get('eggs', ''))
  if not retval:
    raise MissingOption("Could not find an 'eggs' entry in either the " \
        "section '%s' nor at the 'buildout' section" % (name,))
  return parse_list(retval)
