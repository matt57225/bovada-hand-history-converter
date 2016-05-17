#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright 2008-2011 Carl Gherardi
#Copyright 2016 matt57225
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, version 3 of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU Affero General Public License
#along with this program. If not, see <http://www.gnu.org/licenses/>.
#In the "official" distribution you can find the license in agpl-3.0.txt.

import re
import sys
from decimal_wrapper import Decimal
import operator

import time
import datetime

from pytz import timezone
import pytz

import logging

log = logging.getLogger("parser")

import Hand
#from Exceptions import *

class HandHistoryConverter():
    re_tzOffset = re.compile('^\w+[+-]\d{4}$')
    copyGameHeader = False

    def __init__(self):
        self.sitename = None
        self.maxseats  = 0
        self.in_path = ''
        self.compiledPlayers = set()
        self.tourney = None

    def processHand(self, handText, showKnown, fastFold, separateTablesByMaxSeats):
        if not self.isPartial(handText):
            gametype = self.determineGameType(handText)
            hand = None
            l = None
            if gametype is None:
                gametype = "unmatched"
            else:
                if 'mix' not in gametype: gametype['mix'] = 'none'
                if 'ante' not in gametype: gametype['ante'] = 0
                if 'buyinType' not in gametype: gametype['buyinType'] = 'regular'
                if 'fast' not in gametype: gametype['fast'] = False
                if 'newToGame' not in gametype: gametype['newToGame'] = False
                if 'homeGame' not in gametype: gametype['homeGame'] = False
                type = gametype['type']
                base = gametype['base']
                limit = gametype['limitType']
                l = [type] + [base] + [limit]

            if l in self.readSupportedGames():
                if gametype['base'] == 'hold':
                    if gametype['fast'] == True:
                        hand = Hand.HoldemOmahaHand(None,
                                                    self,
                                                    self.sitename,
                                                    gametype,
                                                    handText,
                                                    showKnown,
                                                    fastFold,
                                                    separateTablesByMaxSeats)
                    else:
                        hand = Hand.HoldemOmahaHand(None,
                                                    self,
                                                    self.sitename,
                                                    gametype,
                                                    handText,
                                                    showKnown,
                                                    False,
                                                    separateTablesByMaxSeats)

                elif gametype['base'] == 'stud':
                    hand = Hand.StudHand(None, self, self.sitename, gametype, handText)
                elif gametype['base'] == 'draw':
                    hand = Hand.DrawHand(None, self, self.sitename, gametype, handText)
            else:
                print(("%s Unsupported game type: %s") % (self.sitename, gametype))
                #raise FpdbParseError
                return

            if hand:
                return hand
            else:
                print(("%s Unsupported game type: %s") % (self.sitename, gametype))

    def isPartial(self, handText):
        count = 0
        for m in self.re_Identify.finditer(handText):
            count += 1
        if count != 1:
            return True
        return False

    def readSupportedGames(self): abstract
    def determineGameType(self, handText): abstract
    def readHandInfo(self, hand): abstract
    def readPlayerStacks(self, hand): abstract
    def compilePlayerRegexs(self): abstract
    def markStreets(self, hand): abstract
    def readBlinds(self, hand): abstract
    def readAntes(self, hand): abstract
    def readBringIn(self, hand): abstract
    def readButton(self, hand): abstract
    def readHeroCards(self, hand): abstract
    def readPlayerCards(self, hand, street): abstract
    def readAction(self, hand, street): abstract
    def readCollectPot(self, hand): abstract
    def readShownCards(self, hand): abstract
    def readTourneyResults(self, hand): abstract

    def readOther(self, hand): pass

    def getRake(self, hand):
        hand.rake = hand.totalpot - hand.totalcollected
        round = -1 if hand.gametype['type'] == "tour" else -0.01
        if hand.rake < 0 and (not hand.roundPenny or hand.rake < round):
            print(("hhc.getRake(): '%s': Converter may not have processed hand correctly: Amount collected (%s) is greater than the pot (%s)")
                      % (hand.handid,str(hand.totalcollected), str(hand.totalpot)))
            #raise FpdbParseError
            return
        elif hand.totalpot > 0 and Decimal(hand.totalpot/4) < hand.rake and not hand._fastFold:
            print(("hhc.getRake(): '%s': Converter may not have calculated rake correctly: (%s) > 25 pct of pot (%s)")
                      % (hand.handid,str(hand.rake), str(hand.totalpot)))
            #raise FpdbParseError
            return

    def guessMaxSeats(self, hand):
        if not self.copyGameHeader and hand.gametype['type']=='tour':
            return 10

        if self.maxseats > 1 and self.maxseats < 11:
            return self.maxseats

        mo = self.maxOccSeat(hand)

        if mo > 2 and mo <= 6: mo = 6

        if mo > 6 and mo <= 9: mo = 9

        if mo == 10: return 10

        if hand.gametype['base'] == 'stud':
            if mo <= 8: return 8

        if hand.gametype['base'] == 'draw':
            if mo <= 6: return 6

        if mo:
            return mo
        else:
            return 10

    def maxOccSeat(self, hand):
        max = len(hand.players)
        #max = 0
        #for player in hand.players:
            #if player[0] > max:
                #max = player[0]
        return max

    def readSummaryInfo(self, summaryInfoList): abstract

    def getTourney(self):
        return self.tourney

    @staticmethod
    def changeTimezone(time, givenTimezone, wantedTimezone):
        if wantedTimezone=="UTC":
            wantedTimezone = pytz.utc
        else:
            print(("Unsupported target timezone: ") + givenTimezone)
            #raise FpdbParseError(("Unsupported target timezone: ") + givenTimezone)
            return
        givenTZ = None
        if HandHistoryConverter.re_tzOffset.match(givenTimezone):
            offset = int(givenTimezone[-5:])
            givenTimezone = givenTimezone[0:-5]
        else: offset=0

        if givenTimezone in ("ET", "EST", "EDT"):
            givenTZ = timezone('US/Eastern')
        elif givenTimezone in ("CET", "CEST", "MEZ", "MESZ", "HAEC"):
            givenTZ = timezone('Europe/Berlin')
        elif givenTimezone == 'GMT': # GMT is always the same as UTC
            givenTZ = timezone('GMT')
        elif givenTimezone == 'BST':
             givenTZ = timezone('Europe/London')
        elif givenTimezone == 'WET': # WET is GMT with daylight saving delta
            givenTZ = timezone('WET')
        elif givenTimezone in ('HT', 'HST', 'HDT'): # Hawaiian Standard Time
            givenTZ = timezone('US/Hawaii')
        elif givenTimezone == 'AKT': # Alaska Time
            givenTZ = timezone('US/Alaska')
        elif givenTimezone in ('PT', 'PST', 'PDT'): # Pacific Time
            givenTZ = timezone('US/Pacific')
        elif givenTimezone in ('MT', 'MST', 'MDT'): # Mountain Time
            givenTZ = timezone('US/Mountain')
        elif givenTimezone in ('CT', 'CST', 'CDT'): # Central Time
            givenTZ = timezone('US/Central')
        elif givenTimezone == 'AT': # Atlantic Time
            givenTZ = timezone('Canada/Atlantic')
        elif givenTimezone == 'NT': # Newfoundland Time
            givenTZ = timezone('Canada/Newfoundland')
        elif givenTimezone == 'ART': # Argentinian Time
            givenTZ = timezone('America/Argentina/Buenos_Aires')
        elif givenTimezone == 'BRT': # Brasilia Time
            givenTZ = timezone('America/Sao_Paulo')
        elif givenTimezone == 'VET':
            givenTZ = timezone('America/Caracas')
        elif givenTimezone == 'COT':
            givenTZ = timezone('America/Bogota')
        elif givenTimezone in ('EET', 'EEST'): # Eastern European Time
            givenTZ = timezone('Europe/Bucharest')
        elif givenTimezone in ('MSK', 'MESZ', 'MSKS', 'MSD'): # Moscow Standard Time
            givenTZ = timezone('Europe/Moscow')
        elif givenTimezone == 'GST':
            givenTZ = timezone('Asia/Dubai')
        elif givenTimezone in ('YEKT','YEKST'):
            givenTZ = timezone('Asia/Yekaterinburg')
        elif givenTimezone in ('KRAT','KRAST'):
            givenTZ = timezone('Asia/Krasnoyarsk')
        elif givenTimezone == 'IST': # India Standard Time
            givenTZ = timezone('Asia/Kolkata')
        elif givenTimezone == 'ICT':
            givenTZ = timezone('Asia/Bangkok')
        elif givenTimezone == 'CCT': # China Coast Time
            givenTZ = timezone('Australia/West')
        elif givenTimezone == 'JST': # Japan Standard Time
            givenTZ = timezone('Asia/Tokyo')
        elif givenTimezone in ('AWST', 'AWT'):  # Australian Western Standard Time
            givenTZ = timezone('Australia/West')
        elif givenTimezone in ('ACST', 'ACT'): # Australian Central Standard Time
            givenTZ = timezone('Australia/Darwin')
        elif givenTimezone in ('AEST', 'AET'): # Australian Eastern Standard Time
            givenTZ = timezone('Australia/Sydney')
        elif givenTimezone == 'NZT': # New Zealand Time
            givenTZ = timezone('Pacific/Auckland')
        elif givenTimezone == 'UTC': # Universal time co-ordinated
            givenTZ = pytz.UTC

        if givenTZ is None:
            # do not crash if timezone not in list, just return UTC localized time
            print("Timezone conversion not supported") + ": " + givenTimezone + " " + str(time)
            givenTZ = pytz.UTC
            return givenTZ.localize(time)

        localisedTime = givenTZ.localize(time)
        utcTime = localisedTime.astimezone(wantedTimezone) + datetime.timedelta(seconds=-3600*(offset/100)-60*(offset%100))
        return utcTime

    @staticmethod
    def getTableTitleRe(type, table_name=None, tournament = None, table_number=None):
        if type=="tour":
            return ( re.escape(str(tournament)) + ".+\\Table " + re.escape(str(table_number)) )
        else:
            return re.escape(table_name)

    @staticmethod
    def getTableNoRe(tournament):
        return "%s.+(?:Table|Torneo) (\d+)" % (tournament, )

    @staticmethod
    def clearMoneyString(money):
        if not money:
            return money
        money = money.replace(' ', '')
        money = money.replace(u'\xa0', u'')
        if 'K' in money:
            money = money.replace('K', '000')
        if 'M' in money:
            money = money.replace('M', '000000')
        if 'B' in money:
            money = money.replace('B', '000000000')
        if money[-1] in ('.', ','):
            money = money[:-1]
        if len(money) < 3:
            return money # No commas until 0,01 or 1,00
        if money[-3] == ',':
            money = money[:-3] + '.' + money[-2:]
        if len(money) > 7:
            if money[-7] == '.':
                money = money[:-7] + ',' + money[-6:]
        if len(money) > 4:
            if money[-4] == '.':
                money = money[:-4] + ',' + money[-3:]

        return money.replace(',', '').replace("'", '')
