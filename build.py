#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections
import datetime
import json
import glob
import pathlib
import re
import shutil
import sys

import babel.dates
import bs4
import dateutil.parser
import jinja2
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


def populateFromMeetups(events, locations, organizations):
    print('Loading meetups.json...')
    with open('meetups.json', 'r') as f:
        meetups = json.loads(f.read())

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


def parseTime(date_str):
    return dateutil.parser.parse(date_str).astimezone(_LOCAL_TZ)


def populateFromEventbrite(events, locations, organizations):
    print('Loading eventbrites.json...')
    with open('eventbrites.json', 'r') as f:
        eventbrites = json.loads(f.read())

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


def populateFromFacebook(events, locations, organizations):
    print('Loading facebooks.json...')
    with open('facebooks.json', 'r') as f:
        facebooks = json.loads(f.read())

    existing_event_urls = {e['link'] for e in events.values()}

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
        if link in existing_event_urls:
            print ('Skipping already known event: %s' % link)
            continue

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



def sortedEvents(events):
    return sorted(events, key=lambda e: (e['time'], e['name']))


def renderTo(path, template, context):
    path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    path.write_bytes(template.render(context).encode('utf-8'))


def slugify(v):
    v = v.lower()
    v = re.sub(r'[^a-z0-9\-]+', '-', v)
    v = re.sub(r'-{2,}', '-', v)
    v = v.strip('-').rstrip('-')
    v = v[:72]
    return v


def formatDatetime(d):
    return babel.dates.format_date(d, format='full', locale='ro')


target_dir = pathlib.Path(sys.argv[1])
print('Cleaning directory...')
ignore_during_clean = frozenset(['.git', 'CNAME'])
for p in target_dir.iterdir():
    if p.name in ignore_during_clean:
        continue
    if p.is_dir():
        shutil.rmtree(str(p), ignore_errors=True)
    else:
        p.unlink()

print('Copying assets...')
for p in pathlib.Path('assets').iterdir():
    target = str(target_dir / p.name)
    if p.is_dir():
        shutil.copytree(str(p), target)
    else:
        shutil.copy2(str(p), target)


events, locations, organizations = {}, {}, {}
populateFromMeetups(events, locations, organizations)
populateFromEventbrite(events, locations, organizations)
populateFromFacebook(events, locations, organizations)

for event_id, event in events.items():
    event['url'] = (
        '/eveniment/%s/%s-%s.html' % (event['time'].strftime('%Y/%m'), event_id,
        slugify(event['name']))
    )

for location_id, location in locations.items():
    location['url'] = '/locatie/%s' % slugify('%s-%s' % (location_id, location['name']))

for org_id, org in organizations.items():
    org['url'] = '/organizatie/%s' % slugify('%s-%s' % (org_id, org['name']))


now = datetime.datetime.now(tz=_LOCAL_TZ)
for event_id, event in events.items():
    past = event['time'] < now
    if event['venue_id'] is not None:
        # some events have yet to decide their venue
        locations[event['venue_id']]['event_ids']['past' if past else 'future'].append(event_id)
    organizations[event['organizer_id']]['event_ids']['past' if past else 'future'].append(event_id)

# TODO: sort future events in chronological order and past events in reverse chronological order

template_loader = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'), extensions=['jinja2.ext.autoescape'],
    autoescape=True)

template_loader.filters['datetime'] = formatDatetime

print('Writing events...')
event_template = template_loader.get_template('event.html')
for event in events.values():
    renderTo(target_dir / event['url'][1:], event_template, event)

events_by_year_month = collections.defaultdict(list)
events_by_year_week = collections.defaultdict(list)

for event in events.values():
    key = event['time'].strftime('%Y-%m')
    events_by_year_month[key].append(event)
    key = event['time'].strftime('%Y-%U')
    events_by_year_week[key].append(event)

print('Writing event lists...')
event_list_template = template_loader.get_template('event_list.html')
for key, events in events_by_year_month.items():
    events = sortedEvents(events)
    renderTo(target_dir / 'evenimente' / (key + '.html'), event_list_template, dict(events=events))

key = datetime.datetime.now().strftime('%Y-%m')
events = sortedEvents(events_by_year_month[key])
renderTo(target_dir / 'index.html', event_list_template, dict(events=events))

print('Writing sitemap.xml...')
prefix_length = len(str(target_dir))
page_relative_paths = [str(p)[prefix_length:] for p in target_dir.glob('**/*.html')]
excluded_pages_from_sitemap = frozenset(['/index.html', '/404.html', '/google0302201fa5fdf331.html'])
page_relative_paths = sorted([
    p for p in page_relative_paths if p not in excluded_pages_from_sitemap])
renderTo(
    target_dir / 'sitemap.xml',
    template_loader.get_template('sitemap.xml'),
    dict(pages=page_relative_paths))

