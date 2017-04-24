#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2017 matt57225
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import codecs
import datetime

from StringIO import StringIO

from BovadaToFpdb import Bovada

class Worker():

    def __init__(self, parent = None):
        self.inputPath = ''
        self.outputPath = ''
        self.movePath = ''
        self.moveFiles = True
        self.showKnown = 'False'
        self.fastFold = 'True'
        self.separateTablesByMaxSeats = 'False'
        self.saveErrors = 'False'

    def runConverter(self,
                     inputPath,
                     outputPath,
                     movePath,
                     moveFiles,
                     showKnown,
                     fastFold,
                     separateTablesByMaxSeats,
                     saveErrors):
        self.inputPath = inputPath
        self.outputPath = outputPath
        self.movePath = movePath
        self.moveFiles = moveFiles
        self.showKnown = showKnown
        self.fastFold = fastFold
        self.separateTablesByMaxSeats = separateTablesByMaxSeats
        self.saveErrors = saveErrors
        self.run()

    def readFile(self, fileIn):
        while True:
            fileContents = fileIn.read(10000)
            if not fileContents:
                break
            yield fileContents

    def run(self):
        dateToday = datetime.date.today().strftime("%Y%m%d")
        converter = Bovada()
        handInput = ''
        processedHandsTotal = 0
        origPht = 0
        numFilesWithHands = 0
        processedFiles = 0

        txtFiles = [f for f in os.listdir(self.inputPath)
                    if (os.path.isfile(os.path.join(self.inputPath, f))
                        and f.endswith('.txt'))]

        totalFiles = len(txtFiles)

        errorsOutPath = os.path.join(self.outputPath, dateToday + '_errors.txt')

        if self.saveErrors == 'True':
            errorsOut = open(errorsOutPath, 'a')

        for fileName in txtFiles:
            fileInPath = os.path.join(self.inputPath, fileName)
            fileOutPath = os.path.join(self.outputPath, fileName)
            fileOutPath = fileOutPath.replace('.txt', '_' + dateToday + '.txt')
            converter.in_path = fileName
            origPht = processedHandsTotal
            hhStr = ''

            fileIn = codecs.open(fileInPath, 'r', 'utf-8-sig')

            for chunk in self.readFile(fileIn):
                hhStr += chunk

            fileIn.close()

            hhStr = hhStr.replace('Bodog.eu Hand #', '\n\nBodog.eu Hand #')
            hhStr = hhStr.replace('Bovada Hand #', '\n\nBovada Hand #')
            hhStr = hhStr.replace('Ignition Hand #', '\n\nIgnition Hand #')
            hhStr += '\n\n'
            lines = hhStr.splitlines(True)

            fileOut = open(fileOutPath, 'a')

            for line in lines:
                handInput += line
                if line.strip() == '':
                    if handInput.strip() != '':
                        hand = converter.processHand(handInput,
                                                     self.showKnown,
                                                     self.fastFold,
                                                     self.separateTablesByMaxSeats)
                        if hand:
                            processedHandsTotal += 1
                            handText = StringIO()
                            hand.writeHand(handText)
                            handOutput = handText.getvalue()
                            #fileOut = open(fileOutPath, 'a')
                            fileOut.write(handOutput)
                            #fileOut.close()
                        else:
                            if self.saveErrors:
                                #errorsOut = open(errorsOutPath, 'a')
                                errorsOut.write(handInput + '\n\n')
                                #errorsOut.close()
                    handInput = ''
                    handOutput = ''

            fileOut.close()

            processedFiles += 1
            sys.stdout.write('%d of %d files processed - %d%% \r'
                % (processedFiles, 
                   totalFiles,
                   ((float(processedFiles) / totalFiles) * 100)))
            sys.stdout.flush()

            if processedHandsTotal > origPht:
                numFilesWithHands += 1
                if self.moveFiles == True:
                    fileMovePath = os.path.join(self.movePath, fileName)
                    if not os.path.exists(fileMovePath):
                        os.rename(fileInPath, fileMovePath)

        if self.saveErrors == 'True':
            errorsOut.close()

        sys.stdout.write('%d hands processed in %d file(s) \r'
                % (processedHandsTotal, numFilesWithHands))
        sys.stdout.flush()

