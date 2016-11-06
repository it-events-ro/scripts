#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils


print('Fetching all likes for ItEventsRo as a starting point')
likes = utils.facebookApi('ItEventsRo/likes?fields=name,link', paginate=True)
for l in likes:
  print('\t'.join([l['name'], l['name'], l['link']]))
