#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json

import utils


NO_EVENTS_TO_FETCH = 100


with open('meetup_ids.txt') as f:
  meetup_ids = [l.strip() for l in f.readlines()]


meetup_data = {
  'events': {},
  'groups': {},
}

for i, meetup_id in enumerate(meetup_ids):
  print('Getting events for %s (%d/%d)' % (meetup_id, i+1, len(meetup_ids)))
  try:
    data = utils.meetupApi(
      '/%s/events?&page=%d&status=past,upcoming' % (meetup_id, NO_EVENTS_TO_FETCH))
    if not isinstance(data, list):
      print('!!! Unexpected shape of response for %s:\n%s' % (meetup_id, data))
      continue
    meetup_data['events'][meetup_id] = data
  except Exception as e:
    print('There was an error processing %s: %s' % (meetup_id, e))


group_urlids = sorted(
  set(e['group']['urlname'] for events in meetup_data['events'].values() for e in events))
for i, group_urlid in enumerate(group_urlids):
  print('Getting group info for %s (%d/%d)' % (group_urlid, i+1, len(group_urlids)))
  data = utils.meetupApi(group_urlid)
  meetup_data['groups'][group_urlid] = data


with open('meetups.json', 'w') as f:
  f.write(json.dumps(meetup_data, sort_keys=True, indent=4))

