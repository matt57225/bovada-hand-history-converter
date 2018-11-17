#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2008-2011 Carl Gherardi
# Copyright 2016 matt57225
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# In the "official" distribution you can find the license in agpl-3.0.txt.

import sys
from decimal_wrapper import Decimal
import datetime
import pprint
import Card

class Hand(object):
    UPS = {'a':'A', 't':'T', 'j':'J', 'q':'Q', 'k':'K', 'S':'s', 'C':'c', 'H':'h', 'D':'d'}
    LCS = {'H':'h', 'D':'d', 'C':'c', 'S':'s'}
    SYMBOL = {'USD': '$', 'CAD': 'C$', 'EUR': '€', 'GBP': '£', 'SEK': 'kr.', 'RSD': 'РСД', 'mBTC': 'ⓑ', 'T$': '', 'play': ''}
    MS = {'horse' : 'HORSE', '8game' : '8-Game', 'hose'  : 'HOSE', 'ha': 'HA'}
    ACTION = {'ante': 1, 'small blind': 2, 'secondsb': 3, 'big blind': 4, 'both': 5, 'calls': 6, 'raises': 7,
              'bets': 8, 'stands pat': 9, 'folds': 10, 'checks': 11, 'discards': 12, 'bringin': 13, 'completes': 14}


    def __init__(self, config, sitename, gametype, handText, builtFrom = "HHC"):
        self.config = config
        self.sitename = sitename
        self.gametype = gametype
        self.startTime = 0
        self.handText = handText
        self.handid = 0
        self.in_path = None
        self.cancelled = False
        self.tablename = ""
        self.hero = ""
        self.maxseats = None
        self.counted_seats = 0
        self.buttonpos = 0
        self.runItTimes = 0
        self.uncalledbets = False
        self.checkForUncalled = False
        self.adjustCollected = False

        # tourney stuff
        self.tourNo = None
        self.tourneyId = None
        self.tourneyName = None
        self.tourneyTypeId = None
        self.buyin = None
        self.buyinCurrency = None
        self.buyInChips = None
        self.fee = None
        self.level = None
        self.mixed = None
        self.speed = "Normal"
        self.isSng = False
        self.isRebuy = False
        self.rebuyCost = 0
        self.isAddOn = False
        self.addOnCost = 0
        self.isKO = False
        self.koBounty = 0
        self.isProgressive = False
        self.isMatrix = False
        self.isShootout = False
        self.isFast = False
        self.stack = "Regular"
        self.isStep = False
        self.stepNo = 0
        self.isChance = False
        self.chanceCount = 0
        self.isMultiEntry = False
        self.isReEntry = False
        self.isHomeGame = False
        self.isNewToGame = False
        self.isFifty50 = False
        self.isTime = False
        self.timeAmt = 0
        self.isSatellite = False
        self.isDoubleOrNothing = False
        self.isCashOut = False
        self.isOnDemand = False
        self.isFlighted = False
        self.isGuarantee = False
        self.guaranteeAmt = 0
        self.added = None
        self.addedCurrency = None
        self.entryId = 1

        self.seating = []
        self.players = []
        # Cache used for checkPlayerExists.
        self.player_exists_cache = set()
        self.posted = []
        self.tourneysPlayersIds = {}

        # Collections indexed by street names
        self.bets = {}
        self.lastBet = {}
        self.streets = {}
        self.actions = {} # [['mct','bets','$10'],['mika','folds'],['carlg','raises','$20']]
        self.board = {} # dict from street names to community cards
        self.holecards = {}
        self.discards = {}
        self.showdownStrings = {}
        for street in self.allStreets:
            self.streets[street] = "" # portions of the handText, filled by markStreets()
            self.actions[street] = []
        for street in self.actionStreets:
            self.bets[street] = {}
            self.lastBet[street] = 0
            self.board[street] = []
        for street in self.holeStreets:
            self.holecards[street] = {} # dict from player names to holecards
        for street in self.discardStreets:
            self.discards[street] = {} # dict from player names to dicts by street ... of tuples ... of discarded holecards
        # Collections indexed by player names
        self.rakes = {}
        self.stacks = {}
        self.collected = [] #list of ?
        self.collectees = {} # dict from player names to amounts collected (?)
        self.koCounts = {}
        self.endBounty = {}

        # Sets of players
        self.folded = set()
        self.dealt = set()  # 'dealt to' line to be printed
        self.shown = set()  # cards were shown
        self.mucked = set() # cards were mucked at showdown
        self.sitout = set() # players sitting out or not dealt in (usually tournament)

        # Things to do with money
        self.pot = Pot()
        self.totalpot = None
        self.totalcollected = None
        self.rake = None
        self.roundPenny = False
        self._fastFold = False
        self._separateTablesByMaxSeats = False
        # currency symbol for this hand
        self.sym = self.SYMBOL[self.gametype['currency']]
        self.pot.setSym(self.sym)
        self.is_duplicate = False

    def __str__(self):
        vars = ( (("BB"), self.bb),
                 (("SB"), self.sb),
                 (("BUTTON POS"), self.buttonpos),
                 (("HAND NO."), self.handid),
                 (("SITE"), self.sitename),
                 (("TABLE NAME"), self.tablename),
                 (("HERO"), self.hero),
                 (("MAX SEATS"), self.maxseats),
                 (("LEVEL"), self.level),
                 (("MIXED"), self.mixed),
                 (("LAST BET"), self.lastBet),
                 (("ACTION STREETS"), self.actionStreets),
                 (("STREETS"), self.streets),
                 (("ALL STREETS"), self.allStreets),
                 (("COMMUNITY STREETS"), self.communityStreets),
                 (("HOLE STREETS"), self.holeStreets),
                 (("COUNTED SEATS"), self.counted_seats),
                 (("DEALT"), self.dealt),
                 (("SHOWN"), self.shown),
                 (("MUCKED"), self.mucked),
                 (("TOTAL POT"), self.totalpot),
                 (("TOTAL COLLECTED"), self.totalcollected),
                 (("RAKE"), self.rake),
                 (("START TIME"), self.startTime),
                 (("TOURNAMENT NO"), self.tourNo),
                 (("TOURNEY ID"), self.tourneyId),
                 (("TOURNEY TYPE ID"), self.tourneyTypeId),
                 (("BUYIN"), self.buyin),
                 (("BUYIN CURRENCY"), self.buyinCurrency),
                 (("BUYIN CHIPS"), self.buyInChips),
                 (("FEE"), self.fee),
                 (("IS REBUY"), self.isRebuy),
                 (("IS ADDON"), self.isAddOn),
                 (("IS KO"), self.isKO),
                 (("KO BOUNTY"), self.koBounty),
                 (("IS MATRIX"), self.isMatrix),
                 (("IS SHOOTOUT"), self.isShootout),
        )

        structs = ( (("PLAYERS"), self.players),
                    (("STACKS"), self.stacks),
                    (("POSTED"), self.posted),
                    (("POT"), self.pot),
                    (("SEATING"), self.seating),
                    (("GAMETYPE"), self.gametype),
                    (("ACTION"), self.actions),
                    (("COLLECTEES"), self.collectees),
                    (("BETS"), self.bets),
                    (("BOARD"), self.board),
                    (("DISCARDS"), self.discards),
                    (("HOLECARDS"), self.holecards),
                    (("TOURNEYS PLAYER IDS"), self.tourneysPlayersIds),
        )
        result = ''
        for (name, var) in vars:
            result = result + "\n%s = " % name + pprint.pformat(var)

        for (name, struct) in structs:
            result = result + "\n%s =\n" % name + pprint.pformat(struct, 4)
        return result

    def addHoleCards(self, street, player, open=[], closed=[], shown=False, mucked=False, dealt=False):
        self.checkPlayerExists(player, 'addHoleCards')

        if dealt:  self.dealt.add(player)
        if shown:  self.shown.add(player)
        if mucked: self.mucked.add(player)

        for i in range(len(closed)):
            if closed[i] in ('', 'Xx', 'Null', 'null'):
                closed[i] = '0x'

        try:
            self.holecards[street][player] = [open, closed]
        except KeyError as e:
            print((("Hand.addHoleCards: '%s': Major failure while adding holecards: '%s'"), self.handid, e))
            return

    def addPlayer(self, seat, name, chips, position=None, sitout=False, bounty=None):
        if len(self.players) > 0 and seat in [p[0] for p in self.players]:
            print(("addPlayer: " + ("Can't have 2 players in the same seat!") + ": '%s'" % self.handid))
            return
        if chips is not None:
            chips = chips.replace(',', '') #some sites have commas
            self.players.append([seat, name, chips, position, bounty])
            self.stacks[name] = Decimal(chips)
            self.pot.addPlayer(name)
            for street in self.actionStreets:
                self.bets[street][name] = []
            if sitout:
                self.sitout.add(name)

    def removePlayer(self, name):
        if self.stacks.get(name):
            self.players = [p for p in self.players if p[1]!=name]
            del self.stacks[name]
            self.pot.removePlayer(name)
            for street in self.actionStreets:
                del self.bets[street][name]
            self.sitout.discard(name)

    def addStreets(self, match):
        if match:
            self.streets.update(match.groupdict())
        else:
            tmp = self.handText[0:100]
            self.cancelled = True
            print((("Streets didn't match - Assuming hand '%s' was cancelled.") % (self.handid) + " " + ("First 100 characters: %s") % tmp))
            return

    def checkPlayerExists(self,player,source = None):
        if player in self.player_exists_cache:
            return

        if player not in (p[1] for p in self.players):
            if source is not None:
                print((("Hand.%s: '%s' unknown player: '%s'"), source, self.handid, player))
            return
        else:
            self.player_exists_cache.add(player)

    def setCommunityCards(self, street, cards):
        self.board[street] = [self.card(c) for c in cards]

    def card(self,c):
        """upper case the ranks but not suits, 'atjqk' => 'ATJQK'"""
        for k,v in list(self.UPS.items()):
            c = c.replace(k,v)
        return c

    def addAllIn(self, street, player, amount):
        self.checkPlayerExists(player, 'addAllIn')
        amount = amount.replace(',', '') #some sites have commas
        Ai = Decimal(amount)
        Bp = self.lastBet[street]
        Bc = sum(self.bets[street][player])
        C = Bp - Bc
        if Ai <= C:
            self.addCall(street, player, amount)
        elif Bp == 0:
            self.addBet(street, player, amount)
        else:
            Rb = Ai - C
            Rt = Bp + Rb
            self._addRaise(street, player, C, Rb, Rt)

    def addAnte(self, player, ante):
        if player is not None:
            ante = ante.replace(',', '') #some sites have commas
            self.checkPlayerExists(player, 'addAnte')
            ante = Decimal(ante)
            self.bets['BLINDSANTES'][player].append(ante)
            self.stacks[player] -= ante
            act = (player, 'ante', ante, self.stacks[player]==0)
            self.actions['BLINDSANTES'].append(act)
            self.pot.addCommonMoney(player, ante)
            self.pot.addAntes(player, ante)
            if 'ante' not in list(self.gametype.keys()) or self.gametype['ante'] < ante or self.gametype['ante'] == 0:
                self.gametype['ante'] = ante

    def addBlind(self, player, blindtype, amount):
        if player is not None:
            self.checkPlayerExists(player, 'addBlind')
            amount = amount.replace(',', '') #some sites have commas
            amount = Decimal(amount)
            self.stacks[player] -= amount
            act = (player, blindtype, amount, self.stacks[player]==0)
            self.actions['BLINDSANTES'].append(act)

            if blindtype == 'both':
                amount = Decimal(str(self.bb))
                sb = Decimal(str(self.sb))
                self.bets['BLINDSANTES'][player].append(sb)
                self.pot.addCommonMoney(player, sb)

            if blindtype == 'secondsb':
                amount = Decimal(0)
                sb = Decimal(str(self.sb))
                self.bets['BLINDSANTES'][player].append(sb)
                self.pot.addCommonMoney(player, sb)

            street = 'BLAH'

            if self.gametype['base'] == 'hold':
                street = 'PREFLOP'
            elif self.gametype['base'] == 'draw':
                street = 'DEAL'

            self.bets[street][player].append(amount)
            self.pot.addMoney(player, amount)
            if amount>self.lastBet.get(street):
                self.lastBet[street] = amount
            self.posted = self.posted + [[player,blindtype]]

    def addCall(self, street, player=None, amount=None):
        if amount is not None:
            amount = amount.replace(',', '') #some sites have commas
        if amount is not None:
            self.checkPlayerExists(player, 'addCall')
            amount = Decimal(amount)
            self.bets[street][player].append(amount)
            if street in ('PREFLOP', 'DEAL', 'THIRD') and self.lastBet.get(street)<amount:
                self.lastBet[street] = amount
            self.stacks[player] -= amount
            act = (player, 'calls', amount, self.stacks[player] == 0)
            self.actions[street].append(act)
            self.pot.addMoney(player, amount)

    def addCallTo(self, street, player=None, amountTo=None):
        if amountTo:
            amountTo = amountTo.replace(',', '') #some sites have commas
        if amountTo is not None:
            self.checkPlayerExists(player, 'addCallTo')
            Bc = sum(self.bets[street][player])
            Ct = Decimal(amountTo)
            C = Ct - Bc
            amount = C
            self.bets[street][player].append(amount)
            self.stacks[player] -= amount
            act = (player, 'calls', amount, self.stacks[player] == 0)
            self.actions[street].append(act)
            self.pot.addMoney(player, amount)

    def addRaiseBy(self, street, player, amountBy):
        amountBy = amountBy.replace(',', '') #some sites have commas
        self.checkPlayerExists(player, 'addRaiseBy')
        Rb = Decimal(amountBy)
        Bp = self.lastBet[street]
        Bc = sum(self.bets[street][player])
        C = Bp - Bc
        Rt = Bp + Rb

        self._addRaise(street, player, C, Rb, Rt)

    def addCallandRaise(self, street, player, amount):
        self.checkPlayerExists(player, 'addCallandRaise')
        amount = amount.replace(',', '') #some sites have commas
        CRb = Decimal(amount)
        Bp = self.lastBet[street]
        Bc = sum(self.bets[street][player])
        C = Bp - Bc
        Rb = CRb - C
        Rt = Bp + Rb

        self._addRaise(street, player, C, Rb, Rt)

    def addRaiseTo(self, street, player, amountTo):
        self.checkPlayerExists(player, 'addRaiseTo')
        amountTo = amountTo.replace(',', '') #some sites have commas
        Bp = self.lastBet[street]
        Bc = sum(self.bets[street][player])
        Rt = Decimal(amountTo)
        C = Bp - Bc
        Rb = Rt - C - Bc
        self._addRaise(street, player, C, Rb, Rt)

    def _addRaise(self, street, player, C, Rb, Rt, action = 'raises'):
        self.bets[street][player].append(C + Rb)
        self.stacks[player] -= (C + Rb)
        act = (player, action, Rb, Rt, C, self.stacks[player]==0)
        self.actions[street].append(act)
        self.lastBet[street] = Rt
        self.pot.addMoney(player, C+Rb)

    def addBet(self, street, player, amount):
        amount = amount.replace(',', '') #some sites have commas
        amount = Decimal(amount)
        self.checkPlayerExists(player, 'addBet')
        self.bets[street][player].append(amount)
        self.stacks[player] -= amount
        act = (player, 'bets', amount, self.stacks[player]==0)
        self.actions[street].append(act)
        self.lastBet[street] = amount
        self.pot.addMoney(player, amount)

    def addStandsPat(self, street, player, cards=None):
        self.checkPlayerExists(player, 'addStandsPat')
        act = (player, 'stands pat')
        self.actions[street].append(act)
        if cards:
            cards = cards.split(' ')
            self.addHoleCards(street, player, open=[], closed=cards)

    def addFold(self, street, player):
        self.checkPlayerExists(player, 'addFold')
        if player in self.folded:
            return
        self.folded.add(player)
        self.pot.addFold(player)
        self.actions[street].append((player, 'folds'))

    def addCheck(self, street, player):
        self.checkPlayerExists(player, 'addCheck')
        self.actions[street].append((player, 'checks'))

    def discardDrawHoleCards(self, cards, player, street):
        self.discards[street][player] = set([cards])

    def addDiscard(self, street, player, num, cards=None):
        self.checkPlayerExists(player, 'addDiscard')
        if cards:
            act = (player, 'discards', Decimal(num), cards)
            self.discardDrawHoleCards(cards, player, street)
        else:
            act = (player, 'discards', Decimal(num))
        self.actions[street].append(act)

    def addCollectPot(self, player, pot):
        self.checkPlayerExists(player, 'addCollectPot')
        self.collected = self.collected + [[player, pot]]
        if player not in self.collectees:
            self.collectees[player] = Decimal(pot)
        else:
            self.collectees[player] += Decimal(pot)

    def sittingOut(self):
        dealtIn = set()
        for street in self.actionStreets:
            for act in self.actions[street]:
                dealtIn.add(act[0])
        for player in list(self.collectees.keys()):
            dealtIn.add(player)
        for player in self.dealt:
            dealtIn.add(player)
        for p in list(self.players):
            if p[1] not in dealtIn:
                if self.gametype['type']=='tour':
                    self.sitout.add(p[1])
                else:
                    self.removePlayer(p[1])
        if len(self.players)<2:
            print((("Less than 2 players - Assuming hand '%s' was cancelled.") % (self.handid)))
            return

    def setUncalledBets(self, value):
        self.uncalledbets = value

    def totalPot(self):
        # This gives us the total amount put in the pot
        if self.totalpot is None:
            self.pot.end(self.sb, self.bb, self.collectees)
            self.totalpot = self.pot.total

        #if self.adjustCollected:
            #self.stats.awardPots(self)

        def gettempcontainers(collected, collectees):
            (collectedCopy, collecteesCopy, totalcollected) = ([], {}, 0)
            for v in sorted(collected, key=lambda collectee: collectee[1], reverse=True):
                if Decimal(v[1])!=0:
                    totalcollected += Decimal(v[1])
                    collectedCopy.append([v[0], Decimal(v[1])])
            for k, j in collectees.items():
                if j!=0: collecteesCopy[k] = j
            return collectedCopy, collecteesCopy, totalcollected

        collected, collectees, totalcollected = gettempcontainers(self.collected, self.collectees)
        if (self.uncalledbets or ((self.totalpot - totalcollected < 0) and self.checkForUncalled)):
            for i,v in enumerate(sorted(self.collected, key=lambda collectee: collectee[1], reverse=True)):
                if v[0] in self.pot.returned:
                    collected[i][1] = Decimal(v[1]) - self.pot.returned[v[0]]
                    collectees[v[0]] -= self.pot.returned[v[0]]
                    self.pot.returned[v[0]] = 0
            (self.collected, self.collectees, self.totalcollected) = gettempcontainers(collected, collectees)

        if self.totalcollected is None:
            self.totalcollected = 0
            for entry in self.collected:
                self.totalcollected += Decimal(entry[1])

    def getGameTypeAsString(self):
        """ Map the tuple self.gametype onto the PokerStars string describing it """
        # currently it appears to be something like ["ring", "hold", "nl", sb, bb]:
        gs = {"holdem"     : "Hold'em",
              "omahahi"    : "Omaha",
              "omahahilo"  : "Omaha Hi/Lo",
              "razz"       : "Razz",
              "studhi"     : "7 Card Stud",
              "studhilo"   : "7 Card Stud Hi/Lo",
              "fivedraw"   : "5 Card Draw",
              "27_1draw"   : "Single Draw 2-7 Lowball",
              "27_3draw"   : "Triple Draw 2-7 Lowball",
              "5_studhi"   : "5 Card Stud",
              "badugi"     : "Badugi"
             }
        ls = {"nl"  : "No Limit",
              "pl"  : "Pot Limit",
              "fl"  : "Limit",
              "cn"  : "Cap No Limit",
              "cp"  : "Cap Pot Limit"
             }

        retstring = "%s %s" %(gs[self.gametype['category']], ls[self.gametype['limitType']])
        return retstring

    def printHand(self):
        self.writeHand(sys.stdout)

    def actionString(self, act, street=None):
        if act[1] == 'folds':
            return ("%s: folds " %(act[0]))
        elif act[1] == 'checks':
            return ("%s: checks " %(act[0]))
        elif act[1] == 'calls':
            return ("%s: calls %s%s%s" %(act[0], self.sym, act[2], ' and is all-in' if act[3] else ''))
        elif act[1] == 'bets':
            return ("%s: bets %s%s%s" %(act[0], self.sym, act[2], ' and is all-in' if act[3] else ''))
        elif act[1] == 'raises':
            return ("%s: raises %s%s to %s%s%s" %(act[0], self.sym, act[2], self.sym, act[3], ' and is all-in' if act[5] else ''))
        elif act[1] == 'completes':
            return ("%s: completes to %s%s%s" %(act[0], self.sym, act[2], ' and is all-in' if act[3] else ''))
        elif(act[1] == "small blind"):
            if Decimal(act[2]) == Decimal(self.bb):
                return ("%s: posts big blind %s%s%s" %(act[0], self.sym, act[2], ' and is all-in' if act[3] else ''))
            return ("%s: posts small blind %s%s%s" %(act[0], self.sym, act[2], ' and is all-in' if act[3] else ''))
        elif(act[1] == "big blind"):
            return ("%s: posts big blind %s%s%s" %(act[0], self.sym, act[2], ' and is all-in' if act[3] else ''))
        elif(act[1] == "both"):
            return ("%s: posts small & big blinds %s%s%s" %(act[0], self.sym, act[2], ' and is all-in' if act[3] else ''))
        elif(act[1] == "ante"):
            return ("%s: posts the ante %s%s%s" %(act[0], self.sym, act[2], ' and is all-in' if act[3] else ''))
        elif act[1] == 'bringin':
            return ("%s: brings in for %s%s%s" %(act[0], self.sym, act[2], ' and is all-in' if act[3] else ''))
        elif act[1] == 'discards':
            return ("%s: discards %s %s%s" %(act[0], act[2],
                                             'card' if act[2] == 1 else 'cards',
                                             " [" + " ".join(self.discards[street][act[0]]) + "]" if self.hero == act[0] else ''))
        elif act[1] == 'stands pat':
            return ("%s: stands pat" %(act[0]))

    def get_actions_short(self, player, street):
        actions = self.actions[street]
        result = []
        for action in actions:
            if player in action:
                if action[1] == 'folds':
                    result.append('F')
                elif action[1] == 'checks':
                    result.append('X')
                elif action[1] == 'bets':
                    result.append('B')
                elif action[1] == 'calls':
                    result.append('C')
                elif action[1] == 'raises':
                    result.append('R')

        return ''.join(result)

    def get_actions_short_streets(self, player, *streets):
        result = []
        for street in streets:
            action = self.get_actions_short(player, street)
            if len(action) > 0: # if there is no action on later streets, nothing is added.
                result.append(action)
        return ','.join(result)

    def get_player_position(self, player):
        for p in self.players:
            if p[1] == player:
                return p[3]

    def getStakesAsString(self):
        return "%s%s/%s%s" % (self.sym, self.sb, self.sym, self.bb)

    def getStreetTotals(self):
        tmp, i = [0, 0, 0, 0, 0, 0], 0
        for street in self.allStreets:
            if street != 'BLINDSANTES':
                tmp[i] = self.pot.getTotalAtStreet(street)
                i+=1
        tmp[5] = sum(self.pot.committed.values()) + sum(self.pot.common.values())
        return tmp

    def writeGameLine(self):
        if self._fastFold:
            gs = "PokerStars Zoom Hand #%s: " % self.handid
        else:
            gs = "PokerStars Hand #%s: " % self.handid

        if self.tourNo is not None and self.mixed is not None: # mixed tournament
            if self.buyin is not None:
                gs = gs + "Tournament #%s, $%s+$%s %s (%s) - Level %s (%s) - " % (self.tourNo, self.buyin, self.fee, self.MS[self.mixed], self.getGameTypeAsString(), self.level, self.getStakesAsString())
            else:
                gs = gs + "Tournament #%s, %s (%s) - Level %s (%s) - " % (self.tourNo, self.MS[self.mixed], self.getGameTypeAsString(), self.level, self.getStakesAsString())
        elif self.tourNo is not None: # all other tournaments
            if self.buyin is not None:
                gs = gs + "Tournament #%s, $%s+$%s %s - Level %s (%s) - " % (self.tourNo, self.buyin, self.fee, self.getGameTypeAsString(), self.level, self.getStakesAsString())
            else:
                gs = gs + "Tournament #%s, %s - Level %s (%s) - " % (self.tourNo, self.getGameTypeAsString(), self.level, self.getStakesAsString())
        elif self.mixed is not None: # all other mixed games
            gs = gs + " %s (%s, %s) - " % (self.MS[self.mixed],
                            self.getGameTypeAsString(), self.getStakesAsString())
        else: # non-mixed cash games
            gs = gs + " %s (%s) - " % (self.getGameTypeAsString(), self.getStakesAsString())

        try:
            timestr = datetime.datetime.strftime(self.startTime, '%Y/%m/%d %H:%M:%S ET')
        except TypeError:
            print(("*** ERROR - HAND: calling writeGameLine with unexpected STARTTIME value, expecting datetime.date object, received:"), self.startTime)
            print("*** Make sure your HandHistoryConverter is setting hand.startTime properly!")
            print(("*** Game String:"), gs)
            return gs
        else:
            return gs + timestr

    def writeTableLine(self):
        table_string = "Table "
        if self.gametype['type'] == 'tour':
            table_string = table_string + "\'%s\' %s-max" % (self.tablename, self.maxseats)
        else:
            if self._separateTablesByMaxSeats:
                table_string = table_string + "\'%s %s-max\' %s-max" % (self.tablename, self.maxseats, self.maxseats)
            else:
                table_string = table_string + "\'%s\' %s-max" % (self.tablename, self.maxseats)
        if self.gametype['currency'] == 'play':
            table_string = table_string + " (Play Money)"
        if self.buttonpos is not None and self.buttonpos != 0:
            table_string = table_string + " Seat #%s is the button" % self.buttonpos
        return table_string


    def writeHand(self, fh=sys.__stdout__):
        # PokerStars format.
        print(self.writeGameLine(), file=fh)
        print(self.writeTableLine(), file=fh)


