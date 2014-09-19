#!/usr/bin/python

from pyproj import Proj
from math import *
from scipy import optimize
import sys

# found manually using mapwarper.net
# (x, y] / 10, (lon, lat], error
points = [
  [ 1316.6292134831, 1047.10955056175, 19.8632812492, -34.9579953096, 21.60],
  [ 1528.1039325842, 864.83426966287, 49.306640623, -12.0393205571, 32.95],
  [ 1487.4016853942, 648.93539325853, 43.9453124982, 12.4687601443, 24.35],
  [ 1563.4971910122, 536.56179775291, 56.6894531227, 26.1948766748, 20.28],
  [ 1415.7303370796, 520.63483146077, 34.2773437486, 27.6056708255, 12.28],
  [ 2167.3946629214, 1200.18539325818, 166.8164062434, -46.255846817, 60.69],
  [ 2283.75, 1105.06601123571, 172.8808593681, -34.4937630208, 28.30],
  [ 2172.2612359555, 860.85252808973, 142.4267578067, -10.6669453731, 96.32],
  [ 1930.7022471917, 1062.15168539316, 115.0488281203, -34.1307857768, 28.51],
  [ 1153.3778089907, 455.5997191023, -5.3613281249, 35.8482125859, 16.25],
  [ 1168.8623595525, 348.977528091, -4.5703124999, 48.4249213111, 21.04],
  [ 1256.7829822403, 276.0555141516, 10.4871652098, 57.5088060832, 25.34],
  [ 1518.6930946006, 140.2338849386, 69.4617745824, 72.7862226354, 108.19],
  [ 2002.3634450457, 441.9668557291, 126.8104073926, 34.260039568, 35.98],
  [ 2037.756703473, 338.8839905611, 141.1805245794, 45.3584056081, 49.46],
  [ 833.05866976504, 1227.6971928083, -64.0440847874, -54.833532819, 46.97],
  [ 717.14574841673, 595.27822250197, -68.2628347873, 18.2909213212, 47.48],
  [ 690.6008045965, 649.25294160309, -70.8116629122, 12.1886450819, 57.74],
  [ 937.46878212459, 801.44395283905, -35.2159597886, -5.4639737796, 31.22],
  [ 710.95192819201, 926.2051887941, -70.0206472872, -18.5848023484, 42.55],
  [ 595.48142257391, 564.30912137817, -86.6319754115, 21.4316086214, 54.50],
  [ 446.38732145032, 543.95799778267, -109.7615176387, 22.6535719465, 58.83],
  [ 737.93928774245, 309.3314599848, -79.7965444658, 50.8920855889, 46.00],
  [ 448.599400102, 195.1882015579, -154.0135970498, 56.598331532, 221.64],
  [ 502.12578141531, 373.1769066418, -112.8002040758, 41.6865177735, 14.92],
  [ 136.91159602235, 557.00064259577, -153.4935634492, 18.9235199968, 96.18],
]

# The map I uploaded was scaled down. Scale back up to the full coords.
for pt in points:
  pt[0] *= 10.0
  pt[1] *= 10.0


def ProjectPoints(pts, lat_1, lon_0=0):
  p = Proj(proj='wintri', lat_1=lat_1, lon_0=lon_0)
  # p = Proj(proj='eck6', lat_1=lat_1, lon_0=lon_0)
  x_max, _ = p(180.0, 0.0)
  _, y_max = p(0.0, 90.0)
  width = 25201
  height = 15120

  ret = []
  for pt in points:
    x, y, lon, lat, _ = pt

    xp, yp = p(lon, lat)
    xp, yp = (
      (xp / (2 * x_max) + 0.5) * width,
      (0.5 - yp / (2 * y_max)) * height)
    ret.append((xp, yp))

  return ret


def Score(pts, lat_1, lon_0=0):
  err = 0.0
  for orig, proj in zip(pts, ProjectPoints(pts, lat_1, lon_0)):
    x, y, lon, lat, _ = orig
    xp, yp = proj
    
    err += (xp - x) ** 2 + (yp - y) **2

  return sqrt(1.0 * err / len(pts))


def TopWidth(width, lat_1):
  # p = Proj(proj='wintri', lat_1=lat_1)
  # p = Proj(proj='eck6', theta=lat_1)
  # p = Proj(proj='robin', lat_1=lat_1)
  # p = Proj(proj='eck4', lat_1=lat_1)
  # p = Proj(proj='wink1', lat_ts=lat_1)
  p = Proj(proj='moll')
  x_max, _ = p(180.0, 0.0)
  x1, _ = p(-180.0, lat_1)
  x2, _ = p(+180.0, lat_1)
  # x1, _ = p(-180.0, 90.0)
  # x2, _ = p(+180.0, 90.0)

  x1 = (x1 / (2 * x_max) + 0.5) * width
  x2 = (x2 / (2 * x_max) + 0.5) * width

  top_width = x2 - x1
  return top_width


def TopWidthErr(lat_1):
  return (TopWidth(2520, lat_1) - 1014) ** 2


# print TopWidth(2520, 0)
# print TopWidth(2520, 45)
# print TopWidth(2520, 90)

# res = optimize.minimize_scalar(TopWidthErr, bounds=(0.0, 90.0), method='bounded')
# assert res.success
# 
# print res
# 
# 
# sys.exit(0)

# res = optimize.minimize_scalar(lambda x: Score(points, x), bounds=(0.0, 90.0), method='bounded')
lat_1 = 47.677200891704118
res = optimize.minimize_scalar(lambda x: Score(points, lat_1, x), bounds=(-20, 20.0), method='bounded')
assert res.success

# res = optimize.minimize(lambda x: Score(points, x[0], x[1]), (45, 0), method='L-BFGS-B', bounds=[(0, 90), (-45, 45)])

print res

proj = ProjectPoints(points, res.x)
for orig, proj in zip(points, proj):
  x, y, lon, lat, _ = orig
  xp, yp = proj
  print '(%f,%f) -> %f vs. %f, %f vs. %f' % (lon, lat, xp, x, yp, y)

# print Score(points, acos(2.0/pi))

# Winkel Tripel has all its x-coordinates shifted (~700px too big)
# try verifying what the central meridian on worldhistorymaps.com is.
# -> His central meridian _is_ shifted -- Greenwich is ~800px left of it.
# -> I'd guess that his central meridian is 10-11E.

# central meridian=0    -> 58.98, RMSE 680.2
# central meridian=10.5 -> 74.91, RMSE 249.3

# optimal (lat_1, lon_0) = 73.08843286, 9.26223067 -> RMSE 232.94

# Alternatively, try eck6.
# -> optimal result: lat_1, lon_0 = 45., 9.93951767 -> RMSE 626.62

# The optimal Winkel has a top line which is way too short (starts at pixel 977
# and not 753).
# The correct top width happens at lat_1=47.7. But this has the wrong shape.
# -> worldhistorymaps.com is _not_ using Winkel Tripel.
# -> NO! It is. I just had the math wrong -- lines of latitude do not come
# through the Winkel Tripel as straight lines.

# With lat_1=47.7 and Winkel Tripel, the shapes match up perfectly.
# A central meridian of 8deg E seems to match my test points best.
