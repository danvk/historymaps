#!/usr/bin/python
"""Module for interacting w/ worldhistorymaps.com SVG files."""

from BeautifulSoup import BeautifulSoup
from datetime import datetime
import re
import glob

def filename_to_year(name):
  """Name is something like worldhistorymaps/html/WA2000.svg
  Returns 2000, -50, etc."""
  m = re.search(r'W([AB])(\d{4})\.svg', name)
  assert m
  ab = m.group(1)
  y = int(m.group(2))
  return (-1 if ab == 'B' else 1) * y


def ordered_map_files(html_dir="worldhistorymaps/html"):
  """Returns a list of SVG files ordered by year."""
  return sorted(glob.glob(html_dir + '/W?????.svg'), key=filename_to_year)


def parse_year_range(year_range):
  """Takes "232 - 25BCE" and returns [-232, -25]."""
  # note: this eliminates any uncertainty, like 'c500BCE - c200'.
  year_range = year_range.replace('c', '')
  year_range = year_range.replace('Present', str(datetime.now().year))
  parts = year_range.split(' - ')
  assert 2 == len(parts)
  y1 = parts[0].replace('BCE', '')
  y2 = parts[1].replace('BCE', '')
  ys = [int(y1), int(y2)]
  if y1 != parts[0]:
    ys[0] *= -1
  elif y2 != parts[1]:
    ys[0] *= -1
    ys[1] *= -1
  return ys


def contains_year_range(s):
  """Checks if there is a year range in s."""
  ms = [m for m in re.finditer(r'c?(Present|[0-9]+(BCE)?) - c?(Present|[0-9]+(BCE)?)', s)]
  if not ms: return False
  return True


def parse_title(t):
  if t[-1] == '.': t = t[:-1]
  r = {}
  parts = re.split(r'(c?(?:Present|[0-9]+(?:BCE)?) - c?(?:Present|[0-9]+(?:BCE)?))', t)
  parts = [re.sub(r'^[ ,]*|[ ,]*$', '', p) for p in parts]
  parts = [p for p in parts if p]

  r['name'] = parts[0]
  if len(parts) > 1:
    r['years'] = parse_year_range(parts[1])
    if len(parts) > 2:
      r['dynasty'] = parts[2]
      if len(parts) > 3:
        r['dynasty_years'] = parse_year_range(parts[3])

  return r


# tests = [
# "Magadha, 1000BCE - 733."
# , "Chios"
# , "Dasarna, 1000BCE - 100."
# , "Indo Parthia, 87BCE - 45."
# , "Persia, 646BCE - 1353, Achaemenid Dynasty 559 - 330BCE."
# , "Magadha, 1000BCE - 733, Haryanka Dynasty c575 - c410BCE."
# , "Africa, Autonomous Province, 800 - 909, Aghlabid Dynasty 800 - 909"
# ]


class SvgFile(object):
  def __init__(self, filename):
    self._bs = BeautifulSoup(file(filename))
    self._filename = filename
    self._countries = self.country_info()

  def year(self):
    """Returns the year as an integer (i.e. 50BC = -50, 2000AD = 2000)"""
    return filename_to_year(self._filename)

  def country_info(self):
    """Returns dicts w/ these keys:
      'id', 'x', 'y', 'font-size', 'name', 'years', 'dynasty', 'dynasty_years'
    """
    countries = []
    title_text_tags = [t.parent for t in self._bs('title')]
    for t in title_text_tags:
      entry = {}
      entry['id'] = t['id']
      entry['x'] = int(t['x'])
      entry['y'] = int(t['y'])

      # t could be either:
      # <text><title>Dasarna, 1000BCE - 100.</title>Dasarna</text>
      # <text><title>Indo Parthia, 87BCE - 45.</title><tspan>Indo</tspan><tspan>Parthia</tspan></text>
      entry['name'] = ' '.join([x.string for x in t.contents[1:]])

      title_entry = parse_title(t.title.string)
      assert title_entry['name'] == entry['name'], '"%s" vs "%s"' % (title_entry['name'], entry['name'])
      for field in ['years', 'dynasty', 'dynasty_years']:
        if field in title_entry: entry[field] = title_entry[field]

      countries.append(entry)

    return countries

  def countries(self):
    """Returns a list of country names in this file.
    
    These are short names next to <title> tags, e.g. the "Chile" in:
    <text id="30439416" x="7201" y="10618" font-size="15">
      <title>Chile, 1818 - Present</title>
      Chile
    </text>
    """
    return [c['name'] for c in self._countries]

