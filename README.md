# Ignition/Bovada Hand History Converter
This program converts Ignition/Bovada poker hand histories to PokerStars format.  It will not convert hand histories as you play.

*All hole cards are shown (optional) in HM2's latest version*

View the [Updates](#Updates) section to see details of any changes/bug fixes.  You can update to the latest version by re-downloading all of the files in this repository and replacing the old files with the new ones.

**This converter is beta software and has not been tested extensively (use it at your own risk).  It has been tested with NLHE and PLO cash game hands (and some NLHE tournament hands).  It is recommended that you backup your original hand history files (and keep them in a safe place) before using this converter.  It is also recommended that you backup your databases before using this converter.**

A large portion of the code in this project is modified code (mostly unused code was removed) from the <a href="http://fpdb.wikidot.com/" target="_blank">FPDB</a> project (<a href="https://github.com/ChazDazzle/fpdb-chaz" target="_blank">GitHub page 1</a>, <a href="https://github.com/philroberts/FPDB-for-OSX" target="_blank">GitHub page 2</a>)
<br>
<br>
<hr>
If you find this program useful and would like to make a donation click on one of the links below

<a href="http://matt57225.github.io/bovada-hand-history-converter/" target="_blank">PayPal</a>

<a href="https://www.coinbase.com/matt57225" target="_blank">BitCoin</a>

<a id="Windows"></a>
## Windows
Complete the following steps in order.

#### *Short Version*
1. Install <a href="https://www.python.org/downloads/" target="_blank">Python</a>  3.5.x (install the latest 3.5.x)
  * enable/install ```"Add Python 3.6 to PATH"``` (from the first screen) and ```"pip"``` (from the "Customize installation" screen), no other features need to be installed
2. Install <a href="https://www.riverbankcomputing.com/software/pyqt/download5" target="_blank">PyQt5</a>
  * install via <a href="http://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/" target="_blank">Command Prompt</a> with the following command:
    * ```pip3 install PyQt5```
3. Install <a href="https://pypi.python.org/pypi/pytz" target="_blank">pytz</a>
  * install via <a href="http://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/" target="_blank">Command Prompt</a> with the following command:
    * ```easy_install --upgrade pytz```
4. Download and run the converter
  * scroll to the top of this webpage and download the converter (click on ```"Clone or download"``` then click ```"Download ZIP"```)
  * extract the folder within the zip file you downloaded to a new folder on your computer
  * <a href="http://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/" target="_blank">open a Command Prompt</a> window to that folder and run the following command:
    * ```python app.py```
  * the program might load slowly the first time but each time after that it should load quickly
  * **you probably will want to make a shortcut to run the converter (see details below)**

#### *Detailed Version*
1. Install <a href="https://www.python.org/downloads/" target="_blank">Python</a>  3.5.x (install the latest 3.5.x)
  * on the installer's first screen check/enable ```"Add Python 3.6 to PATH"```
  * (optional) on the same screen you can click ```"Customize installation"``` and uncheck all features except for ```"pip"``` (pip is required for step 3)
  * click "Next" button until you see an "Install" button and then click the "Install" button (you do not need to check any more boxes)
  * when installation is complete you will have an option to "Disable path length limit", do not choose this option just click the "Close" button
  * Test if Python is installed by doing the following:
    * <a href="http://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/" target="_blank">open a Command Prompt</a> window
    * type ```python --version```
    * press Enter key
    * if a version is shown then Python is installed
    * **if this is not working you might need to sign out of your Windows user account and sign back in or restart the computer
2. Install <a href="https://www.riverbankcomputing.com/software/pyqt/download5" target="_blank">PyQt5</a>
  * <a href="http://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/" target="_blank">open a Command Prompt</a> window
  * type ```pip3 install PyQt5```
  * press Enter key
  * wait for installation to complete
3. Install <a href="https://pypi.python.org/pypi/pytz" target="_blank">pytz</a>
  * <a href="http://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/" target="_blank">open a Command Prompt</a> window
  * type ```easy_install --upgrade pytz```
  * press Enter key
  * wait for installation to complete
4. Download and run the converter
  * scroll to the top of this webpage
  * click on ```"Clone or download"``` then click ```"Download ZIP"```
  * extract the folder (this folder can be renamed) within the zip you downloaded to a new folder on your computer
  * <a href="http://www.howtogeek.com/235101/10-ways-to-open-the-command-prompt-in-windows-10/" target="_blank">open a Command Prompt</a> window to that folder (hold shift and right click in/on that folder and then click on ```"Open command window here"```)
  * type ```python app.py```
  * press Enter key and the converter should start running and the GUI should appear (you can minimize the Command Prompt window while it's running), the program might load slowly the first time but each time after that it should load quickly
  * **you probably will want to make a shortcut to run the converter by doing the following:**
    * within the folder you extracted from the zip file make a new text document (right click --> ```"New"``` --> ```"Text Document"```
    * open the text document and type ```python app.py```
    * save the document
    * rename the text document from New Text Document.txt to anyname.cmd (or anyname.bat), you might have to set Windows to show file name extensions to be able rename the file's extension (you can change the setting back to hide file extensions after completing this step)
    * you can double click on this cmd (or bat) file to run the converter, you can also make a shortcut by right clicking on the cmd (or bat) file and then clicking ```"Send to"``` --> ```"Desktop (create shortcut)"``` (the shortcut can be renamed)

## Mac
* The installation steps for Mac should be similar to the Windows installation steps
* Python might already be installed on your system, check by doing the following:
  * open a Terminal window
  * type ```python --version```
  * press Enter key
  * if a version is shown then Python is installed
  * **make sure you are using Python 3.5.x (other versions may not work)

## Misc
#### Packaging converter into a single executable file (Windows and Mac)
* This can be done using <a href="http://www.pyinstaller.org/" target="_blank">PyInstaller</a> or similar software

## Updates <a name="Updates"></a>
**4/3/2018**
- update for Python 3

**8/15/2016**
- fix for Ignition hands

**5/23/2016** 
- fixed timezone
