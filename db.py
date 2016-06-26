"""Manages a SQLite database for World History Maps"""

import sqlite3

db_file = "whm.sqlite"


def create_db():
  conn, c = get_conn_cursor()
  c.execute('''create table shapes (country text, year integer, shape text, color text)''')
  conn.commit()
  c.close()


def get_conn_cursor():
  global db_file
  conn = sqlite3.connect(db_file)
  c = conn.cursor()
  return conn, c


class ShapesDb(object):
  """Common queries on a shapes DB."""
  def __init__(self):
    global db_file
    self._conn = sqlite3.connect(db_file)

  def years(self):
    """Returns an ordered list of years in the DB."""
    rows = self._conn.execute("""select year from shapes group by year order by year""")
    return [row[0] for row in rows]

  def countries(self):
    """Returns an list of country names in the DB."""
    rows = self._conn.execute("""select country from shapes group by country order by country""")
    return [row[0] for row in rows]

  def shapes_for_country(self, name):
    """Returns a list of (year, shape) tuples for the country, or None."""
    rows = self._conn.execute("""select year, shape from shapes where country = ? order by year""", (name,))
    return [(row[0], row[1]) for row in rows]

  def color_for_country(self, name):
    """Returns the fill color for the country."""
    rows = self._conn.execute("""select color, count(*) as count from shapes where country = ? group by color order by count desc""", (name,))
    colors = [r[0] for r in rows if (r[0] and r[0] != 'none')]
    if not colors:
      return 'none'
    # assert len(colors) == 1, '%s has %d colors: %s' % (name, len(colors), ', '.join(colors))
    return colors[0]

  def countries_by_span(self, limit_year=2011):
    """Returns a list of (country, span in years) tuples, ordered by decreasing
    span."""
    rows = self._conn.execute("select country, max(year) - min(year) as span from shapes where year < ? group by country order by span desc", (limit_year,))
    return [(r[0], r[1]) for r in rows]
