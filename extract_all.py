#!/usr/bin/python

import db
import re
import whm
from collections import defaultdict
import sys

fs = whm.all_ordered_map_files()

last_shape_colors = defaultdict(lambda: ("",""))  # name -> (shape, color) tuple

conn, c = db.get_conn_cursor()

for f in fs:
  #if whm.filename_to_year(f) != 1549: continue
  svg = whm.SvgFile(f)
  c.execute("delete from shapes where year=?", (svg.year(),))

  this_year = defaultdict(lambda: ("", ""))
  present = {}

  for name in svg.countries():
    info = svg.infos_for_country(name)
    if not info: continue
    info = info[0]
    present[name] = True

    path = svg.path_for_id(info['id'])
    if not path: continue  # might be an ellipse

    try:
      color = path['fill']
    except:
      color = 'none'
    shape = svg.combined_shape_for_country(name)

    shape_color = (shape, color)

    if shape_color != last_shape_colors[name]:
      try:
        this_year[name] = (re.sub(r'\r|\n', '', shape), color)
        last_shape_colors[name] = shape_color
      except:
        assert False, '%d: %s' % (svg.year(), name)

  for name in last_shape_colors.keys():
    if name not in present:
      this_year[name] = ('', '')
      del last_shape_colors[name]

  tuples = []
  for name, shape_color in this_year.iteritems():
    tuples.append((name, svg.year(), shape_color[0], shape_color[1]))

  c.executemany("""insert into shapes values (?, ?, ?, ?)""", tuples)
  conn.commit()

  sys.stderr.write('%d...\n' % svg.year())

c.close()
