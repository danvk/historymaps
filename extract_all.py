#!/usr/bin/python

from BeautifulSoup import BeautifulSoup
import re
import whm


ordered_files = whm.ordered_map_files()

for f in ordered_files:
  svg = whm.SvgFile(f)
  print '%+4d: %d' % (svg.year(), len(svg.countries()))