class HoldemOmahaHand(Hand):
    def __init__(self, config, hhc, sitename, gametype, handText, showKnown, fastFold, separateTablesByMaxSeats, builtFrom = "HHC", handid=None):
        self.config = config
        self.showKnown = showKnown
        self.fastFold = fastFold
        self.separateTablesByMaxSeats = separateTablesByMaxSeats
        if gametype['base'] != 'hold':
            pass
        self.allStreets = ['BLINDSANTES', 'PREFLOP','FLOP','TURN','RIVER']
        self.holeStreets = ['PREFLOP']
        if gametype['category']=='irish':
            self.discardStreets = ['TURN']
        else:
            self.discardStreets = ['PREFLOP']
        self.communityStreets = ['FLOP', 'TURN', 'RIVER']
        self.actionStreets = ['BLINDSANTES','PREFLOP','FLOP','TURN','RIVER']
        Hand.__init__(self, self.config, sitename, gametype, handText, builtFrom = "HHC")
        self.sb = gametype['sb']
        self.bb = gametype['bb']
        if hasattr(hhc, "in_path"):
            self.in_path = hhc.in_path
        else:
            self.in_path = "database"

        # Populate a HoldemOmahaHand
        if builtFrom == "HHC":
            hhc.readHandInfo(self)
            if self.gametype['type'] == 'tour':
                self.tablename = "%s %s" % (self.tourNo, self.tablename)
            hhc.readPlayerStacks(self)
            hhc.compilePlayerRegexs(self)
            hhc.markStreets(self)

            if self.cancelled:
                return

            hhc.readBlinds(self)

            hhc.readAntes(self)
            hhc.readButton(self)
            hhc.readHoleCards(self)
            hhc.readShowdownActions(self)
            # Read actions in street order
            for street, text in self.streets.items():
                if text and (street is not "PREFLOP"):
                    hhc.readCommunityCards(self, street)
            for street in self.actionStreets:
                if self.streets[street]:
                    hhc.readAction(self, street)
                    self.pot.markTotal(street)
            hhc.readCollectPot(self)
            hhc.readShownCards(self)
            self.pot.handid = self.handid # This is only required so Pot can throw it in totalPot
            self.totalPot() # finalize it (total the pot)
            hhc.getRake(self)
            if self.maxseats is None:
                self.maxseats = hhc.guessMaxSeats(self)
            self.sittingOut()
            hhc.readTourneyResults(self)
            hhc.readOther(self)
        elif builtFrom == "DB":
            self.maxseats = 10
        else:
            pass

    def addShownCards(self, cards, player, shown=True, mucked=False, dealt=False, string=None):
        if player == self.hero: # we have hero's cards just update shown/mucked
            if shown:  self.shown.add(player)
            if mucked: self.mucked.add(player)
        else:
            if len(cards) in (2, 3, 4, 6) or self.gametype['category'] in ('5_omahahi', '5_omaha8', 'cour_hi', 'cour_hilo'):  # avoid adding board by mistake
                self.addHoleCards('PREFLOP', player, open=[], closed=cards, shown=shown, mucked=mucked, dealt=dealt)
            elif len(cards) == 5:     # cards holds a winning hand, not hole cards
                diff = [x for x in cards if x not in self.board['FLOP']+self.board['TURN']+self.board['RIVER']]
                if len(diff) == 2 and self.gametype['category'] in ('holdem'):
                    self.addHoleCards('PREFLOP', player, open=[], closed=diff, shown=shown, mucked=mucked, dealt=dealt)
        if string is not None:
            self.showdownStrings[player] = string

    def join_holecards(self, player, asList=False):
        holeNo = Card.games[self.gametype['category']][5][0][1]
        hcs = ['0x'] * holeNo
        for street in self.holeStreets:
            if player in list(self.holecards[street].keys()):
                if len(self.holecards[street][player][1])==1: continue
                for i in 0,1:
                    hcs[i] = self.holecards[street][player][1][i]
                    hcs[i] = str.upper(hcs[i][0:1])+hcs[i][1:2]
                try:
                    for i in range(2, holeNo):
                        hcs[i] = self.holecards[street][player][1][i]
                        hcs[i] = str.upper(hcs[i][0:1])+hcs[i][1:2]
                except IndexError:
                    print("indexerror")

        if asList:
            return hcs
        else:
            return " ".join(hcs)

    def writeHand(self, fh=sys.__stdout__):
        if self.maxseats == None:
            return

        sdOccurred = True

        if len(self.folded) == len(self.players) - 1:
            sdOccurred = False

        #self.gametype['maxSeats'] = self.maxseats
        #if self.totalpot == None:
            #self.totalPot()
            #self.rake = self.totalpot - self.totalcollected
        self._fastFold = self.fastFold
        self._separateTablesByMaxSeats = self.separateTablesByMaxSeats
        super(HoldemOmahaHand, self).writeHand(fh)

        players_who_act_preflop = set(([x[0] for x in self.actions['PREFLOP']]+[x[0] for x in self.actions['BLINDSANTES']]))
        for player in [x for x in self.players if x[1] in players_who_act_preflop]:
            # Only print stacks of players who do something preflop
            print(("Seat %s: %s ($%.2f in chips) " %(player[0], player[1], float(player[2]))), file=fh)

        if self.actions['BLINDSANTES']:
            for act in self.actions['BLINDSANTES']:
                print(self.actionString(act), file=fh)

        print(("*** HOLE CARDS ***"), file=fh)
        for player in self.dealt:
            print(("Dealt to %s [%s]" %(player, " ".join(self.holecards['PREFLOP'][player][1]))), file=fh)
        if self.hero == "":
            for player in self.shown.difference(self.dealt):
                print(("Dealt to %s [%s]" %(player, " ".join(self.holecards['PREFLOP'][player][1]))), file=fh)

        if self.actions['PREFLOP']:
            for act in self.actions['PREFLOP']:
                print(self.actionString(act), file=fh)

        if self.board['FLOP']:
            print(("*** FLOP *** [%s]" %( " ".join(self.board['FLOP']))), file=fh)
        if self.actions['FLOP']:
            for act in self.actions['FLOP']:
                print(self.actionString(act), file=fh)

        if self.board['TURN']:
            print(("*** TURN *** [%s] [%s]" %( " ".join(self.board['FLOP']), " ".join(self.board['TURN']))), file=fh)
        if self.actions['TURN']:
            for act in self.actions['TURN']:
                print(self.actionString(act), file=fh)

        if self.board['RIVER']:
            print(("*** RIVER *** [%s] [%s]" %(" ".join(self.board['FLOP']+self.board['TURN']), " ".join(self.board['RIVER']) )), file=fh)
        if self.actions['RIVER']:
            for act in self.actions['RIVER']:
                print(self.actionString(act), file=fh)

        if self.shown:
            print(("*** SHOW DOWN ***"), file=fh)
            if self.showKnown:
                for name in self.shown:
                    #numOfHoleCardsNeeded = None
                    #if self.gametype['category'] in ('omahahi','omahahilo'):
                        #numOfHoleCardsNeeded = 4
                    #elif self.gametype['category'] in ('holdem'):
                        #numOfHoleCardsNeeded = 2
                    #if len(self.holecards['PREFLOP'][name][1]) == numOfHoleCardsNeeded:
                    print(("%s: shows [%s] (a hand...)" % (name, " ".join(self.holecards['PREFLOP'][name][1]))), file=fh)
            else:
                if sdOccurred:
                    for name in self.shown:
                        #if name in self.collectees or (name not in self.folded):
                        if name not in self.folded:
                            print(("%s: shows [%s] (a hand...)" % (name, " ".join(self.holecards['PREFLOP'][name][1]))), file=fh)

        for name in self.pot.returned:
            print(("Uncalled bet (%s%s) returned to %s" %(self.sym, self.pot.returned[name],name)), file=fh)
        for entry in self.collected:
            if len(self.collected) == 1 and entry[1] == (Decimal(self.sb) + Decimal(self.sb)):
                entry[1] = Decimal(self.sb) + Decimal(self.bb)
            print(("%s collected %s%s from pot" %(entry[0], self.sym, entry[1])), file=fh)

        print(("*** SUMMARY ***"), file=fh)
        print("%s | Rake %s%.2f" % (self.pot, self.sym, self.rake), file=fh)

        board = []
        for street in ["FLOP", "TURN", "RIVER"]:
            board += self.board[street]
        if board:   # sometimes hand ends preflop without a board
            print(("Board [%s]" % (" ".join(board))), file=fh)

        for player in [x for x in self.players if x[1] in players_who_act_preflop]:
            seatnum = player[0]
            name = player[1]
            rAmt = 0

            if (name in self.pot.returned):
                rAmt = self.pot.returned[name]

            if name in self.collectees and name in self.shown:
                if len(self.collectees) == 1 and rAmt == 0 and self.collectees[name] == (Decimal(self.sb) + Decimal(self.sb)):
                    wonAmt = Decimal(self.sb) + Decimal(self.bb)
                else:
                    wonAmt = self.collectees[name]

                if sdOccurred:
                    print(("Seat %d: %s showed [%s] and won (%s%s)"
                             % (seatnum,
                                name,
                                " ".join(self.holecards['PREFLOP'][name][1]),
                                self.sym,
                                wonAmt)), file=fh)
                else:
                    print(("Seat %d: %s collected (%s%s)"
                             % (seatnum, name, self.sym, wonAmt)), file=fh)

            elif name in self.collectees:
                if len(self.collectees) == 1 and rAmt == 0 and self.collectees[name] == (Decimal(self.sb) + Decimal(self.sb)):
                    wonAmt = Decimal(self.sb) + Decimal(self.bb)
                else:
                    wonAmt = self.collectees[name]

                print(("Seat %d: %s collected (%s%s)"
                             % (seatnum, name, self.sym, wonAmt)), file=fh)
            elif name in self.folded:
                print(("Seat %d: %s folded" % (seatnum, name)), file=fh)
            else:
                if sdOccurred and name in self.shown:
                    print(("Seat %d: %s showed [%s] and lost with..." % (seatnum, name, " ".join(self.holecards['PREFLOP'][name][1]))), file=fh)
                elif name in self.mucked:
                    print(("Seat %d: %s mucked [%s] " % (seatnum, name, " ".join(self.holecards['PREFLOP'][name][1]))), file=fh)
                else:
                    print(("Seat %d: %s mucked" % (seatnum, name)), file=fh)

        print("\n\n", file=fh)

