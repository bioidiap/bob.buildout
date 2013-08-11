#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Wed 22 Aug 10:20:07 2012 

"""Generic tools for Bob buildout recipes
"""
  
import os
import fnmatch

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

def deep_working_set(egg, depth, logger):
  """Given a zc.recipe.egg.Egg object in 'egg' and a depth, recurse through
  the package dependencies and satisfy them all requiring an egg for each
  dependency."""
  
  import pkg_resources

  def _make_specs(req):
    """Re-creates the specification given the requirement"""
    if not req.specs: return req.project_name
    return ' '.join((req.project_name,) + req.specs[0])

  def _recurse(egg, ws, deps, depth):
    """A recursive requirement parser"""

    if depth <= 0 or len(deps) == 0: return deps

    retval = []
    for dep in deps:
      retval.append(dep)
      dep_deps = [_make_specs(k) for k in \
          ws.find(pkg_resources.Requirement.parse(dep)).requires()]
      retval.extend(_recurse(egg, ws, dep_deps, depth-1))
   
    return retval

  deps, ws = egg.working_set()
  deps = uniq(_recurse(egg, ws, deps, depth))
  logger.warn("returning: %s" % (deps,))
  return egg.working_set(deps)

def find_eggs(eggdirs, glob, recurse):
  """Find egg directories with a certain glob filename under eggdirs"""

  eggs = []

  if recurse:
    for path in eggdirs:
      for (dirpath, dirnames, filenames) in os.walk(path):
        for g in glob:
          names = fnmatch.filter(dirnames, g) + fnmatch.filter(filenames, g)
          eggs += [os.path.join(dirpath, k) for k in names]
  else:
    for path in eggdirs:
      names = fnmatch.filter(os.listdir(path), glob)
      eggs += [os.path.join(path, k) for k in names]

  return eggs

def prepend_env_paths(name, values):
  """Prepends a value to an environment variable in the "right" way"""

  if name in os.environ and os.environ[name]:
    os.environ[name] = os.pathsep.join(values + [os.environ[name]])
  else:
    os.environ[name] = os.pathsep.join(values)

def add_eggs(eggs, l):
  """Adds eggs from a list into the buildout option"""

  egglist = parse_list(eggs)
  egglist = uniq(egglist + l)
  return '\n'.join(egglist)
