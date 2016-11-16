#!/usr/bin/env python
import datetime
import sys

import babel.dates
import dateutil.parser
from pyquery import PyQuery as pq


now = datetime.datetime.now()
week_delta = int(sys.argv[1])
now += datetime.timedelta(days=week_delta * 7)
# TODO: shorten the dates if start/end month/year are the same
# ie: Din 7 pana 13 noiembrie 2016
# instead of: Din 7 noiembrie 2016 până 13 noiembrie 2016
week_start = (now - datetime.timedelta(days=now.weekday())).date()
week_end = week_start + datetime.timedelta(days=6)


comunitatea_saptamanii_name = input('Comunitatea săptămânii (nume): ')
comunitatea_saptamanii_href = input('Comunitatea săptămânii (href): ')

def extractLinks(url):
    d = pq(url=url)
    result = []
    for a in d('a'):
        href = a.attrib.get('href', '')
        if 'evenimenteit.ro' in href:
            result.append(href)
    return frozenset(result)


def getEventLinks():
    event_links = set()
    for event_type in ('current', 'upcoming'):
        print('Fetching %s events' % event_type)
        links = extractLinks('https://evenimenteit.ro/?etype=%s' % event_type)
        event_links.update([l for l in links if 'evenimenteit.ro/event/' in l])

        pages = [l for l in links if 'evenimenteit.ro/page/' in l]
        for p in pages:
            print('Fetching page %s' % p)
            event_links.update([l for l in extractLinks(p) if 'evenimenteit.ro/event/' in l])

    return event_links

def extract(prefix, nodes):
    text = nodes[0].text_content()
    assert text.startswith(prefix)
    return text[len(prefix):]


events = {k: [] for k in ('cluj', 'iasi', 'buc', 'timis', 'oradea', 'other-altele')}

event_links = getEventLinks()
for idx, url in enumerate(event_links):
    print('Fetching %d/%d: %s' % (idx + 1, len(event_links), url))
    d = pq(url=url)
    title = d('h1.entry-title')[0].text_content()
    date = extract('STARTING DATE', d('p.date'))
    date = dateutil.parser.parse(date).date()
    location = extract('LOCATION', d('p.location'))
    event = (url, title, date, location)

    if date < week_start or date > week_end:
        continue

    location_norm = location.lower().replace('timiș', 'timis')
    for k in events.keys():
        if k not in location_norm:
            continue
        events[k].append(event)
        break
    else:
        events['other-altele'].append(event)



location_names = {
    'cluj': 'Cluj',
    'iasi': 'Iași',
    'buc': 'București',
    'timis': 'Timiș',
    'oradea': 'Oradea',
    'other-altele': 'România',
}
assert location_names.keys() == events.keys()


class BaseFormatter(object):
    def __init__(self):
        self.week_index = now.isocalendar()[1]
        self.year = now.year
        self.week_start = babel.dates.format_date(week_start, format='long', locale='ro')
        self.week_end = babel.dates.format_date(week_end, format='long', locale='ro')

    def __printEventsIn(self, events, location):
        if not events[location]:
            return
        title = (
            'Alte evenimente în România' if location == 'other-altele'
            else 'Evenimente în %s:' % location_names[location])
        print(title)
        print()
        local_events = sorted(events[location], key=lambda e: (e[2], e[1]))
        self.printEvents([(event[0], event[1]) for event in local_events])
        print()

    def printAll(self, events):
        print('-' * 80)
        self.printTitle()
        print()
        self.printSubtitle()
        print()

        for k in sorted(location_names.keys()):
            if k != 'other-altele':
                self.__printEventsIn(events, k)
        self.__printEventsIn(events, 'other-altele')

        print()
        self.printComunitateaSaptamanaii()


class WordpressFormatter(BaseFormatter):
    def printTitle(self):
        print('Evenimentele săptămânii %d din %d' % (self.week_index, self.year))

    def printSubtitle(self):
        print('<em>Din %s până %s</em>' % (self.week_start, self.week_end))

    def printEvents(self, events):
        print('<ul>')
        for url, title in events:
            print('  <li><a href="%s">%s</a></li>' % (url, title))
        print('</ul>')

    def printComunitateaSaptamanaii(self):
        print(
            'Comunitatea săptămâni - interviu exclusiv: <a href="%s">%s</a>'
            % (comunitatea_saptamanii_href, comunitatea_saptamanii_name))


class RedditFormatter(BaseFormatter):
    def printTitle(self):
        print('Evenimentele săptămânii %d din %d' % (self.week_index, self.year))

    def printSubtitle(self):
        print('_Din %s până %s_' % (self.week_start, self.week_end))

    def printEvents(self, events):
        for url, title in events:
            print('  * [%s](%s)' % (title, url))

    def printComunitateaSaptamanaii(self):
        print(
            'Comunitatea săptămâni - interviu exclusiv: [%s](%s)'
            % (comunitatea_saptamanii_name, comunitatea_saptamanii_href))


class FacebookFormatter(BaseFormatter):
    def printTitle(self):
        print('Evenimentele săptămânii %d din %d' % (self.week_index, self.year))

    def printSubtitle(self):
        print('Din %s până %s' % (self.week_start, self.week_end))

    def printEvents(self, events):
        for url, title in events:
            print('  * %s' % title)
            print('    %s' % url)

    def printComunitateaSaptamanaii(self):
        print('!!! Share comunitatea saptamanii on FB !!!')


for formatter_cls in [WordpressFormatter, RedditFormatter, FacebookFormatter]:
    formatter_cls().printAll(events)