class DrawHand(Hand):
    def __init__(self, config, hhc, sitename, gametype, handText, builtFrom = "HHC", handid=None):
        self.config = config
        if gametype['base'] != 'draw':
            pass
        self.streetList = ['BLINDSANTES', 'DEAL', 'DRAWONE']
        self.allStreets = ['BLINDSANTES', 'DEAL', 'DRAWONE']
        self.holeStreets = ['DEAL', 'DRAWONE']
        self.actionStreets = ['BLINDSANTES', 'DEAL', 'DRAWONE']
        if gametype['category'] in ["27_3draw","badugi", "a5_3draw"]:
            self.streetList += ['DRAWTWO', 'DRAWTHREE']
            self.allStreets += ['DRAWTWO', 'DRAWTHREE']
            self.holeStreets += ['DRAWTWO', 'DRAWTHREE']
            self.actionStreets += ['DRAWTWO', 'DRAWTHREE']
        self.discardStreets = self.holeStreets
        self.communityStreets = []
        Hand.__init__(self, self.config, sitename, gametype, handText)
        self.sb = gametype['sb']
        self.bb = gametype['bb']
        if hasattr(hhc, "in_path"):
            self.in_path = hhc.in_path
        else:
            self.in_path = "database"
        # Populate the draw hand.
        if builtFrom == "HHC":
            hhc.readHandInfo(self)
            if self.gametype['type'] == 'tour':
                self.tablename = "%s %s" % (self.tourNo, self.tablename)
            hhc.readPlayerStacks(self)
            hhc.compilePlayerRegexs(self)
            hhc.markStreets(self)
            # markStreets in Draw may match without dealing cards
            if self.streets['DEAL'] is None:
                print(("DrawHand.__init__: " + ("Street 'DEAL' is empty. Was hand '%s' cancelled?") % self.handid))
                return
            hhc.readBlinds(self)
            hhc.readAntes(self)
            hhc.readButton(self)
            hhc.readHoleCards(self)
            hhc.readShowdownActions(self)
            # Read actions in street order
            for street in self.streetList:
                if self.streets[street]:
                    hhc.readAction(self, street)
                    self.pot.markTotal(street)
            hhc.readCollectPot(self)
            hhc.readShownCards(self)
            self.pot.handid = self.handid # This is only required so Pot can throw it in totalPot
            self.totalPot() # finalize it (total the pot)
            hhc.getRake(self)
            if self.maxseats is None:
                self.maxseats = hhc.guessMaxSeats(self)
            self.sittingOut()
            hhc.readTourneyResults(self)
            hhc.readOther(self)

        elif builtFrom == "DB":
            self.maxseats = 10

    def addShownCards(self, cards, player, shown=True, mucked=False, dealt=False, string=None):
        #if player == self.hero: # we have hero's cards just update shown/mucked
        #    if shown:  self.shown.add(player)
        #    if mucked: self.mucked.add(player)
        #else:
        #    pass
        self.addHoleCards(self.actionStreets[-1], player, open=[], closed=cards, shown=shown, mucked=mucked, dealt=dealt)

        if string is not None:
            self.showdownStrings[player] = string

    def holecardsAsSet(self, street, player):
        (nc,oc) = self.holecards[street][player]
        nc = set(nc)
        oc = set(oc)
        return (nc, oc)

    def join_holecards(self, player, asList=False, street=False):
        handsize = Card.games[self.gametype['category']][5][0][1]
        holecards = ['0x']*20

        for i, _street in enumerate(self.holeStreets):
            if player in list(self.holecards[_street].keys()):
                allhole = self.holecards[_street][player][1] + self.holecards[_street][player][0]
                allhole = allhole[:handsize]
                for c in range(len(allhole)):
                    idx = c + i * 5
                    holecards[idx] = allhole[c]

        result = []
        if street is False:
            result = holecards
        elif street in self.holeStreets:
            if street == 'DEAL':
                result = holecards[0:5]
            elif street == 'DRAWONE':
                result = holecards[5:10]
            elif street == 'DRAWTWO':
                result = holecards[10:15]
            elif street == 'DRAWTHREE':
                result = holecards[15:20]
        return result if asList else " ".join(result)

    def writeHand(self, fh=sys.__stdout__):
        #self.gametype['maxSeats'] = self.maxseats
        #if self.totalpot == None:
            #self.totalPot()
            #self.rake = self.totalpot - self.totalcollected
        # PokerStars format.
        super(DrawHand, self).writeHand(fh)

        players_who_act_ondeal = set(([x[0] for x in self.actions['DEAL']]+[x[0] for x in self.actions['BLINDSANTES']]))

        for player in [x for x in self.players if x[1] in players_who_act_ondeal]:
            # Only print stacks of players who do something on deal
            print((("Seat %s: %s (%s%s in chips) ") % (player[0], player[1], self.sym, player[2])), file=fh)

        if 'BLINDSANTES' in self.actions:
            for act in self.actions['BLINDSANTES']:
                print(("%s: %s %s %s%s" % (act[0], act[1], act[2], self.sym, act[3])), file=fh)

        if 'DEAL' in self.actions:
            print(("*** DEALING HANDS ***"), file=fh)
            for player in [x[1] for x in self.players if x[1] in players_who_act_ondeal]:
                if 'DEAL' in self.holecards:
                    if player in self.holecards['DEAL']:
                        (nc,oc) = self.holecards['DEAL'][player]
                        print(("Dealt to %s: [%s]") % (player, " ".join(nc)), file=fh)
            for act in self.actions['DEAL']:
                print(self.actionString(act, 'DEAL'), file=fh)

        if 'DRAWONE' in self.actions:
            print(("*** FIRST DRAW ***"), file=fh)
            for act in self.actions['DRAWONE']:
                print(self.actionString(act, 'DRAWONE'), file=fh)
                if act[0] == self.hero and act[1] == 'discards':
                    (nc,oc) = self.holecardsAsSet('DRAWONE', act[0])
                    dc = self.discards['DRAWONE'][act[0]]
                    kc = oc - dc
                    print((("Dealt to %s [%s] [%s]") % (act[0], " ".join(kc), " ".join(nc))), file=fh)

        if 'DRAWTWO' in self.actions:
            print(("*** SECOND DRAW ***"), file=fh)
            for act in self.actions['DRAWTWO']:
                print(self.actionString(act, 'DRAWTWO'), file=fh)
                if act[0] == self.hero and act[1] == 'discards':
                    (nc,oc) = self.holecardsAsSet('DRAWONE', act[0])
                    dc = self.discards['DRAWTWO'][act[0]]
                    kc = oc - dc
                    print((("Dealt to %s [%s] [%s]") % (act[0], " ".join(kc), " ".join(nc))), file=fh)

        if 'DRAWTHREE' in self.actions:
            print(("*** THIRD DRAW ***"), file=fh)
            for act in self.actions['DRAWTHREE']:
                print(self.actionString(act, 'DRAWTHREE'), file=fh)
                if act[0] == self.hero and act[1] == 'discards':
                    (nc,oc) = self.holecardsAsSet('DRAWONE', act[0])
                    dc = self.discards['DRAWTHREE'][act[0]]
                    kc = oc - dc
                    print((("Dealt to %s [%s] [%s]") % (act[0], " ".join(kc), " ".join(nc))), file=fh)

        if 'SHOWDOWN' in self.actions:
            print(("*** SHOW DOWN ***"), file=fh)

        for name in self.pot.returned:
            print(("Uncalled bet (%s%s) returned to %s" % (self.sym, self.pot.returned[name],name)), file=fh)
        for entry in self.collected:
            print(("%s collected %s%s from pot" % (entry[0], self.sym, entry[1])), file=fh)

        print(("*** SUMMARY ***"), file=fh)
        print("%s | Rake %s%.2f" % (self.pot, self.sym, self.rake), file=fh)
        print("\n\n", file=fh)

