###
#sqlite database Wrapper
#
#
#Released under the MIT license
#Copyright (c) 2012, Jason Millward
#
#@category   misc
#@version    $Id: 1.5, 2013-10-20 20:40:30 CST $;
#@author     Jason Millward <jason@jcode.me>
#@license    http://opensource.org/licenses/MIT
###
#
# XBMC addon version by Matt De Young(giftie)

import os, sys
import sqlite3

__addon__                = sys.modules[ "__main__" ].__addon__
__addonID__              = sys.modules[ "__main__" ].__addonID__
__addon_data__           = sys.modules[ "__main__" ].__addon_data__

class database(object):

    def __init__(self):
        DATABASE = 'autoripper.db'
        
        self.con = sqlite3.connect( os.path.join( __addon_data__, DATABASE ) )

        if not self._tableExists():
            self._createStructure()

    def _tableExists(self):
        with self.con:

            cur = self.con.cursor()
            uSql = ("SELECT name ",
                    "FROM   sqlite_master ",
                    "WHERE  type='table' ",
                    "AND    name='movies' ",
                    "LIMIT 1;")

            cur.execute(''.join(uSql))
            data = cur.fetchone()

            if isinstance(data, tuple) and ''.join(data) == "movies":
                return True
            else:
                return False

    def _createStructure(self):
        with self.con:
            cur = self.con.cursor()
            uSql = ("CREATE TABLE movies ("
                    "ID         INTEGER PRIMARY KEY AUTOINCREMENT, ",
                    "path       TEXT, ",
                    "inMovie    TEXT, ",
                    "outMovie   TEXT, ",
                    "status     TEXT, ",
                    "statusText TEXT)")

            cur.execute(''.join(uSql))

    def insert(self, path, inMovie, outMovie):
        with self.con:
            cur = self.con.cursor()
            uSql = ("INSERT INTO movies ",
                    "(path, inMovie, outMovie, status, statusText) ",
                    "VALUES ('%s', '%s', '%s', 'In Queue', 'Waiting');"
                    %
                    (path, inMovie.replace("'","''"), outMovie.replace("'","''"))
            )
            cur.execute(''.join(uSql))

    def update(self, uid, status, text):
        with self.con:
            cur = self.con.cursor()
            uSql = ("UPDATE  movies ",
                   "SET     status=?, ",
                   "        statusText=? ",
                   "WHERE   ID=?")

            cur.execute(''.join(uSql), (status, text, uid))
            self.con.commit()

    def getNextMovie(self):
        with self.con:
            cur = self.con.cursor()
            uSql = ("SELECT ID, path, inMovie, outMovie ",
                   "FROM movies WHERE status = 'In Queue'")
            cur.execute(''.join(uSql))

            return cur.fetchone()

