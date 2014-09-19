#!/usr/bin/env python
"""
Reads in the shapefile from http://publications.newberry.org/ahcbp/pages/United_States.html
and produces a JSON file containing data on U.S. Territory & State boundaries.
"""

import shapefile
import shape_tools
import itertools
import json
from collections import defaultdict

# states = shapefile.Reader('US_AtlasHCB_StateTerr_Gen001/' +
#    'US_HistStateTerr_Gen001_Shapefile/US_HistStateTerr_Gen001.shp')

states = shapefile.Reader('US_AtlasHCB_StateTerr_Gen05/' +
    'US_HistStateTerr_Gen05_Shapefile/US_HistStateTerr_Gen05.shp')

# sample record:
#  0: 1
#  1: Alaska Department
#  2: ak_dept
#  3: 1
#  4: [1867, 3, 30]
#  5: [1884, 5, 16]
#  6: The United States acquired Alaska from Russia. Presidential proclamation issued 20 June 1867. Alaska was considered an "unorganized territory" with no organized civil government.
#  7: (Parry, 134:331-335; Swindler, 1:163-168)
#  8: 18670330
#  9: 18840516
# 10: 5.75301000000e+005
# 11: Unorganized Territory
# 12: Alaska Department
# 13: AK Dept
# 14: Alaska Department (1867-03-30)

# e.g. 'ak_dept' -> 'Alaska Department'
state_names = {}
state_colors = {}
for rec in states.records():
  state_names[rec[2]] = rec[1]
  color = '#DDDDDD'
  if '_state' in rec[2]:
    color = '#EECCCC'
  state_colors[rec[1]] = color


def ExtractStateCode(shape_rec):
  """Returns 'ak', 'in', etc. from a shapeRecord"""
  return shape_rec.record[2][0:2]


def ExtractFirstDate(shape_rec):
  return shape_rec.record[4]

# year -> state_code -> SVG path
shape_changes = defaultdict(lambda: {})

# start everything off empty.
for code, name in state_names.iteritems():
  shape_changes[1780][name] = '';


# for state, it in itertools.groupby(states.shapeRecords(), ExtractStateCode):
for state, it in itertools.groupby(states.shapeRecords(), lambda x: x.record[2]):
  key = state_names[state]
  last_date = None
  for sr in sorted(it, key=ExtractFirstDate):
    shape, rec = sr.shape, sr.record

    start_date = rec[4]
    end_date = rec[5]
    shape_tools.TranslateShape(shape, +98.5795, -39.828175)
    shape_tools.ScaleShape(shape, 1.0, -1.0)
    path = shape_tools.ExtractPathSpec(shape)

    shape_changes[start_date[0]][key] = path
    last_date = end_date

  if last_date[0] != 2010:
    # Must have disappeared
    shape_changes[last_date[0]][key] = ''

rome = []
for year in sorted(shape_changes.keys()):
  rome.append([year, shape_changes[year]])

print 'var rome=%s;' % json.dumps(rome)
print 'var colors=%s;' % json.dumps(state_colors)
print 'var end_year=2010;'