class StudHand(Hand):
    def __init__(self, config, hhc, sitename, gametype, handText, builtFrom = "HHC", handid=None):
        self.config = config
        if gametype['base'] != 'stud':
            pass

        self.communityStreets = []
        if gametype['category'] == '5_studhi':
            self.allStreets = ['BLINDSANTES','SECOND', 'THIRD','FOURTH','FIFTH']
            self.actionStreets = ['BLINDSANTES','SECOND','THIRD','FOURTH','FIFTH']
            self.streetList = ['BLINDSANTES','SECOND','THIRD','FOURTH','FIFTH'] # a list of the observed street names in order
            self.holeStreets = ['SECOND','THIRD','FOURTH','FIFTH']
        else:
            self.allStreets = ['BLINDSANTES','THIRD','FOURTH','FIFTH','SIXTH','SEVENTH']
            self.actionStreets = ['BLINDSANTES','THIRD','FOURTH','FIFTH','SIXTH','SEVENTH']
            self.streetList = ['BLINDSANTES','THIRD','FOURTH','FIFTH','SIXTH','SEVENTH'] # a list of the observed street names in order
            self.holeStreets = ['THIRD','FOURTH','FIFTH','SIXTH','SEVENTH']
        self.discardStreets = self.holeStreets
        Hand.__init__(self, self.config, sitename, gametype, handText)
        self.sb = gametype['sb']
        self.bb = gametype['bb']
        if hasattr(hhc, "in_path"):
            self.in_path = hhc.in_path
        else:
            self.in_path = "database"
        # Populate the StudHand
        if builtFrom == "HHC":
            hhc.readHandInfo(self)
            if self.gametype['type'] == 'tour':
                self.tablename = "%s %s" % (self.tourNo, self.tablename)
            hhc.readPlayerStacks(self)
            hhc.compilePlayerRegexs(self)
            hhc.markStreets(self)
            hhc.readAntes(self)
            hhc.readBringIn(self)
            hhc.readHoleCards(self)
            hhc.readShowdownActions(self)
            # Read actions in street order
            for street in self.actionStreets:
                if street == 'BLINDSANTES': continue # sometimes someone folds in the ante round
                if self.streets[street]:
                    hhc.readAction(self, street)
                    self.pot.markTotal(street)
            hhc.readCollectPot(self)
            hhc.readShownCards(self)
            self.pot.handid = self.handid # This is only required so Pot can throw it in totalPot
            self.totalPot() # finalize it (total the pot)
            hhc.getRake(self)
            if self.maxseats is None:
                self.maxseats = hhc.guessMaxSeats(self)
            self.sittingOut()
            hhc.readTourneyResults(self)
            hhc.readOther(self)

        elif builtFrom == "DB":
            self.maxseats = 10

    def addShownCards(self, cards, player, shown=True, mucked=False, dealt=False, string=None):
        if player == self.hero: # we have hero's cards just update shown/mucked
            if shown:  self.shown.add(player)
            if mucked: self.mucked.add(player)
        else:
            if self.gametype['category'] == '5_studhi' and len(cards)>4:
                self.addHoleCards('SECOND', player, open=[cards[1]], closed=[cards[0]], shown=shown, mucked=mucked)
                self.addHoleCards('THIRD', player, open=[cards[2]], closed=[cards[1]], shown=shown, mucked=mucked)
                self.addHoleCards('FOURTH', player, open=[cards[3]], closed=cards[1:2],  shown=shown, mucked=mucked)
                self.addHoleCards('FIFTH', player, open=[cards[4]], closed=cards[1:3], shown=shown, mucked=mucked)
            if len(cards) > 6:
                self.addHoleCards('THIRD', player, open=[cards[2]], closed=cards[0:2], shown=shown, mucked=mucked)
                self.addHoleCards('FOURTH', player, open=[cards[3]], closed=[cards[2]],  shown=shown, mucked=mucked)
                self.addHoleCards('FIFTH', player, open=[cards[4]], closed=cards[2:4], shown=shown, mucked=mucked)
                self.addHoleCards('SIXTH', player, open=[cards[5]], closed=cards[2:5], shown=shown, mucked=mucked)
                self.addHoleCards('SEVENTH', player, open=[], closed=[cards[6]], shown=shown, mucked=mucked)
        if string is not None:
            self.showdownStrings[player] = string


    def addPlayerCards(self, player,  street,  open=[],  closed=[]):
        self.checkPlayerExists(player, 'addPlayerCards')
        self.holecards[street][player] = (open, closed)

    def addComplete(self, street, player, amountTo):
        amountTo = amountTo.replace(',', '') #some sites have commas
        self.checkPlayerExists(player, 'addComplete')
        Bp = self.lastBet[street]
        Bc = sum(self.bets[street][player])
        Rt = Decimal(amountTo)
        C = Bp - Bc
        Rb = Rt - C
        self._addRaise(street, player, C, Rb, Rt, 'completes')

    def addBringIn(self, player, bringin):
        if player is not None:
            if self.gametype['category']=='5_studhi':
                street = 'SECOND'
            else:
                street = 'THIRD'
            bringin = bringin.replace(',', '') #some sites have commas
            self.checkPlayerExists(player, 'addBringIn')
            bringin = Decimal(bringin)
            self.bets[street][player].append(bringin)
            self.stacks[player] -= bringin
            act = (player, 'bringin', bringin, self.stacks[player]==0)
            self.actions[street].append(act)
            self.lastBet[street] = bringin
            self.pot.addMoney(player, bringin)

    def writeHand(self, fh=sys.__stdout__):
        # PokerStars format.
        super(StudHand, self).writeHand(fh)

        players_who_post_antes = set([x[0] for x in self.actions['BLINDSANTES']])

        for player in [x for x in self.players if x[1] in players_who_post_antes]:
            # Only print stacks of players who do something preflop
            print(("Seat %s: %s (%s%s in chips)" %(player[0], player[1], self.sym, player[2])), file=fh)

        if 'BLINDSANTES' in self.actions:
            for act in self.actions['BLINDSANTES']:
                print(("%s: posts the ante %s%s" %(act[0], self.sym, act[3])), file=fh)

        if 'THIRD' in self.actions:
            dealt = 0
            for player in [x[1] for x in self.players if x[1] in players_who_post_antes]:
                if player in self.holecards['THIRD']:
                    dealt += 1
                    if dealt == 1:
                        print(("*** 3RD STREET ***"), file=fh)
                    print(self.writeHoleCards('THIRD', player), file=fh)
            for act in self.actions['THIRD']:
                print(self.actionString(act), file=fh)

        if 'FOURTH' in self.actions:
            dealt = 0
            for player in [x[1] for x in self.players if x[1] in players_who_post_antes]:
                if player in self.holecards['FOURTH']:
                    dealt += 1
                    if dealt == 1:
                        print(("*** 4TH STREET ***"), file=fh)
                    print(self.writeHoleCards('FOURTH', player), file=fh)
            for act in self.actions['FOURTH']:
                print(self.actionString(act), file=fh)

        if 'FIFTH' in self.actions:
            dealt = 0
            for player in [x[1] for x in self.players if x[1] in players_who_post_antes]:
                if player in self.holecards['FIFTH']:
                    dealt += 1
                    if dealt == 1:
                        print(("*** 5TH STREET ***"), file=fh)
                    print(self.writeHoleCards('FIFTH', player), file=fh)
            for act in self.actions['FIFTH']:
                print(self.actionString(act), file=fh)

        if 'SIXTH' in self.actions:
            dealt = 0
            for player in [x[1] for x in self.players if x[1] in players_who_post_antes]:
                if player in self.holecards['SIXTH']:
                    dealt += 1
                    if dealt == 1:
                        print(("*** 6TH STREET ***"), file=fh)
                    print(self.writeHoleCards('SIXTH', player), file=fh)
            for act in self.actions['SIXTH']:
                print(self.actionString(act), file=fh)

        if 'SEVENTH' in self.actions:
            print(("*** RIVER ***"), file=fh)
            for player in [x[1] for x in self.players if x[1] in players_who_post_antes]:
                if player in self.holecards['SEVENTH']:
                    if self.writeHoleCards('SEVENTH', player):
                        print(self.writeHoleCards('SEVENTH', player), file=fh)
            for act in self.actions['SEVENTH']:
                print(self.actionString(act), file=fh)

        if 'SHOWDOWN' in self.actions:
            print(("*** SHOW DOWN ***"), file=fh)

        for name in self.pot.returned:
            print(("Uncalled bet (%s%s) returned to %s" %(self.sym, self.pot.returned[name],name)), file=fh)
        for entry in self.collected:
            print(("%s collected %s%s from pot" %(entry[0], self.sym, entry[1])), file=fh)

        print(("*** SUMMARY ***"), file=fh)
        print("%s | Rake %s%.2f" % (self.pot, self.sym, self.rake), file=fh)

        board = []
        for s in list(self.board.values()):
            board += s
        if board:   # sometimes hand ends preflop without a board
            print(("Board [%s]" % (" ".join(board))), file=fh)

        for player in [x for x in self.players if x[1] in players_who_post_antes]:
            seatnum = player[0]
            name = player[1]
            if name in self.collectees and name in self.shown:
                print(("Seat %d: %s showed [%s] and won (%s%s)" % (seatnum, name, self.join_holecards(name), self.sym, self.collectees[name])), file=fh)
            elif name in self.collectees:
                print(("Seat %d: %s collected (%s%s)" % (seatnum, name, self.sym, self.collectees[name])), file=fh)
            elif name in self.shown:
                print(("Seat %d: %s showed [%s]" % (seatnum, name, self.join_holecards(name))), file=fh)
            elif name in self.mucked:
                print(("Seat %d: %s mucked [%s]" % (seatnum, name, self.join_holecards(name))), file=fh)
            elif name in self.folded:
                print(("Seat %d: %s folded" % (seatnum, name)), file=fh)
            else:
                print(("Seat %d: %s mucked" % (seatnum, name)), file=fh)

        print("\n\n", file=fh)

    def writeHoleCards(self, street, player):
        hc = "Dealt to %s [" % player
        if street == 'THIRD':
            if player == self.hero:
                return hc + " ".join(self.holecards[street][player][1]) + " " + " ".join(self.holecards[street][player][0]) + ']'
            else:
                return hc + " ".join(self.holecards[street][player][0]) + ']'

        if street == 'SEVENTH' and player != self.hero: return # only write 7th st line for hero
        return hc + " ".join(self.holecards[street][player][1]) + "] [" + " ".join(self.holecards[street][player][0]) + "]"

    def join_holecards(self, player, asList=False):
        holecards = []
        for street in self.holeStreets:
            if player in self.holecards[street]:
                if ((self.gametype['category'] == '5_studhi' and street == 'SECOND') or
                    (self.gametype['category'] != '5_studhi' and street == 'THIRD')):
                    holecards = holecards + self.holecards[street][player][1] + self.holecards[street][player][0]
                elif street == 'SEVENTH':
                    if player == self.hero:
                        holecards = holecards + self.holecards[street][player][0]
                    else:
                        holecards = holecards + self.holecards[street][player][1]
                else:
                    holecards = holecards + self.holecards[street][player][0]

        if asList:
            if self.gametype['category']=='5_studhi':
                if len(holecards) < 2:
                    holecards = ['0x'] + holecards
                return holecards
            else:
                if player == self.hero:
                    if len(holecards) < 3:
                        holecards = ['0x', '0x'] + holecards
                    else:
                        return holecards
                elif len(holecards) == 7:
                    return holecards
                elif len(holecards) <= 4:
                    # Non hero folded before showdown, add first two downcards
                    holecards = ['0x', '0x'] + holecards
                else:
                    pass
                if holecards == ['0x', '0x']:
                    print((("join_holecards: Player '%s' appears not to have been dealt a card"), player))
                    # If a player is listed but not dealt a card in a cash game this can occur
                    holecards = ['0x', '0x', '0x']
                return holecards
        else:
            return " ".join(holecards)

