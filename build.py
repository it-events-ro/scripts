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


def populateFromMeetups(meetups, events, locations, organizations):
    for group_events in meetups['events'].values():
        for e in group_events:
            venue = e.get('venue', None)
            if venue:
                venue_id = 'mtup-vne-%s' % e['venue']['id']

            events.append(dict(
                event_id='mtup-%s' % e['id'],
                name=e['name'],
                description=bs4.BeautifulSoup(e.get('description', ''), 'html5lib').prettify(),
                link=e['link'],
                venue_id=venue_id if venue else None,
                organizer_id = 'mtup-grp-%s' % e['group']['id'],
                time=datetime.datetime.fromtimestamp(int(e['time']) // 1000, tz=_LOCAL_TZ),
                duration=datetime.timedelta(milliseconds=int(e.get('duration', _DEFAULT_DURATION))),
            ))

            if venue:
                locations[venue_id] = dict(
                    address=_composeMeetupVenueAddress(venue),
                    lat=venue['lat'],
                    lon=venue['lon'],
                    name=venue['name'],
                )


def sortedEvents(events):
    return sorted(events, key=lambda e: (e['time'], e['name'], e['event_id']))


def renderTo(path, template, context):
    path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    path.write_bytes(template.render(context).encode('utf-8'))


def slugify(v):
    v = v.lower()
    v = re.sub(r'[^a-z0-9\-]+', '-', v)
    v = re.sub(r'-{2,}', '-', v)
    v = v.strip('-').rstrip('-')
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


print('Loading meetups.json...')
with open('meetups.json', 'r') as f:
    meetups = json.loads(f.read())

events, locations, organizations = [], {}, {}
populateFromMeetups(meetups, events, locations, organizations)

for event in events:
    event['url'] = (
        '/eveniment/%s/%s-%s.html' % (event['time'].strftime('%Y/%m'), event['event_id'],
        slugify(event['name']))
    )

template_loader = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'), extensions=['jinja2.ext.autoescape'],
    autoescape=True)

template_loader.filters['datetime'] = formatDatetime

print('Writing events...')
event_template = template_loader.get_template('event.html')
for event in events:
    renderTo(target_dir / event['url'][1:], event_template, event)

events_by_year_month = collections.defaultdict(list)
events_by_year_week = collections.defaultdict(list)

for event in events:
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
excluded_pages_from_sitemap = frozenset(['/index.html', '/404.html'])
page_relative_paths = sorted([
    p for p in page_relative_paths if p not in excluded_pages_from_sitemap])
renderTo(
    target_dir / 'sitemap.xml',
    template_loader.get_template('sitemap.xml'),
    dict(pages=page_relative_paths))

