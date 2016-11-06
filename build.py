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

