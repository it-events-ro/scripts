#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os
import json

import pytz

import utils


NO_EVENTS_TO_FETCH = 100


with open('meetup_ids.txt') as f:
    meetup_ids = [l.strip() for l in f.readlines()]


with open('meetups.json') as f:
    meetups = json.loads(f.read())


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


_LOCAL_TZ = pytz.timezone('Europe/Bucharest')


def diff(existing_data, data):
    if existing_data is None:
        return True

    result = False
    for k in sorted(existing_data.keys() & data.keys()):
        old = existing_data.get(k, '')
        new = data.get(k, '')
        if old != new:
            print ('Difference for %s' % k)
            print ('-OLD: %s' % old)
            print ('+NEW: %s' % new)
            result = True
    return result


def print_meetup(data):
    predefined = ['title', 'venue', 'start_time', 'end_time']
    for k in predefined:
        print ('%s: %s' % (k.upper(), data[k]))

    for k in sorted(data.keys()):
        if k != 'description' and k not in predefined:
            print ('%s: %s' % (k.upper(), data[k]))

    print ('DESCRIPTION:\n%s' % data['description'])
    print ('-' * 80)
    print ()


for organizer in meetup_data['events']:
    for event in meetup_data['events'][organizer]:
        if event.get('status') != 'upcoming':
            continue
        organizer_info = meetup_data['groups'][event['group']['urlname']]
        key = 'meetup-%s-%s' % (organizer, event['id'])
        event_time = datetime.datetime.fromtimestamp(event['time'] / 1000, _LOCAL_TZ).isoformat()
        end_time = event.get('duriation')
        if end_time:
            end_time = event_time + datetime.timedelta(seconds=end_time / 1000)
        venue = event.get('venue')
        if venue:
            venue = []
            for k in ('address_1', 'address_2', 'address_3'):
                a = event['venue'].get(k, None)
                if a is None: continue
                if a in venue: continue
                if venue: venue.append(' ')
                venue.append(a)
            venue = [event['venue']['name'], ': '] + venue + [', ', event['venue']['city']]
            venue = ''.join(venue)
        data = {
            'title': event['name'],
            'description': event.get('description'),
            'link': event['link'],
            'start_time': event_time,
            'end_time': end_time,
            'venue': venue,
            'organizer': organizer_info['name'],
        }

        if data['organizer'] == 'Tabara de Testare Cluj' and 'Call for content' in data['title']:
            continue
        if data['organizer'] == 'Drupal Cluj' and data['description'] == '<p>Ne intalnim, discutam si aflam mai multe despre Drupal. :)</p> <p>Adaugati in comentarii "oferte / cereri" de prezentari.</p>':
            continue
        if data['organizer'] == 'Timisoara Agile Software Meetup' and data['description'] == '<p>The program for this meetup will be published in the week preceding the event.</p>':
            continue

        existing_data = meetups.get(key)
        if not diff(existing_data, data):
            continue
        else:
            print_meetup(data)
            s = input('Save [y/n]: ')
            if s.strip().lower() == 'y':
                meetups[key] = data
                with open('meetups.json', 'w') as f:
                    f.write(json.dumps(meetups, sort_keys=True, indent=4))
