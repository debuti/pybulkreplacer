#!/usr/bin/env python
###############################################################################################
#  Author: 
_author = '<a href="mailto:debuti@gmail.com">Borja Garcia</a>'
# Program: 
_name = 'pyBulkReplacer'
# Descrip: 
_description = '''Multiline regexp replacer'''
# Version: 
_version = '0.0.2'
#    Date:
_date = '20100203'
# License: This script doesn't require any license since it's not intended to be redistributed.
#          In such case, unless stated otherwise, the purpose of the author is to follow GPLv3.
# History: 
#          0.0.2 (2010-02-03:19:00)
#            -Fixed some bugs
#            -Added loop-avoiding technique
#          0.0.0 (2009-11-26:00:00)
#            -Initial release
###############################################################################################

#TODO
# No funciona con xargs, verificar esto (funciona con find . -type f -print -exec pyBulkReplacer.py -b"T8110" -a"CULOZ" -s3 {} \;)

# imports
import logging
import sys
import doctest
import datetime, time
import os
import optparse
import inspect
import re

# Parameters n' Constants
APP_PATH = os.getcwd() + os.path.sep + '.' + _name 
LOG_PATH = APP_PATH + os.path.sep + 'logs'
LOG_FILENAME = LOG_PATH + os.path.sep + _name + '_' + time.strftime("%Y%m%d_%H%M%S") + '.log'

# Global variables
global now
now = time.strftime("%Y-%m-%d:%H:%M:%S")

# Error declaration
error = { "" : "",
          "" : "",
          "" : "" }

# Usage function, logs, utils and check input
def createWorkDir():
    '''This function is for creating the working directory, if its not already
    '''
    if not os.path.isdir(APP_PATH):
        os.mkdir(APP_PATH)
    if not os.path.isdir(LOG_PATH):
        os.mkdir(LOG_PATH)
    if not os.path.isfile(LOG_FILENAME):
        f = open(LOG_FILENAME, "w")
        f.close()

def openLog():
    '''This function is for initialize the logging job
    '''
  
    global logger

    desiredLevel = logging.DEBUG
    logger = logging.getLogger(_name)
    logger.setLevel(desiredLevel)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOG_FILENAME)
    fh.setLevel(desiredLevel)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(desiredLevel)
    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

def closeLog():
    '''This function is for shutdown the logging job
    '''
  
    logging.shutdown()

def checkInput():
    '''This function is for treat the user command line parameters.
    '''

    #Create instance of OptionParser Module, included in Standard Library
    p = optparse.OptionParser(description=_description,
                              prog=_name,
                              version=_version,
                              usage='''%prog [options] filename''') 
    p.add_option('--before', '-b', action="store", type="string", dest="old_regexp", help='Regular expression to search for')
    p.add_option('--after', '-a', action="store", type="string", dest="new_string", help='New text to replace with')
    p.add_option('--surround', '-s', action="store", type="int", dest="surround", help='The number of surrounding lines to display')
    p.add_option('--notpreview','-n', action="store_true", dest="not_do_preview", help='Do not ask to replace the coincidence before doing it')

    #Parse the commandline
    options, arguments = p.parse_args()

    #Decide what to do
    if options.old_regexp is None or options.new_string is None or len(arguments) < 1 :
        p.print_help()
        sys.exit(-1)
    else:
        if options.surround is None: 
            surround = 1
        else:
            surround = options.surround
        old_regexp = options.old_regexp
        new_string = options.new_string
        not_do_preview = options.not_do_preview
        filename = arguments
        return [old_regexp, new_string, surround, not_do_preview, filename]


# Helper functions

