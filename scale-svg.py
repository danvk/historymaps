#!/usr/bin/python
"""Reads in SVG data, scaling and translating it."""

import fileinput
import re

scale = 1.0

def rep(m):
  if m.group(0).startswith('#'): return m.group(0)
  return str(int(scale * int(...)))

for line in fileinput.input():
  re.sub(r'#?\d+', lambda 
