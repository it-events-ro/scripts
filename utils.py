# -*- coding: utf-8 -*-
import os
import traceback

import requests


def _append(url, name, value):
  if '?' in url:
    url += '&%s=%s' % (name, value)
  else:
    url += '?%s=%s' % (name, value)
  return url


def repeat(elements, message, callback):
  for i, e in enumerate(elements):
    print(message % e + ' (%d/%d)' % (i+1, len(elements)))
    try:
      callback(e)
    except (KeyboardInterrupt, SystemExit):
      raise
    except Exception as ex:
      print('There was an error processing %s' % e)
      traceback.print_exc()


def meetupApi(url):
  url = 'https://api.meetup.com/%s' % url
  meetup_key = os.environ['MEETUP_API_KEY']
  url = _append(url, 'key', meetup_key)
  return requests.get(url).json()


def eventbriteApi(url):
  eventbrite_key = os.environ['EVENTBRITE_API_KEY']
  return requests.get(
    'https://www.eventbriteapi.com/v3/%s' % url, headers={'Authorization': 'Bearer %s' % eventbrite_key}).json()


def facebookApi(url, paginate):
  url = 'https://graph.facebook.com/v2.7/%s' % url
  facebook_key = os.environ['FACEBOOK_API_KEY']
  url = _append(url, 'access_token', facebook_key)
  result = []
  while True:
    data = requests.get(url).json()
    if not paginate:
      return data
    result += data['data']
    print('.', end='', flush=True)
    if 'paging' not in data or 'next' not in data['paging']:
      break
    url = data['paging']['next']
  print()
  return result

