#!/usr/bin/python

import whm
import sys
import re

last_shape = ''
for year in range(-390, 500):
  svg = whm.SvgFile.forYear(year)
  if not svg:
    sys.stderr.write('%+5d: Missing file\n' % year)
    continue

  info = svg.info_for_country('Rome')
  if not info:
    sys.stderr.write('%+5d: No Rome\n' % year)
    continue

  shape = svg.shape_for_id(info['id'])
  shape = re.sub(r'\r|\n', '', shape)
  if shape != last_shape:
    print '%+5d: %s' % (year, shape)
    last_shape = shape

  if year % 100 == 0:
    sys.stderr.write('%+5d: ...\n' % year)
