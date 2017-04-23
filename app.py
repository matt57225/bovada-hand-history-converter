#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 matt57225
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

from gui import *
from BovadaToFpdb import Bovada

class Worker(QtCore.QThread):

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.inputDir = ''
        self.outputDir = ''
        self.moveDir = ''
        self.moveFiles = None
        self.showKnown = None
        self.fastFold = None
        self.separateTablesByMaxSeats = None
        self.saveErrors = None

    def __del__(self):
        self.exiting = True
        self.wait()

    def runConverter(self,
                     inputDir,
                     outputDir,
                     moveDir,
                     moveFiles,
                     showKnown,
                     fastFold,
                     separateTablesByMaxSeats,
                     saveErrors):
        self.inputDir = inputDir
        self.outputDir = outputDir
        self.moveDir = moveDir
        self.moveFiles = moveFiles
        self.showKnown = showKnown
        self.fastFold = fastFold
        self.separateTablesByMaxSeats = separateTablesByMaxSeats
        self.saveErrors = saveErrors
        self.start()

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

        txtFiles = [f for f in os.listdir(self.inputDir)
                    if (os.path.isfile(os.path.join(self.inputDir, f))
                        and f.endswith('.txt'))]

        totalFiles = len(txtFiles)

        errorsOutPath = os.path.join(self.outputDir, dateToday + '_errors.txt')

        if self.saveErrors:
            errorsOut = open(errorsOutPath, 'a')

        for fileName in txtFiles:
            fileInPath = os.path.join(self.inputDir, fileName)
            fileOutPath = os.path.join(self.outputDir, fileName)
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
            self.emit(QtCore.SIGNAL('updateProgressBar'), processedFiles, totalFiles)

            if processedHandsTotal > origPht:
                numFilesWithHands += 1
                if self.moveFiles:
                    fileMovePath = os.path.join(self.moveDir, fileName)
                    if not os.path.exists(fileMovePath):
                        os.rename(fileInPath, fileMovePath)

        if self.saveErrors:
            errorsOut.close()

        self.emit(QtCore.SIGNAL('runFinished'), processedHandsTotal, numFilesWithHands)

