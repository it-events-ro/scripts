#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

import utils


print('Fetching all likes for ItEventsRo as a starting point')
likes = utils.facebookApi('ItEventsRo/likes', paginate=True)


def _getFromNestedDict(d, *keys):
  r = d
  for k in keys:
    r = r.get(k, None)
    if r is None: return None
  return r


fb = dict(events=[], orgs={})
def _getOrgAndEvents(like):
  fb_id = like['id']

  events = utils.facebookApi(
    '%s/events?fields=description,name,start_time,end_time,ticket_uri,place,id&'
    'since=2010-11-01T00:00:00' % fb_id, paginate=True)
  events = [
    e for e in events
    if _getFromNestedDict(e, 'place', 'location', 'country') == 'Romania'
  ]
  if not events: return

  for event in events:
    event['org_id'] = fb_id
  fb['events'] += events

  fb['orgs'][fb_id] = utils.facebookApi(
    '%s?fields=name,birthday,cover,description' % fb_id, paginate=False) 
utils.repeat(likes, 'Getting info for %s', _getOrgAndEvents)

with open('facebooks.json', 'w') as f:
  f.write(json.dumps(fb, sort_keys=True, indent=4))

