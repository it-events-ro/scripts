#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys

import utils

included_organizers = {
  2491303902, # http://www.eventbrite.com/o/itcamp-2491303902
  6873285549, # http://www.eventbrite.com/o/sponge-media-lab-6873285549
  3001324227, # http://www.eventbrite.com/o/labview-student-ambassador-upb-3001324227
  2300226659, # http://www.eventbrite.com/o/techstars-startup-programs-2300226659
  5899601137, # http://www.eventbrite.com/o/oana-calugar-amp-fabio-carati-amp-cristian-dascalu-5899601137
  4662547959, # http://www.eventbrite.com/o/clujhub-4662547959
  4138472935, # http://www.eventbrite.com/o/yonder-4138472935
  6397991619, # http://www.eventbrite.com/o/facultatea-de-inginerie-electrica-in-colaborare-cu-best-cluj-napoca-6397991619
  3367422098, # http://www.eventbrite.com/o/andreea-popescu-3367422098
  4206997271, # http://www.eventbrite.com/o/babele-create-together-4206997271
  3168795376, # http://www.eventbrite.com/o/girls-in-tech-romania-3168795376
  6671021543, # http://www.eventbrite.com/o/asociatia-ip-workshop-6671021543
  2761218168, # http://www.eventbrite.com/o/ccsir-2761218168
  9377817403, # http://www.eventbrite.com/o/hellojs-9377817403
  7802438407, #  http://www.eventbrite.com/o/innodrive-7802438407
  10949312400, # http://www.eventbrite.com/o/school-of-content-10949312400
  6795968089, # http://www.eventbrite.com/o/iiba-romania-chapter-6795968089
  10963965257, # http://www.eventbrite.com/o/sinaptiq-edu-10963965257
  4246372985, # http://www.eventbrite.com/o/hackathon-in-a-box-4246372985
  8767089022, # http://www.eventbrite.com.au/o/bm-college-8767089022
  6886785391, # http://www.eventbrite.com/o/sprint-consulting-6886785391
  8270334915, # http://www.eventbrite.co.uk/o/msg-systems-romania-8270334915
  2670928534, # http://www.eventbrite.com/o/itcamp-community-2670928534
  5340605367, # http://www.eventbrite.com/o/techhub-bucharest-5340605367
}

excluded_organizers = {
  8035595159, # http://www.eventbrite.com/o/magicianul-augustin-8035595159
  8193977126, # http://www.eventbrite.com/o/growth-marketing-conference-8193977126
  2725971154, # http://www.eventbrite.com/o/lost-worlds-racing-2725971154
  7795480037, # http://www.eventbrite.de/o/dexcar-autovermietung-ug-7795480037
  10911641537, # http://www.eventbrite.com/o/johanna-house-10911641537
  10950100881, # http://www.eventbrite.com/o/peace-action-training-and-research-institute-of-romania-patrir-10950100881
  8349138707, # http://www.eventbrite.com/o/trix-bike-primaria-tg-jiu-consilul-local-gorj-salvamont-gorj-8349138707
  5715420837, # http://www.eventbrite.com/o/mattei-events-5715420837
  2087207893, # http://www.eventbrite.com/o/john-stevens-zero-in-2087207893
  11050568264, # http://www.eventbrite.com/o/cristian-vasilescu-11050568264
  10924487836, # http://www.eventbrite.com/o/kmdefensecom-krav-maga-scoala-bukan-10924487836
  10797347037, # http://www.eventbrite.co.uk/o/story-travels-ltd-10797347037
  10933030217, # http://www.eventbrite.com/o/10933030217
  5570020107, # http://www.eventbrite.com/o/marius-5570020107
  10948788760, # http://www.eventbrite.com/o/centrul-de-dezvoltare-personala-constanta-10948788760
  10796273575, # http://www.eventbrite.com/o/summer-foundation-10796273575
  10931790600, # http://www.eventbrite.com/o/ioana-amp-vali-10931790600
  10024410089, # http://www.eventbrite.com/o/leagea-atractiei-in-actiune-10024410089
  6837788799, # http://www.eventbrite.com/o/lost-worlds-travel-6837788799
  10868911506, # http://www.eventbrite.com/o/the-city-of-green-buildings-association-10868911506
  10973196426, # http://www.eventbrite.com/o/10973196426
  8428263732, # http://www.eventbrite.com/o/upwork-8428263732
  10967928809, # http://www.eventbrite.com/o/eastern-artisans-atelier-10967928809
  1863005385, # http://www.eventbrite.com/o/sigma-3-survival-school-1863005385
  8541146418, # http://www.eventbrite.com/o/modularity-8541146418
  10909622502, # http://www.eventbrite.com/o/different-angle-cluster-10909622502
  8384351483, # http://www.eventbrite.com/o/sciencehub-8384351483
  10894747098, # http://www.eventbrite.com/o/consact-consulting-10894747098
  10952849991, # http://www.eventbrite.co.uk/o/art-live-10952849991
  10902884665, # http://www.eventbrite.com/o/10902884665
  10942128462, # http://www.eventbrite.com/o/eurotech-assessment-and-certification-services-pvt-ltd-10942128462
  9631107106, # http://www.eventbrite.com/o/de-ce-nu-eu-9631107106
  11054013211, # http://www.eventbrite.co.uk/o/first-people-solutions-aviation-11054013211
  10867523860, # http://www.eventbrite.com/o/igloo-media-10867523860
  11063098365, # http://www.eventbrite.co.uk/o/glas-expert-11063098365
  8348933279, # http://www.eventbrite.com/o/parentis-8348933279
  11087510059, # http://www.eventbrite.co.uk/o/untold-ong-11087510059
  11085577626, # http://www.eventbrite.com/o/11085577626
}

# TODO: make somehow API calls return historical events also
# TODO: make API calls handle paging

print ('Looking for new organizations')
has_unknown_orgs = False
events = utils.eventbriteApi('events/search/?venue.country=RO&include_unavailable_events=true')
for e in events['events']:
  organizer_id = int(e['organizer_id'])
  if (organizer_id in included_organizers) or (organizer_id in excluded_organizers):
    continue

  has_unknown_orgs = True
  org = utils.eventbriteApi('organizers/%d/' % organizer_id)
  print('Unknown organization %d:\n- %s\n- %s' % (organizer_id, e['url'], org['url']))

if has_unknown_orgs:
  print('Had unknown orgs, stopping')
  sys.exit(1)


orgs, venues, events = {}, {}, []

def _getOrganizersAndEvents(org_id):
  global events, orgs
  org = utils.eventbriteApi('organizers/%d/' % org_id)
  orgs[org_id] = org

  org_events = utils.eventbriteApi(
    'organizers/%d/events/?start_date.range_start=2010-01-01T00:00:00&status=all' % org_id)
  events += [e for e in org_events['events'] if 'venue_id' in e and e['venue_id'] is not None]
utils.repeat(included_organizers, 'Fetching organization data for %d', _getOrganizersAndEvents)


def _getVenueInfo(venue_id):
  global venues
  venue = utils.eventbriteApi('venues/%d/' % venue_id)
  # some organizations do events world-wide, not in RO only
  if venue['address']['country'] != 'RO': return
  venues[venue_id] = venue
unique_venues = frozenset(int(e['venue_id']) for e in events)
utils.repeat(unique_venues, 'Fetching venue information for %d', _getVenueInfo)


# filter out events not from RO
events = [e for e in events if int(e['venue_id']) in venues]


result = dict(orgs=orgs, venues=venues, events=events)
with open('eventbrites.json', 'w') as f:
  f.write(json.dumps(result, sort_keys=True, indent=4))

