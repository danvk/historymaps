#!/usr/bin/python

import db
import sys
import re
import json
from collections import defaultdict

first_year = -390
last_year = 1600
countries = {
  'Rome': 'Rome',
  'West Rome': 'Rome',
  'East Rome': 'Byzantium',
  'Byzantium': 'Byzantium',
  'Parthia': 'Parthia',
  'Arabia': 'Arabia',
  'Turkey': 'Ottomans',
  'Osman': 'Ottomans',
  'Francia': 'HRE',
  'East Francia': 'HRE',
  'Persia': 'Persia'
}

shapes = db.ShapesDb()

country_shapes = {}  # name -> year -> shape
for key, name in countries.iteritems():
  key_shapes = shapes.shapes_for_country(key)
  if name not in country_shapes:
    country_shapes[name] = {}

  data = country_shapes[name]  # year -> shape
  for year, shape in key_shapes:
    if year not in data:
      data[year] = shape
    else:
      assert (data[year] == '' or shape == '')
      if shape:
        data[year] = shape


hash_data = defaultdict(lambda : defaultdict(str))  # year -> name -> shape
for name, data in country_shapes.iteritems():
  hash_data[min(data.keys()) - 1][name] = ''  # year before it existed.
  for year, shape in data.iteritems():
    hash_data[year][name] = shape


array_data = []
for year in sorted(hash_data.keys()):
  array_data.append([year, hash_data[year]])

print 'var rome = ',
print json.dumps(array_data, separators=(',',':'))