def findNReplaceRegExp(file_name, regexp, replaceString, verbose=False, confirmationNeeded=False, surroundingLines = 1):
    '''Replaces the oldString with the replaceString in the file given,\
       returns the number of replaces
    '''

    class SearchIterator:
        '''A Simple class to iterate over a text and return ocurrencies
        '''
        _text=''
        _lastPosition=0
        _cregexp = None

        def __init__ (self, text, regexp):
            self._text = text     
            self._lastPosition=0  
            self._cregexp = re.compile(regexp, re.MULTILINE | re.DOTALL)
    
        def reset (self, text, regexp):
            self._text = text
            self._lastPosition=0
            self._cregexp = re.compile(regexp, re.MULTILINE | re.DOTALL)
    
        def reset (self):
            self.reset('', '')
    
        def findNext (self):
            '''Returns the position and length of the next ocurrence
            '''
            if self.thereAreItemsLeft():
                coincidence = self._cregexp.search(self._text)
                # return from coincidence and length
                result = [self._lastPosition + coincidence.start(), coincidence.end() - coincidence.start()]
                # update last position to provide right information about position
                self._lastPosition = self._lastPosition + coincidence.end()
                self._text = self._text[coincidence.end():]
            else:
                result = None
 
            return result
 
        def shift (self, number):
            '''Shifts by a number of positions the actual indexf
            '''
            self._lastPosition = self._lastPosition + number
       
        def thereAreItemsLeft (self):
            '''Returns if there are items left to occur
            '''
            if self._cregexp.search(self._text):
                return True
            else:
                return False

    def extendedFind(stringToAnalize, substringToSearch, startPosition, endPosition, numberOfCoincidence = 1):
        '''Finds a substring in a string, like find, but adds support to search\
           for the second or consecutive coincidences. If not found return the last encountered
        '''
        coincidencesCounted = 0
        lastCoincidencePosition = startPosition

        while coincidencesCounted < numberOfCoincidence:
            index = stringToAnalize.find(substringToSearch, lastCoincidencePosition, endPosition)
            if index == -1: 
                break
            else:
                lastCoincidencePosition = index + 1
                coincidencesCounted = coincidencesCounted + 1
     
        if coincidencesCounted != numberOfCoincidence:
            return lastCoincidencePosition
        else:
            return index

    def extendedRFind(stringToAnalize, substringToSearch, startPosition, endPosition, numberOfCoincidence = 1):
        '''Finds a substring in a string, like find, but adds support to search\
           for the second or consecutive coincidences. If not found return the last encountered
        '''
        coincidencesCounted = 0
        lastCoincidencePosition = endPosition
    
        while coincidencesCounted < numberOfCoincidence:
            index = stringToAnalize.rfind(substringToSearch, startPosition, lastCoincidencePosition)
            if index == -1: 
                break
            else:
                lastCoincidencePosition = index - 1
                coincidencesCounted = coincidencesCounted + 1
     
        if coincidencesCounted != numberOfCoincidence:
            return lastCoincidencePosition
        else:
            return index

    # open file for read
    file_in = open(file_name, 'r')
    myFile = file_in.read()
    file_in.close()

    # initialize local variables
    mySearchIterator = SearchIterator (myFile, regexp)
    ocurrences = 0
    isAborted = False

    while mySearchIterator.thereAreItemsLeft():
        [position, length] = mySearchIterator.findNext()
        print "found at " + str(position)
        # new string
        myNewFile = myFile [:position] + replaceString + myFile [position + length:]

        if verbose == True:
            # calculate the segment of text in which the resolution will be done
            from_index = extendedRFind(myFile, "\n", 0, position, surroundingLines + 1)
            to_index_old = extendedFind(myFile, "\n", position + length, len(myFile), surroundingLines + 1)
            to_index_new = extendedFind(myNewFile, "\n", position + len(replaceString), len(myNewFile), surroundingLines + 1)
            # do some adjusting if we fall out of limits
            if myFile[from_index] != "\n":
                from_index=0
            if to_index_old == len(myFile) or myFile[to_index_old] != "\n":
                to_index_old=len(myFile) - 1

            # print the old string and the new string
            print '- ' + myFile[from_index:to_index_old]
            print '+ ' + myNewFile[from_index:to_index_new]

            if confirmationNeeded:
                # ask user if this should be done
                question = raw_input('Accept changes? [Yes (Y), No (n), Abort (a)] ')
                # print new line
                print
                question = str.lower(question)
                if question == 'a':
                    isAborted = True
                    print "Changes to file " + file_name + " aborted"
                    break
                elif question == 'n':
                    pass
                else:
                    myFile = myNewFile
                    mySearchIterator.shift (len(replaceString) - length)
                    ocurrences = ocurrences + 1
            else:
                myFile = myNewFile
                mySearchIterator.shift (len(replaceString) - length)
                ocurrences = ocurrences + 1                
        else:
            myFile = myNewFile
            mySearchIterator.shift (len(replaceString) - length)
            ocurrences = ocurrences + 1        

    # if some text was replaced, overwrite the original file
    if ocurrences > 0 and not isAborted:
        # open the file for overwritting
        file_out = open(file_name, 'w')
        file_out.write(myFile)
        file_out.close()
        if verbose: print "File " + file_name + " written"

    return ocurrences


# Main function
def main(old_regexp, new_string, surround, not_do_preview, filenames):
    '''This is the main procedure
    '''

    for filename in filenames:
        if not_do_preview:
            findNReplaceRegExp(filename, old_regexp, new_string, False, False, surround)
        else:
            findNReplaceRegExp(filename, old_regexp, new_string, True, True, surround)

# Entry point
if __name__ == '__main__':
    [old_regexp, new_string, surround, not_do_preview, filename] = checkInput()
#    createWorkDir()
#    openLog()
    main(old_regexp, new_string, surround, not_do_preview, filename)
#    closeLog()
