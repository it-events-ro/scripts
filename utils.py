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
