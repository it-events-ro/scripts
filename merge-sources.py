#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json

import pytz


_LOCAL_TZ = pytz.timezone('Europe/Bucharest')
_DEFAULT_DURATION = str(int(datetime.timedelta(hours=3).total_seconds()) * 1000)


def _composeMeetupVenueAddress(venue):
    result = []
    for k in ('address_1', 'address_2', 'address_3'):
        a = venue.get(k, None)
        if a is None: continue
        if a in result: continue
        if result: result.append(' ')
        result.append(a)
    result += [', ', venue['city']]
    return ''.join(result)


def loadMeetups():
    print('Loading meetups.json...')
    with open('meetups.json', 'r') as f:
        meetups = json.loads(f.read())

    events, locations, organizations = {}, {}, {}
    for group_events in meetups['events'].values():
        for e in group_events:
            venue = e.get('venue', None)
            if venue:
                venue_id = 'mtup-vne-%s' % e['venue']['id']

            event_id = 'mtup-%s' % e['id']
            if event_id in events:
                # the same event can appear in multiple organizations?
                continue

            events[event_id] = dict(
                name=e['name'],
                description=bs4.BeautifulSoup(e.get('description', ''), 'html5lib').prettify(),
                link=e['link'],
                venue_id=venue_id if venue else None,
                organizer_id = 'mtup-grp-%s' % e['group']['id'],
                time=datetime.datetime.fromtimestamp(int(e['time']) // 1000, tz=_LOCAL_TZ),
                duration=datetime.timedelta(milliseconds=int(e.get('duration', _DEFAULT_DURATION))),
            )

            if venue:
                locations[venue_id] = dict(
                    address=_composeMeetupVenueAddress(venue),
                    lat=venue['lat'],
                    lon=venue['lon'],
                    name=venue['name'],
                    event_ids=dict(past=[], future=[]),
                )

    for group in meetups['groups'].values():
        organizer_id = 'mtup-grp-%s' % group['id']
        assert organizer_id not in organizations
        organizations[organizer_id] = dict(
            name=group['name'],
            description=group['description'],
            link=group['link'],
            event_ids=dict(past=[], future=[]),
        )

    return events, locations, organizations


def parseTime(date_str):
    return dateutil.parser.parse(date_str).astimezone(_LOCAL_TZ)


def loadEventbrite():
    print('Loading eventbrites.json...')
    with open('eventbrites.json', 'r') as f:
        eventbrites = json.loads(f.read())

    events, locations, organizations = {}, {}, {}
    for e in eventbrites['events']:
        event_id = 'evtbt-%s' % e['id']
        assert event_id not in events

        start_time = parseTime(e['start']['utc'])
        end_time = parseTime(e['end']['utc'])
        events[event_id] = dict(
            name=e['name']['text'],
            description=bs4.BeautifulSoup(e['description']['html'] or '', 'html5lib').prettify(),
            link=e['url'],
            venue_id='evtbt-vne-%s' % e['venue_id'],
            organizer_id = 'evtbt-org-%s' % e['organizer_id'],
            time=start_time,
            duration=end_time - start_time,
        )

    for org in eventbrites['orgs'].values():
        organizer_id = 'evtbt-org-%s' % org['id']
        assert organizer_id not in organizations
        organizations[organizer_id] = dict(
            name=org['name'],
            description=bs4.BeautifulSoup(org['description']['html'] or '', 'html5lib').prettify(),
            link=org.get('website') or org['url'],
            event_ids=dict(past=[], future=[]),
        )

    for venue in eventbrites['venues'].values():
        venue_id = 'evtbt-vne-%s' % venue['id']
        assert venue_id not in locations
        locations[venue_id] = dict(
            address=venue['address']['localized_address_display'],
            lat=venue['latitude'],
            lon=venue['longitude'],
            name=venue['name'],
            event_ids=dict(past=[], future=[]),
        )

    return events, locations, organizations


def loadFacebook():
    print('Loading facebooks.json...')
    with open('facebooks.json', 'r') as f:
        facebooks = json.loads(f.read())

    events, locations, organizations = {}, {}, {}
    for event in facebooks['events']:
        venue_id = 'fb-vne-%s' % event['place']['id']

        start_time = parseTime(event['start_time'])
        if 'end_time' in event:
            end_time = parseTime(event['end_time'])
        else:
            end_time = start_time + datetime.timedelta(milliseconds=int(_DEFAULT_DURATION))

        event_id = 'fb-%s' % event['id']
        if event_id in events:
            # event can be shared by multiple pages
            continue

        link = event.get('ticket_uri') or 'https://www.facebook.com/events/%s' % event['id']
        events[event_id] = dict(
            name=event['name'],
            description=event.get('description'),
            link=link,
            venue_id=venue_id,
            organizer_id = 'fb-org-%s' % event['org_id'],
            time=start_time,
            duration=end_time - start_time,
        )

        venue = event['place']
        if 'street' in venue['location']:
            venue_location = '%s, %s' % (venue['location']['street'], venue['location']['city'])
        else:
            venue_location = venue['location']['city']
        locations[venue_id] = dict(
            address=venue_location,
            lat=venue['location'].get('latitude'),
            lon=venue['location'].get('longitude'),
            name=venue['name'],
            event_ids=dict(past=[], future=[]),
        )

    for group in facebooks['orgs'].values():
        organizer_id = 'fb-org-%s' % group['id']
        assert organizer_id not in organizations
        organizations[organizer_id] = dict(
            name=group['name'],
            description=group.get('description'),
            link='https://www.facebook.com/%s' % group['id'],
            event_ids=dict(past=[], future=[]),
        )

    return events, locations, organizations


events, locations, organizations = {}, {}, {}
populateFromMeetups(events, locations, organizations)
populateFromEventbrite(events, locations, organizations)
populateFromFacebook(events, locations, organizations)

