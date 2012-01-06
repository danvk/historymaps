#!/usr/bin/env python
# $Id: subdiv.py,v 1.5 2005/06/27 15:29:09 migurski Exp $

import sys, math
from PowersOfTwo import tile, prepare, subdivide

# start at the top...
subdivide(prepare(sys.argv[-1], chatty=True), filename='tiles/tile-%d-%d-%d.png')
