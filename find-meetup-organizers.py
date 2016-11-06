#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils


with open('meetup_ids.txt', 'r') as f:
  for meetup_id in f:
    info = utils.meetupApi(meetup_id)
    if not 'organizer' in info:
      continue
    print('\t'.join([
      info['name'], info['organizer']['name'], '%smembers/%s' % (info['link'], info['organizer']['id'])]
    ))

