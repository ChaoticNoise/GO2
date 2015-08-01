from requestmodel import *
import json
import time

import band

class Index(BaseHandler):

  def get(self):

    bands = []
    for b in band.get_all_bands():
      _band = {
        'key'   : b.key.urlsafe(),
        'anyone_can_manage_gigs' : b.anyone_can_manage_gigs,
        'condensed_name' : b.condensed_name,
        'created' : time.mktime(b.created.timetuple()),
        'description' : b.description,
        'hometown' : b.hometown,
        'lower_name' : b.lower_name,
        'member_links' : b.member_links,
        'name' : b.name,
        'plan_feedback' : b.plan_feedback,
        'share_gigs' : b.share_gigs,
        'shortname' : b.shortname,
        'show_in_nav' : b.show_in_nav,
        'simple_planning' : b.simple_planning,
        'thumbnail_img' : b.thumbnail_img,
        'timezone' : b.timezone,
        'website' : b.website
      }
      bands.append(_band)

    self.response.write(json.dumps(bands))
