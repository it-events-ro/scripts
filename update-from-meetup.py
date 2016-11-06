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

def _getEvents(meetup_id):
  data = utils.meetupApi(
    '%s/events?&page=%d&status=upcoming' % (meetup_id, NO_EVENTS_TO_FETCH)) #past,upcoming
  if not isinstance(data, list):
    print('!!! Unexpected shape of response for %s:\n%s' % (meetup_id, data))
    return
  meetup_data['events'][meetup_id] = data
utils.repeat(meetup_ids, 'Getting events for %s', _getEvents)

def _getGroupInfo(group_urlid):
  data = utils.meetupApi(group_urlid)
  meetup_data['groups'][group_urlid] = data
group_urlids = sorted(
  set(e['group']['urlname'] for events in meetup_data['events'].values() for e in events))
utils.repeat(group_urlids, 'Getting group info for %s', _getGroupInfo)


with open('meetups.json', 'w') as f:
  f.write(json.dumps(meetup_data, sort_keys=True, indent=4))

