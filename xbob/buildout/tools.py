#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Wed 22 Aug 10:20:07 2012 

"""Generic tools for Bob buildout recipes
"""

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
