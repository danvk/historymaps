from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import simplejson as json
import logging
import os


class Rectification(db.Model):
  # key = image URL
  data = db.BlobProperty()  # JSON-encoded. See rectify.js


class RectifyPage(webapp.RequestHandler):
  def get(self):
    """Only param is "image_url"."""
    url = self.request.get('image_url')
    if not url:
      self.ReplyUrlList()
      return

    # config = db.create_config(read_policy=db.EVENTUAL_CONSISTENCY)
    r = Rectification.get_by_key_name(url)  #, config)

    pairs = []
    if r:
      data = json.loads(r.data)
      pairs = data['pairs']
    else:
      r = Rectification(key_name = url)
      r.data = json.dumps({'image': url, 'pairs': []})
      r.put()

    template_values = {
      'image_url': url,
      'pairs': pairs
    }
    path = os.path.join(os.path.dirname(__file__), 'rectify/index.html')
    self.response.out.write(template.render(path, template_values))

  def ReplyUrlList(self):
    template_values = {
      'urls': []
    }

    query = db.Query(Rectification, keys_only = True)
    for r in query:
      template_values['urls'].append(r.name())

    path = os.path.join(os.path.dirname(__file__), 'rectify/list.html')
    self.response.out.write(template.render(path, template_values))


class RecordRectification(webapp.RequestHandler):
  def post(self):
    data_json = self.request.get('data');
    data = json.loads(data_json)

    r = Rectification(key_name = data['image'])
    r.data = json.dumps(data)
    r.put()

    self.response.out.write('OK')


application = webapp.WSGIApplication(
    [
     ('/rectify', RectifyPage),
     ('/update_rectification', RecordRectification),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