class Pot(object):

    def __init__(self):
        self.contenders   = set()
        self.committed    = {}
        self.streettotals = {}
        self.common       = {}
        self.antes        = {}
        self.total        = None
        self.returned     = {}
        self.sym          = '$' # this is the default currency symbol
        self.pots         = []
        self.handid       = 0
        self.hsb          = 0
        self.hbb          = 0
        self.collectees   = set()

    def setSym(self, sym):
        self.sym = sym

    def addPlayer(self,player):
        self.committed[player] = Decimal(0)
        self.common[player] = Decimal(0)
        self.antes[player] = Decimal(0)

    def removePlayer(self,player):
        del self.committed[player]
        del self.common[player]
        del self.antes[player]

    def addFold(self, player):
        self.contenders.discard(player)

    def addCommonMoney(self, player, amount):
        self.common[player] += amount

    def addAntes(self, player, amount):
        self.antes[player] += amount

    def addMoney(self, player, amount):
        self.contenders.add(player)
        self.committed[player] += amount

    def markTotal(self, street):
        self.streettotals[street] = sum(self.committed.values()) + sum(self.common.values())

    def getTotalAtStreet(self, street):
        if street in self.streettotals:
            return self.streettotals[street]
        return 0

    def end(self, hsb, hbb, collectees):
        self.hsb = hsb
        self.hbb = hbb
        self.collectees = collectees
        self.total = sum(self.committed.values()) + sum(self.common.values())

        # Return any uncalled bet.
        if sum(self.common.values())>0 and sum(self.common.values())==sum(self.antes.values()):
            common = sorted([ (v,k) for (k,v) in list(self.common.items())])
            try:
                lastcommon = common[-1][0] - common[-2][0]
                if lastcommon > 0: # uncalled
                    returntocommon = common[-1][1]
                    self.total -= lastcommon
                    self.common[returntocommon] -= lastcommon
            except IndexError as e:
                print((("Pot.end(): '%s': Major failure while calculating pot: '%s'"), self.handid, e))
                return

        committed = sorted([ (v,k) for (k,v) in list(self.committed.items())])

        try:
            lastbet = committed[-1][0] - committed[-2][0]
            if lastbet > 0: # uncalled
                returnto = committed[-1][1]
                self.total -= lastbet
                self.committed[returnto] -= lastbet
                self.returned[returnto] = lastbet
        except IndexError as e:
            print((("Pot.end(): '%s': Major failure while calculating pot: '%s'"), self.handid, e))
            return

        # Work out side pots
        commitsall = sorted([(v,k) for (k,v) in list(self.committed.items()) if v >0])

        try:
            while len(commitsall) > 0:
                commitslive = [(v,k) for (v,k) in commitsall if k in self.contenders]
                v1 = commitslive[0][0]
                self.pots += [(sum([min(v,v1) for (v,k) in commitsall]), set(k for (v,k) in commitsall if k in self.contenders))]
                commitsall = [((v-v1),k) for (v,k) in commitsall if v-v1 >0]
        except IndexError as e:
            print((("Pot.end(): '%s': Major failure while calculating pot: '%s'"), self.handid, e))
            return

    def __str__(self):
        if self.sym is None:
            self.sym = "C"
        if self.total is None:
            print(("Error in printing Hand object"))
            return

        if len(self.collectees) == 1:
            if (list(self.collectees.values())[0] == (Decimal(self.hsb) + Decimal(self.hbb))):
                tPot = Decimal(self.hsb) + Decimal(self.hbb)
            else:
                tPot = self.total
        #elif len(self.collectees) > 1 and self.total == (Decimal(self.hsb) + Decimal(self.hsb)):
            #tPot = Decimal(self.hsb) + Decimal(self.hbb)
        else:
            tPot = self.total
        ret = "Total pot %s%.2f" % (self.sym, tPot)
        if len(self.pots) < 2:
            return ret
        ret += " Main pot %s%.2f" % (self.sym, self.pots[0][0])

        return ret + ''.join([ (" Side pot %s%.2f." % (self.sym, self.pots[x][0]) ) for x in range(1, len(self.pots)) ])
