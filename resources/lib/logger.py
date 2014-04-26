# xbmc logging 

import xbmc
import sys

__addon__                = sys.modules[ "__main__" ].__addon__
__addonID__              = sys.modules[ "__main__" ].__addonID__
__addon_name__           = sys.modules[ "__main__" ].__addon_name__
__addon_data__           = sys.modules[ "__main__" ].__addon_data__
__addon_path__           = sys.modules[ "__main__" ].__addon_path__

class logger(object):

    def __init__(self, name, debug):
        if debug == True:
            self.logLevel = xbmc.LOGDEBUG
        else:
            self.logLevel = xbmc.LOGNOTICE

    def log( self, text ):
        if type( text ).__name__=='unicode':
            text = text.encode('utf-8')
        message = ('[%s] - %s' % ( __addon_name__ ,text.__str__() ) )
        xbmc.log( msg=message, level=self.logLevel )
        
    def debug(self, msg):
        previous = self.logLevel
        self.logLevel = xbmc.LOGDEBUG
        self.log(msg)
        self.logLevel = previous
        
    def info(self, msg):
        previous = self.logLevel
        self.logLevel = xbmc.LOGNOTICE
        self.log(msg)
        self.logLevel = previous

    def warn(self, msg):
        previous = self.logLevel
        self.logLevel = xbmc.LOGNOTICE
        self.log(msg)
        self.logLevel = previous

    def error(self, msg):
        previous = self.logLevel
        self.logLevel = xbmc.LOGERROR
        self.log(msg)
        self.logLevel = previous

    def critical(self, msg):
        previous = self.logLevel
        self.logLevel = xbmc.LOGERROR
        self.log(msg)
        self.logLevel = previous