class AppNoGui():

    def __init__(self, parent = None):
        self.inputPath = ''
        self.outputPath = ''
        self.movePath = ''
        self.moveEnabled = 'True'
        self.showKnown = 'False'
        self.fastFold = 'True'
        self.separateTablesByMaxSeats = 'False'
        self.saveErrors = 'False'
        
        self.conv = Worker()

        self.loadPreferences()
        self.performChecks()
        
    def parsePreferencesFile(self):
        prefs = {}
        prefsFile = open('./hhcp51386797995611001157.hhcprefs', 'r')
        for line in prefsFile:
            sIdx = line.find('=')
            prefs[line[:sIdx]] = line.strip()[(sIdx+1):]
        prefsFile.close()

        if 'inputPath' in prefs and prefs['inputPath']:
            self.inputPath = prefs['inputPath']

        if 'outputPath' in prefs and prefs['outputPath']:
            self.outputPath = prefs['outputPath']

        if 'movePath' in prefs and prefs['movePath']:
            self.movePath = prefs['movePath']

        if 'moveEnabled' in prefs and prefs['moveEnabled']:
            self.moveEnabled = prefs['moveEnabled']

        if 'showKnown' in prefs and prefs['showKnown']:
            self.showKnown = prefs['showKnown']

        if 'fastFold' in prefs and prefs['fastFold']:
            self.fastFold = prefs['fastFold']

        if 'separateTablesByMaxSeats' in prefs and prefs['separateTablesByMaxSeats']:
            self.separateTablesByMaxSeats = prefs['separateTablesByMaxSeats']

        if 'saveErrors' in prefs and prefs['saveErrors']:
            self.saveErrors = prefs['saveErrors']
        
    def createNewPreferencesFile(self):
        prefsFile = open('./hhcp51386797995611001157.hhcprefs', 'w')
        prefsFile.write('inputPath=\n' +
                        'outputPath=\n' +
                        'movePath=\n' +
                        'moveEnabled=True\n' +
                        'showKnown=False\n' +
                        'fastFold=True\n' +
                        'separateTablesByMaxSeats=False\n' +
                        'saveErrors=False\n')
        prefsFile.close()

    def checkValidDirs(self):
        invalidDirs = []
        msg = ''

        inputPathValid = True
        outputPathValid = True
        movePathValid = True

        if not os.path.exists(self.inputPath):
            inputPathValid = False
            invalidDirs.append('input')

        if not os.path.exists(self.outputPath):
            outputPathValid = False
            invalidDirs.append('ouput')

        if self.moveEnabled == 'True':
            if not os.path.exists(self.movePath):
                movePathValid = False
                invalidDirs.append('move')

            if inputPathValid and outputPathValid and movePathValid:
                return True
            else:
                for i in invalidDirs:
                    msg += (i + '/')
                msg = msg[:-1]
                print(msg + ' directory is not valid')
                return False
        else:
            if inputPathValid and outputPathValid:
                return True
            else:
                for i in invalidDirs:
                    msg += (i + '/')
                msg = msg[:-1]
                print(msg + ' directory is not valid')
                return False

    def performChecks(self):
        if self.moveEnabled == 'True':
            if self.inputPath == '' or self.outputPath == '' or self.movePath == '':
                print('input/output/move directory not specified')
            else:
                if self.inputPath == self.outputPath or self.inputPath == self.movePath or self.outputPath == self.movePath:
                    print('input/output/move directories cannot be the same')
                else:
                    if self.checkValidDirs():
                        print('Running...')
                        self.conv.runConverter(self.inputPath,
                                                 self.outputPath,
                                                 self.movePath,
                                                 True,
                                                 self.showKnown,
                                                 self.fastFold,
                                                 self.separateTablesByMaxSeats,
                                                 self.saveErrors)
        else:
            if self.inputPath == '' or self.outputPath == '':
                print('input/output directory not specified')
            else:
                if self.inputPath == self.outputPath:
                    print('input/output directories cannot be the same')
                else:
                    if self.checkValidDirs():
                        print('Running...')
                        self.conv.runConverter(self.inputPath,
                                                 self.outputPath,
                                                 self.movePath,
                                                 False,
                                                 self.showKnown,
                                                 self.fastFold,
                                                 self.separateTablesByMaxSeats,
                                                 self.saveErrors)
                                                 
    def loadPreferences(self):
        if not os.path.exists('./hhcp51386797995611001157.hhcprefs'):
            self.createNewPreferencesFile()
        else:
            self.parsePreferencesFile()

if __name__ == "__main__":
    import sys
    app = AppNoGui()
