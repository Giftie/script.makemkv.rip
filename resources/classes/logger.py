"""
Simple logging class

This class provides a cleaner way for adding logging to every file


Released under the MIT license
Copyright (c) 2012, Jason Millward

@category   misc
@version    $Id: 1.5, 2013-10-20 20:40:30 CST $;
@author     Jason Millward <jason@jcode.me>
@license    http://opensource.org/licenses/MIT
"""

import logging
import sys


class logger(object):

    def __init__(self, name, debug):
        frmt = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            "%Y-%m-%d %H:%M:%S"
        )

        if debug == True:
            logLevel = logging.DEBUG
        else:
            logLevel = logging.INFO

        self.sh = logging.StreamHandler(sys.stdout)
        self.sh.setLevel(logLevel)
        self.sh.setFormatter(frmt)

        self.fh = logging.FileHandler('autoripper.log')
        self.fh.setLevel(logLevel)
        self.fh.setFormatter(frmt)

        self.log = logging.getLogger(name)
        self.log.setLevel(logLevel)
        self.log.addHandler(self.sh)
        self.log.addHandler(self.fh)

    def __del__(self):
        self.log.removeHandler(self.sh)
        self.log.removeHandler(self.fh)
        self.log = None

    def debug(self, msg):
        self.log.debug(msg)

    def info(self, msg):
        self.log.info(msg)

    def warn(self, msg):
        self.log.warn(msg)

    def error(self, msg):
        self.log.error(msg)

    def critical(self, msg):
        self.log.critical(msg)