class MyWidget(QtGui.QWidget):

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.lastSelectedIDir = ''
        self.lastSelectedODir = ''
        self.lastSelectedMDir = ''

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.loadPreferences()

        self.thread = Worker()
        self.connect(self.thread, QtCore.SIGNAL('updateProgressBar'), self.updateProgressBar)
        self.connect(self.thread, QtCore.SIGNAL('runFinished'), self.runFinished)

        self.ui.inputDirButton.clicked.connect(self.selectInputDir)
        self.ui.outputDirButton.clicked.connect(self.selectOutputDir)
        self.ui.moveDirButton.clicked.connect(self.selectMoveDir)
        self.ui.runButton.clicked.connect(self.performChecks)
        self.ui.moveDirCheckBox.clicked.connect(self.savePreferences)
        self.ui.showKnownCheckBox.clicked.connect(self.savePreferences)
        self.ui.fastFoldCheckBox.clicked.connect(self.savePreferences)
        self.ui.stbmsCheckBox.clicked.connect(self.savePreferences)
        self.ui.saveErrorsCheckBox.clicked.connect(self.savePreferences)

    def parsePreferencesFile(self):
        prefs = {}
        prefsFile = open('./hhcp51386797995611001157.hhcprefs', 'r')
        for line in prefsFile:
            sIdx = line.find('=')
            prefs[line[:sIdx]] = line.strip()[(sIdx+1):]
        prefsFile.close()

        if 'inputPath' in prefs and prefs['inputPath']:
            self.ui.inputDirText.setText(prefs['inputPath'])
            self.lastSelectedIDir = prefs['inputPath']

        if 'outputPath' in prefs and prefs['outputPath']:
            self.ui.outputDirText.setText(prefs['outputPath'])
            self.lastSelectedODir = prefs['outputPath']

        if 'movePath' in prefs and prefs['movePath']:
            self.ui.moveDirText.setText(prefs['movePath'])
            self.lastSelectedMDir = prefs['movePath']

        if 'moveEnabled' in prefs and prefs['moveEnabled'] == 'False':
            self.ui.moveDirCheckBox.setChecked(False)

        if 'showKnown' in prefs and prefs['showKnown'] == 'True':
            self.ui.showKnownCheckBox.setChecked(True)

        if 'fastFold' in prefs and prefs['fastFold'] == 'True':
            self.ui.fastFoldCheckBox.setChecked(True)

        if 'separateTablesByMaxSeats' in prefs and prefs['separateTablesByMaxSeats'] == 'True':
            self.ui.stbmsCheckBox.setChecked(True)

        if 'saveErrors' in prefs and prefs['saveErrors'] == 'True':
            self.ui.saveErrorsCheckBox.setChecked(True)

    def createNewPreferencesFile(self):
        prefsFile = open('./hhcp51386797995611001157.hhcprefs', 'w')
        prefsFile.write('inputPath=\n' +
                        'outputPath=\n' +
                        'movePath=\n' +
                        'moveEnabled=True\n' +
                        'showKnown=False\n' +
                        'fastFold=False\n' +
                        'separateTablesByMaxSeats=False\n' +
                        'saveErrors=False\n')
        prefsFile.close()

    def savePreferences(self):
        prefsFile = open('./hhcp51386797995611001157.hhcprefs', 'w')
        prefsFile.write('inputPath=' + self.lastSelectedIDir + '\n' +
                        'outputPath=' + self.lastSelectedODir + '\n' +
                        'movePath=' + self.lastSelectedMDir + '\n')

        if self.ui.moveDirCheckBox.isChecked():
            prefsFile.write('moveEnabled=True\n')
        else:
            prefsFile.write('moveEnabled=False\n')

        if self.ui.showKnownCheckBox.isChecked():
            prefsFile.write('showKnown=True\n')
        else:
            prefsFile.write('showKnown=False\n')

        if self.ui.fastFoldCheckBox.isChecked():
            prefsFile.write('fastFold=True\n')
        else:
            prefsFile.write('fastFold=False\n')

        if self.ui.stbmsCheckBox.isChecked():
            prefsFile.write('separateTablesByMaxSeats=True\n')
        else:
            prefsFile.write('separateTablesByMaxSeats=False\n')

        if self.ui.saveErrorsCheckBox.isChecked():
            prefsFile.write('saveErrors=True\n')
        else:
            prefsFile.write('saveErrors=False\n')

        prefsFile.close()

    def updateProgressBar(self, processedFiles, totalFiles):
        self.ui.progressBar.setValue((float(processedFiles) / totalFiles) * 100)

    def runFinished(self, processedHandsTotal, numFilesWithHands):
        self.ui.statusLabel.setStyleSheet('color: black')
        self.ui.statusLabel.setText(str(processedHandsTotal) +
                                    ' hands processed in ' +
                                    str(numFilesWithHands) +
                                    ' file(s)')

        self.ui.runButton.setEnabled(True)
        self.ui.moveDirCheckBox.setEnabled(True)
        self.ui.showKnownCheckBox.setEnabled(True)
        self.ui.fastFoldCheckBox.setEnabled(True)
        self.ui.stbmsCheckBox.setEnabled(True)
        self.ui.saveErrorsCheckBox.setEnabled(True)

    def deactivateButtons(self):
        self.ui.runButton.setEnabled(False)
        self.ui.moveDirCheckBox.setEnabled(False)
        self.ui.showKnownCheckBox.setEnabled(False)
        self.ui.fastFoldCheckBox.setEnabled(False)
        self.ui.stbmsCheckBox.setEnabled(False)
        self.ui.saveErrorsCheckBox.setEnabled(False)

    def checkValidDirs(self, inputText, outputText, moveText, moveFiles):
        invalidDirs = []
        msg = ''

        inputDirValid = True
        outputDirValid = True
        moveDirValid = True

        if not os.path.exists(inputText):
            inputDirValid = False
            invalidDirs.append('input')
        else:
            self.lastSelectedIDir = inputText

        if not os.path.exists(outputText):
            outputDirValid = False
            invalidDirs.append('ouput')
        else:
            self.lastSelectedODir = outputText

        if os.path.exists(moveText):
            self.lastSelectedMDir = moveText

        self.savePreferences()

        if moveFiles:
            if not os.path.exists(moveText):
                moveDirValid = False
                invalidDirs.append('move')

            if inputDirValid and outputDirValid and moveDirValid:
                return True
            else:
                for i in invalidDirs:
                    msg += (i + '/')
                msg = msg[:-1]
                self.ui.statusLabel.setStyleSheet('color: red')
                self.ui.statusLabel.setText(msg + ' directory is not valid')
                return False
        else:
            if inputDirValid and outputDirValid:
                return True
            else:
                for i in invalidDirs:
                    msg += (i + '/')
                msg = msg[:-1]
                self.ui.statusLabel.setStyleSheet('color: red')
                self.ui.statusLabel.setText(msg + ' directory is not valid')
                return False

    def performChecks(self):
        inputText = str(self.ui.inputDirText.text()).strip()
        outputText = str(self.ui.outputDirText.text()).strip()
        moveText = str(self.ui.moveDirText.text()).strip()

        showKnown = False
        fastFold = False
        separateTablesByMaxSeats = False
        saveErrors = False

        if self.ui.showKnownCheckBox.isChecked():
            showKnown = True

        if self.ui.fastFoldCheckBox.isChecked():
            fastFold = True

        if self.ui.stbmsCheckBox.isChecked():
            separateTablesByMaxSeats = True

        if self.ui.saveErrorsCheckBox.isChecked():
            saveErrors = True

        if self.ui.moveDirCheckBox.isChecked():
            if not inputText or not outputText or not moveText:
                self.ui.statusLabel.setStyleSheet('color: red')
                self.ui.statusLabel.setText('input/output/move directory not specified')
            else:
                if inputText == outputText or inputText == moveText or outputText == moveText:
                    self.ui.statusLabel.setStyleSheet('color: red')
                    self.ui.statusLabel.setText('input/output/move directories cannot be the same')
                else:
                    if self.checkValidDirs(inputText, outputText, moveText, True):
                        self.deactivateButtons()
                        self.ui.statusLabel.setStyleSheet('color: black')
                        self.ui.statusLabel.setText('Running...')
                        self.thread.runConverter(inputText,
                                                 outputText,
                                                 moveText,
                                                 True,
                                                 showKnown,
                                                 fastFold,
                                                 separateTablesByMaxSeats,
                                                 saveErrors)
        else:
            if not inputText or not outputText:
                self.ui.statusLabel.setStyleSheet('color: red')
                self.ui.statusLabel.setText('input/output directory not specified')
            else:
                if inputText == outputText:
                    self.ui.statusLabel.setStyleSheet('color: red')
                    self.ui.statusLabel.setText('input/output directories cannot be the same')
                else:
                    if self.checkValidDirs(inputText, outputText, moveText, False):
                        self.deactivateButtons()
                        self.ui.statusLabel.setStyleSheet('color: black')
                        self.ui.statusLabel.setText('Running...')
                        self.thread.runConverter(inputText,
                                                 outputText,
                                                 moveText,
                                                 False,
                                                 showKnown,
                                                 fastFold,
                                                 separateTablesByMaxSeats,
                                                 saveErrors)

    def selectInputDir(self):
        iDir = QtGui.QFileDialog.getExistingDirectory(None, '', self.lastSelectedIDir)
        if iDir:
            self.ui.inputDirText.setText(iDir)
            self.lastSelectedIDir = iDir

    def selectOutputDir(self):
        oDir = QtGui.QFileDialog.getExistingDirectory(None, '', self.lastSelectedODir)
        if oDir:
            self.ui.outputDirText.setText(oDir)
            self.lastSelectedODir = oDir

    def selectMoveDir(self):
        mDir = QtGui.QFileDialog.getExistingDirectory(None, '', self.lastSelectedMDir)
        if mDir:
            self.ui.moveDirText.setText(mDir)
            self.lastSelectedMDir = mDir

    def loadPreferences(self):
        if not os.path.exists('./hhcp51386797995611001157.hhcprefs'):
            self.createNewPreferencesFile()
        else:
            self.parsePreferencesFile()

if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    Form = MyWidget()
    Form.show()

    sys.exit(app.exec_())
