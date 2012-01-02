#!/usr/bin/python

import db

shapes = db.ShapesDb()
#print ', '.join([str(x) for x in shapes.years()])
print '\n'.join([x for x in shapes.countries()])
#print '\n'.join([str(x) for x in shapes.shapes_for_country('Rome')])
