#!/usr/bin/env python
import winkel
import math
import json

pi = math.pi


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

def parse_draw_string(string):
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
            nums = lookahead_numbers(i)
            i += 1 + len(nums)
        elif part == 'z':
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



if __name__ == '__main__':
    raw_js = open('several_countries.js').read()
    data = json.loads(raw_js[raw_js.index('['):raw_js.index('\n')])
    minx = 1e9
    miny = 1e9
    maxx = -1e9
    maxy = -1e9

    for year, nations in data:
        for name, coords in nations.iteritems():
            if not coords: continue
            motions = parse_draw_string(coords)
            (tminx, tminy), (tmaxx, tmaxy) = extremes_from_path(motions)
            minx = min(minx, tminx)
            miny = min(miny, tminy)
            maxx = max(maxx, tmaxx)
            maxy = max(maxy, tmaxy)

    print '(minx, miny) - (maxx, maxy) = (%s, %s) - (%s, %s)' % (
            minx, miny, maxx, maxy)
    # (minx, miny) - (maxx, maxy) = (865, 432) - (24807, 12216)
