#!/usr/bin/python
"""
Apply a projection to a plate carree (equirectangular) image.
"""

from pyproj import Proj
from scipy import interpolate
from math import *

import numpy as np
import png
import sys

assert len(sys.argv) == 3, (
  "Usage: %s input.png output.png" % (sys.argv[0]))

infile, outfile = sys.argv[1:]

# lat_1 = 73.08843286
lat_1 = 47.677200891704118
lon_0 = 8.0
# p = Proj(proj='wink1', lat_ts=lat_1)
p = Proj(proj='wintri', lat_1=lat_1, lon_0=lon_0)
x_max, _ = p(180.0 + lon_0, 0.0)
_, y_max = p(0.0, 90.0)

# p maps from (lon, lat) -> (x, y)
num_samples = 100
lons = np.linspace(-180.0 + lon_0, 180.0 + lon_0, num_samples)
lats = np.linspace(-90.0, 90.0, num_samples)
mesh_lon, mesh_lat = np.meshgrid(lons, lats)
mesh_lon = mesh_lon.flatten()
mesh_lat = mesh_lat.flatten()

xs, ys = p(mesh_lon, mesh_lat)

print xs.shape
print mesh_lon.shape

xs = (xs / (2 * x_max) + 0.5)
ys = (0.5 - ys / (2 * y_max))

# At this point, mesh_lon[i], mesh_lat[i] -> xs[i], ys[i] (target image fractions)
print 'a'
pinv_lat = interpolate.RectBivariateSpline(xs, ys, mesh_lat)
print 'b'
pinv_lon = interpolate.RectBivariateSpline(xs, ys, mesh_lon)
print 'c'

# (pinv_lat(x, y), pinv_lon(x, y)) = lat/lon corresponding to (x, y)
# x \in [0, 1], y \in [0, 1]

x_frac = 1095.0 / 2520
y_frac = 210.0 / 1512

print 'Lon: %s' % pinv_lon(x_frac, y_frac)
print 'Lat: %s' % pinv_lat(x_frac, y_frac)


sys.exit(0)

r = png.Reader(filename=infile)
in_width, in_height, data, meta = r.read()

print meta

pixels = np.array(list(data))

out = np.zeros((1512, 2520 * 3), np.uint8)
height, width = out.shape
width /= 3

for y in xrange(0, 1511):
  # 0..1511 -> y_max .. -y_max
  y_frac = y / 1511.0
  for x in xrange(0, 2519):
    # 0..2519 -> -x_max .. x_max
    x_frac = x / 2519.0

    lon = pinv_lon(x_frac, y_frac)
    lat = pinv_lat(x_frac, y_frac)

    if abs(lon) > 180.0 or abs(lat) > 90.0:
      # does not correspond to any point.
      continue
      
    src_x = (lon + 180.0) / 360.0 * in_width
    src_y = (90.0 - lat) / 180.0 * in_height
    src_x = int(round(src_x))
    src_y = int(round(src_y))

    for c in range(0, 3):
      # print y
      # print 3 * x + c
      # print src_y
      # print 3 * src_x + c
      # print '%d,%d -> %d,%d (%d)' % (src_y, 3*src_x+c, y, 3*x+c, pixels[src_y][3*src_x+c])
      out[y][3*x+c] = pixels[src_y][3*src_x+c]

# for y, lat in enumerate(np.linspace(90.0, -90.0, 1512)):
#   x1, y1 = p(-180.0, lat)
#   x2, y2 = p(180.0, lat)
#   x1p = (x1 / (2 * x_max) + 0.5) * width
#   x2p = (x2 / (2 * x_max) + 0.5) * width
#   y1p = (0.5 - y1 / (2 * y_max)) * height
#   y2p = (0.5 - y2 / (2 * y_max)) * height
#   assert y1p == y2p
# 
#   if y1p >= 1512.0: break
#   out[y1p][:] = 0.0
#   out[y1p][x1p:x2p] = 255
  
  # print '%d %f -> %f - %f' % (y, lat, x1p, x2p)

# width: 2520
# top: 753 - 1767

w = png.Writer(width=width, height=height, planes=3, greyscale=False)
w.write(file(outfile, 'w'), out)
