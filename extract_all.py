#!/usr/bin/python

import db
import re
import whm
from collections import defaultdict
import sys

countries = [
  'Rome',
  'West Rome',
  'East Rome',
  'Byzantium',
  'Parthia',
  'Arabia',
  'Turkey',
  'Osman'
]

fs = whm.all_ordered_map_files()

last_shapes = defaultdict(str)  # name -> shape string

conn, c = db.get_conn_cursor()

for f in fs:
  svg = whm.SvgFile(f)
  c.execute("delete from shapes where year=?", (svg.year(),))

  this_year = defaultdict(str)
  present = {}

  for name in svg.countries():
    info = svg.info_for_country(name)
    if not info: continue
    present[name] = True

    shape = svg.shape_for_id(info['id'])
    if not shape: continue  # might be an ellipse

    if shape != last_shapes[name]:
      try:
        this_year[name] = re.sub(r'\r|\n', '', shape)
        last_shapes[name] = shape
      except:
        assert False, '%d: %s' % (svg.year(), name)

  for name in last_shapes.keys():
    if name not in present:
      this_year[name] = ''
      del last_shapes[name]

  for name, shape in this_year.iteritems():
    c.execute("""insert into shapes values (?, ?, ?)""",
              (name, svg.year(), shape))
  conn.commit()

  sys.stderr.write('%d...\n' % svg.year())

c.close()
