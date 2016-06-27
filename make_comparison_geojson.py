#!/usr/bin/env python
'''
Generate a GeoJSON file that compares the US from WorldHistoryMaps with
a projected USA from Natural Earth Data.
'''

import json
import winkel

natural_usa = json.load(open('/tmp/usa.geojson'))['features'][0]
projected_usa = json.load(open('/tmp/america.projected.geojson'))['features'][0]

w = winkel.ScaledWinkel(25201, 15120, +11.0)

def map_coordinates(coordinates, fn):
    if isinstance(coordinates[0], float):
        return fn(coordinates)
    elif isinstance(coordinates[0][0], float):
        return [fn(xy) for xy in coordinates]
    else:
        return [map_coordinates(xys, fn) for xys in coordinates]


def map_feature(feature, fn):
    return {
        'type': feature['type'],
        'properties': feature['properties'],
        'geometry': {
            'type': feature['geometry']['type'],
            'coordinates': map_coordinates(feature['geometry']['coordinates'], fn)
        }
    }

natural_usa_projected = map_feature(natural_usa, w)