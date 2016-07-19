# -*- coding: utf-8 -*-
import requests
import os


def meetupApi(url):
  url = 'https://api.meetup.com/%s'
  meetup_key = os.environ['MEETUP_API_KEY']
  if '?' in url:
    url += '&key=%s' % key
  else:
    url += '?key=%s' % key
  return requests.get(url).json()


def eventbriteApi(url):
  eventbrite_key = os.environ['EVENTBRITE_API_KEY']
  return requests.get(
    'https://www.eventbriteapi.com/v3/%s' % url, headers={'Authorization': 'Bearer %s' % eventbrite_key}).json()

