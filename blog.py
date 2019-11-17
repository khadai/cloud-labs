import os

import webapp2
import jinja2
import logging

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class VendingHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render(self, template, **kw):
        self.write(render_str(template, **kw))


def vending_key(name='default'):
    return db.Key.from_path('vendings', name)


class Vending(db.Model):
    vending_name = db.StringProperty(required=True)
    image_url = db.LinkProperty(required=False)
    address = db.StringProperty(required=True)
    latitude = db.FloatProperty(required=True)
    longitude = db.FloatProperty(required=True)
    trademarks = db.StringProperty(required=True)
    available_goods = db.IntegerProperty(required=True)
    sold_goods = db.IntegerProperty(required=True)

    def render(self):
        return render_str("vending_post.html", p=self)


class VendingsFront(VendingHandler):
    def get(self):
        posts = db.GqlQuery(
            "select * from Vending order by vending_name desc limit 10")
        self.render('front.html', posts=posts)


class NewVendingPost(VendingHandler):
    def get(self):
        self.render('new_vending.html')

    def post(self):
        vn = self.request.get('vending_name')
        img_url = self.request.get('image_url')
        lat = float(self.request.get('latitude'))
        lon = float(self.request.get('longitude'))
        adrs = self.request.get('address')
        tm = self.request.get('trademarks')
        ag = int(self.request.get('available_goods'))
        sg = int(self.request.get('sold_goods'))

        if vn and img_url and lat and lon and adrs and tm and ag and sg:
            p = Vending(parent=vending_key(), vending_name=vn, image_url=img_url, address=adrs, latitude=lat,
                        longitude=lon, trademarks=tm, available_goods=ag, sold_goods=sg)

            p.put()
            logging.warning(p)
            self.redirect('/')
        else:
            self.render('new_vending.html', vending_name=vn, image_url=img_url, address=adrs, latitude=lat,
                        longitude=lon, trademarks=tm, available_goods=ag, sold_goods=sg)


app = webapp2.WSGIApplication([('/?', VendingsFront),
                               ('/newpost', NewVendingPost),
                               ],
                              debug=True)
