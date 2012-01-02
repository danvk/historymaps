#!/usr/bin/python2.7

import db
import os

if not os.path.exists(db.db_file):
  db.create_db()

conn, c = db.get_conn_cursor()
conn.commit()
c.close()

