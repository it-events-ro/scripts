#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import utils

organizers = {
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
  8042013777, # http://www.eventbrite.com/o/owasp-foundation-8042013777
  11097508562, # http://www.eventbrite.com/o/robertino-vasilescu-si-bogdan-socol-ambasadori-prestashop-11097508562
}


for o in organizers:
  o = utils.eventbriteApi('/organizers/%d/' % o)
  print('\t'.join([o['name'], o['name'], o['url']]))

