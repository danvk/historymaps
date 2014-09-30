#!/usr/bin/env python
import winkel
import math
import json
import sys

pi = math.pi

w = winkel.ScaledWinkel(25201, 15120, +11.0)


def explore_winkel():
    w = winkel.Winkel()
    def show(Lambda, phi):
        x, y = w.project(Lambda, phi)
        print "%s, %s -> %s, %s" % (Lambda, phi, x, y)
    show(-pi, 0.0)
    show(+pi, 0.0)
    show(0.0, -pi/2)
    show(0.0, +pi/2)
    show(-pi, -pi/2)
    show(+pi, -pi/2)
    show(-pi, +pi/2)
    show(+pi, +pi/2)

    # Range is: x \in [-2.57079632679, 2.57079632679]
    #           y \in [-pi/2, +pi/2]

num_relative = 0

def parse_draw_string(string):
    global num_relative
    parts = string.strip().split(' ');

    def lookahead_numbers(index):
        '''Return all the numbers in a row after this index.'''
        r = []
        index += 1
        while index < len(parts):
            try:
                r.append(int(parts[index]))
            except ValueError:
                break
            index += 1
        return r

    i = 0
    tuples = []
    while i < len(parts):
        part = parts[i]
        if part in ['M', 'L', 'S']:
            nums = lookahead_numbers(i)
            tuples.append((part, nums))
            i += 1 + len(nums)
        elif part in ['m', 'l']:
            num_relative += 1
            nums = lookahead_numbers(i)
            i += 1 + len(nums)
        elif part == 'z':
            tuples.append(('z', []))
            i += 1
        else:
            raise ValueError('Unknown command: "%s" in %s' % (part, string))

    return tuples


def extremes_from_path(path):
    '''Return ((minx, miny), (maxx, maxy)) from a parsed path.'''
    minx = 1e9
    miny = 1e9
    maxx = -1e9
    maxy = -1e9
    for motion, coords in path:
        for i in range(0, len(coords), 2):
            x = coords[i]
            y = coords[i + 1]
            minx = min(x, minx)
            miny = min(y, miny)
            maxx = max(x, maxx)
            maxy = max(y, maxy)
    return ((minx, miny), (maxx, maxy))


def motions_to_lat_lons(motions):
    '''Motions is a parse d= string. Converts x,y to lat,lon.'''
    out_motions = []
    for letter, coords in motions:
        lls = []
        for i in range(0, len(coords), 2):
            x = coords[i]
            y = coords[i + 1]
            lon, lat = w.invert(x, y)
            lls.append(lat)
            lls.append(lon)
        out_motions.append((letter, lls))
    return out_motions


def convert_countries_js():
    raw_js = open('several_countries.js').read()
    data = json.loads(raw_js[raw_js.index('['):raw_js.index('\n')])

    out = []
    for year, nations in data:
        out_nations = {}
        for name, coords in nations.iteritems():
            if not coords:
                out_nations[name] = coords
            else:
                motions = parse_draw_string(coords)
                out_nations[name] = motions_to_lat_lons(motions)

        # Something isn't quite right here -- Sparta is ~10 degrees shifted
        # Also have really short polygons (2 points) for Russia at the end
        sys.stderr.write('Done with %s\n' % year)
        out.append((year, out_nations))

    print json.dumps(out)
    sys.stderr.write('# of relative motions: %s\n' % num_relative)
    # viewBox="0 0 25201 15120"


if __name__ == '__main__':
    for idx, line in enumerate(open('coords.tsv')):
        line = line.strip()
        if idx == 0:
            print '\t'.join([line] + ['invLat', 'invLon'])
            continue

        y, x, lat, lon = [float(v) for v in line.split('\t')]
        inv_lon, inv_lat = w.invert(x, y)

        print '\t'.join([line] + [str(inv_lat), str(inv_lon)])
