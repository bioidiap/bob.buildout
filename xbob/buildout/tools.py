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

def add_eggs(eggs, l):
  """Adds eggs from a list into the buildout option"""

  egglist = parse_list(eggs)
  egglist = uniq(egglist + l)
  return '\n'.join(egglist)
