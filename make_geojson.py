#!/usr/bin/env python

import undo_winkel
import db
import sys
import json


def make_feature(country, year, path):
    assert path, 'Missing path for %s' % country
    coordinates = undo_winkel.shape_to_coords(path)
    return {
        'type': 'Feature',
        'properties': {
            'country': country,
            'year': year
        },
        'geometry': {
            'type': 'Polygon',
            'coordinates': coordinates
        }
    }


def main():
    year = sys.argv[1]
    countries = sys.argv[2:]

    shapes_db = db.ShapesDb()
    features = [
        make_feature(country, year, shapes_db.shape_for_country_year(country, year))
        for country in countries]

    print json.dumps({
        'type': 'FeatureCollection',
        'features': features
    })


if __name__ == '__main__':
    main()
