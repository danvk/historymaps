#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
import re
import glob

def name_to_year(name):
  # Name is something like worldhistorymaps/html/WA2000.svg
  m = re.search(r'W([AB])(\d{4})\.svg', name)
  assert m
  ab = m.group(1)
  y = int(m.group(2))
  return (-1 if ab == 'B' else 1) * y

for f in sorted(glob.glob('worldhistorymaps/html/W?????.svg'), key=name_to_year):
  bs = BeautifulSoup(file(f))

  rome_soup = bs(text=re.compile('Rome'))
  title = [t.parent for t in rome_soup if t.parent.name == 'title']
  if len(title) == 0:
    continue

  # there are dupes in a few places. Also East Rome/West Rome in 400-500.
  match = title[0].parent
  rome_id = match['id']
  path = bs('path', id=rome_id)
  assert len(path) == 1, len(path)

  print '%s %s' % (f, path[0])
