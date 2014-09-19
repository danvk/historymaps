"""
A class to help deal with the Winkel Tripel projection.
"""

from pyproj import Proj

class Winkel(object):
  def __init__(self, lat_1, lon_0, width, height):
    """Initialize the Winkel projection onto a width x height surface."""
    self.p = Proj(proj='wintri', lat_1=lat_1, lon_0=lon_0)
    self.width = width
    self.height = height

    self.x_max, _ = self.p(180.0 + lon_0, 0.0)
    _, self.y_max = self.p(0.0, 90.0)


  def XYToLonLat(self, xs, ys):
    """Project x, y -> lon, lat (can be ndarrays or scalars)."""
