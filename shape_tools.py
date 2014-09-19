#!/usr/bin/python
# Copyright 2012 Google Inc. All Rights Reserved.

import sys
from math import *
import json


def SplitIntoPolygons(shape):
  """Returns a list of closed polygons."""
  ret = []
  this_polygon = []
  restart_indices = set(shape.parts)
  for idx, point in enumerate(shape.points):
    if idx in restart_indices:
      if this_polygon:
        ret.append(this_polygon)
      this_polygon = [[point[0], point[1]]]
    else:
      this_polygon.append([point[0], point[1]])
  if this_polygon:
    ret.append(this_polygon)
  return ret


def AreaOfPolygon(points):
  """Calculates the area of a (closed) polygon."""
  # Note: area will be negative for clockwise shapes.
  # See http://paulbourke.net/geometry/polyarea/
  A = 0
  N = len(points)
  for i in xrange(0, N):
    x_i = points[i][0]
    y_i = points[i][1]
    x_ip1 = points[(i+1) % N][0]
    y_ip1 = points[(i+1) % N][1]
    A += (x_i * y_ip1 - x_ip1 * y_i)
  return A / 2


def CenterOfMass(points):
  """Returns a (cx, cy, A) tuple."""
  A = AreaOfPolygon(points)
  N = len(points)
  cx = 0
  cy = 0
  for i in xrange(0, N):
    x_i = points[i][0]
    y_i = points[i][1]
    x_ip1 = points[(i+1) % N][0]
    y_ip1 = points[(i+1) % N][1]
    part = (x_i * y_ip1 - x_ip1 * y_i)
    cx += ((x_i + x_ip1) * part)
    cy += ((y_i + y_ip1) * part)
  return (cx/(6*A), cy/(6*A), abs(A))


def CenterOfMassForShape(shape):
  """Returns a (cx, cy) tuple for a set of polygons."""
  polygons = SplitIntoPolygons(shape)
  total_A = 0
  total_cx = 0
  total_cy = 0

  for polygon in polygons:
    cx, cy, A = CenterOfMass(polygon)
    total_cx += A * cx
    total_cy += A * cy
    total_A += A

  return (total_cx / total_A, total_cy / total_A)


def NameField(reader):
  """reader.shapeRecord(i).record[NameField(reader)] == 'Zimbabwe'."""
  name_field = [i for i,v in enumerate(reader.fields) if v[0] == 'NAME'][0]
  return name_field - 1


def ExtractCountry(reader, country_name):
  name_field = NameField(reader)
  recs = [rec for rec in reader.shapeRecords()
          if rec.record[name_field] == country_name]
  assert len(recs) == 1
  return recs[0]


def ExtractAllCountries(reader):
  """Returns a country name -> ShapeRecord dict."""
  name_field = NameField(reader)
  ret = {}
  for rec in reader.shapeRecords():
    name = rec.record[name_field]
    name_u = unicode(name, 'cp1252')
    ret[name_u.encode('utf-8')] = rec
  return ret


def ExtractPlaces(places, name_field):
  """Returns a place name -> ShapeRecord dict for Places.shp."""
  ok_places = {
      'New York': 'New York City',
      'San Francisco': 'San Francisco',
      'New York County': 'Manhattan',
      'Queens County': 'Queens',
      'Kings County': 'Brooklyn',
      'Bronx County': 'The Bronx',
      'Richmond County': 'Staten Island'
  }
  ret = {}
  for i, rec in enumerate(places.shapeRecords()):
    name = rec.record[name_field]
    if name not in ok_places: continue
    
    real_name = ok_places[name]

    sys.stderr.write('%6d %s: %s\n' % (i, real_name, rec.shape))
    ret[real_name] = rec
  return ret


def ExtractPathSpec(shape):
  """Assemble the SVG "d" path specification."""
  d = ""
  for polygon in SplitIntoPolygons(shape):
    d += "M "
    for point in polygon:
      d += ' %f %f' % (point[0], point[1])
  d += "z"
  return d


def TranslateShape(shape, dx, dy):
  """Modifies a shape object's points array."""
  for i, point in enumerate(shape.points):
    shape.points[i] = [ point[0] + dx, point[1] + dy ]


def GetShapeBoundingBox(shape):
  """Returns a {x, y, w, h} dict. (x, y) is the NW corner."""
  x, y = shape.points[0]
  x_low, x_high = x, x
  y_low, y_high = y, y

  for x, y in shape.points[1:]:
    x_low = min(x, x_low)
    x_high = max(x, x_high)
    y_low = min(y, y_low)
    y_high = max(y, y_high)

  return {
    'x': x_low,
    'w': x_high - x_low,
    'y': y_low,
    'h': y_high - y_low
  }


def ScaleShape(shape, scale_x, scale_y):
  """Scales a shape by different amounts in x & y directions."""
  for i, pt in enumerate(shape.points):
    x, y = pt
    shape.points[i] = [scale_x * x, scale_y * y]
