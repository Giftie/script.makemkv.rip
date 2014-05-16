###
#MakeMKV CLI Wrapper
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
import sys
__addon_data__           = sys.modules[ "__main__" ].__addon_data__
__addon_path__           = sys.modules[ "__main__" ].__addon_path__

import subprocess
import os
import re
import csv
import database
import logger
import xbmcvfs

class makeMKV(object):
    """
        This class acts as a python wrapper to the MakeMKV CLI.
    """
    
    NEWLINE_CHAR = '\n'
    ATTRIBUTE_IDS = { '0': 'Unknown',  '1': 'Type', '2': 'Name', '3': 'Lng Code', '4': 'Lng Name', '5': 'Codec ID', '6': 'Codec Short', '7': 'Codec Long',
                      '8': 'Chapter Count', '9': 'Duration', '10': 'Disk Size', '11': 'Disk Size Bytes', '12': 'Stream Type Extension', '13': 'Bitrate',
                      '14': 'Audio Channels Cnt', '15': 'Angle Info', '16': 'Source File Name', '17': 'Audio Sample Rate', '18': 'Audio Sample Size',
                      '19': 'Video Size', '20': 'Video Aspect Ratio', '21': 'Video Frame Rate', '22': 'Stream Flags', '23': 'Date Time',
                      '24': 'Original Title ID', '25': 'Segments Count', '26': 'Segments Map', '27': 'Output Filename', '28': 'Metadata Lng Code',
                      '29': 'Metadata Lng Name', '30': 'Tree Info', '31': 'Panel Title', '32': 'Volume Name', '33': 'Order Weight', '34': 'Output Format',
                      '35': 'Output Format Description', '36': 'MaxValue', '37': 'ap_iaPanelText', '38': 'ap_iaMkvFlags', '39': 'ap_iaMkvFlagsText', }
    COL_PATTERN = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')
    RESERVED_CHAR_MAP = { '/':'-', '\\':'-', '?':' ', '%':' ', '*':' ',
                         ':':'-', '|':'-', '"':' ', '<':' ', '>':' ', }

    def __init__(self, general_settings):
        """
            Initialises the variables that will be used in this class

            Inputs:
                None

            Outputs:
                None
        """
        self.discIndex = 0
        self.movieName = ""
        self.path = ""
        self.movieName = ""
        self.temp_path = general_settings[ "temp_folder" ]
        self.makemkvcon_path = os.path.join( general_settings[ "mkv_folder" ], "makemkvcon" )
        self.minLength = general_settings[ "mkv_min_length" ]
        self.cacheSize = general_settings[ "mkv_cache" ]
        self.log = logger.logger("makemkv", True)

    def disc_info(self, disc_id, thread_id=None, ):
        info_out = {
            'disc'  :   {},
            'tracks':   {},
            'disc_id':  disc_id,
            'cmd'   :   'disc_info',
        }
        try:
            disc_info = subprocess.check_output([
                self.makemkvcon_path, '--noscan', '-r',
                'info', 'dev:%s' % disc_id,
                ])
        except subprocess.CalledProcessError as e:
            logging.error(e.output)
            raise
        track_id = -1
        for line in disc_info.split(makeMKV.NEWLINE_CHAR):
            split_line = makeMKV.COL_PATTERN.split(line)[1::2]
            if len(split_line) > 1 and split_line[0] != 'TCOUNT':
                if line[0] == 'C':  #<  Disc Info
                    try:
                        info_out['disc'][makeMKV.ATTRIBUTE_IDS[split_line[0].split(':')[-1]]] = split_line[-1].replace('"','')
                    except KeyError:
                        info_out['disc'][split_line[0].split(':')[-1]] = split_line[-1].replace('"','')
                else:
                    if line[0] == 'T':
                        track_id = split_line[0].split(':')[-1]
                        try:    #<  If new track_id, dim var
                            track_info = info_out['tracks'][track_id]
                        except KeyError:
                            track_info = info_out['tracks'][track_id] = {'cnts':{'Subtitles':0,'Video':0,'Audio':0}}
                        try:
                            track_info[makeMKV.ATTRIBUTE_IDS[split_line[1]]] = split_line[-1].replace('"','')
                        except Exception:
                            track_info[split_line[1]] = split_line[-1].replace('"','')
                    if line[0] == 'S':
                        track_part_id = split_line[1]
                        try:    #<  If new track_id, dim var
                            info_out['tracks'][track_id]['track_parts']
                        except KeyError:
                            info_out['tracks'][track_id]['track_parts'] = {}
                        try:    #<  If new track_id, dim var
                            track_info = info_out['tracks'][track_id]['track_parts'][track_part_id]
                        except KeyError:
                            track_info = info_out['tracks'][track_id]['track_parts'][track_part_id] = {}
                        try:
                            track_info[makeMKV.ATTRIBUTE_IDS[split_line[2]]] = split_line[-1].replace('"','')
                        except KeyError:
                            track_info[split_line[2]] = split_line[-1].replace('"','')
        #   Count the track parts
        for track_id,track_info in info_out['tracks'].iteritems():
            for part_id, track_part in track_info['track_parts'].iteritems():
                try:
                    info_out['tracks'][track_id]['cnts'][track_part['Type']] += 1
                except KeyError:    #<  Type not avail, should be good to ignore?
                    pass
        return info_out
        
    def _queueMovie(self):
        """
            Adds the recently ripped movie to the queue db for the compression
                script to handle later on

            Inputs:
                None

            Outputs:
                None
        """
        self.log.info( "Storing movie in to queue database" )
        db = database.database()
        movie = ""

        path = os.path.join( self.path, self.movieName )
        folders, files = xbmcvfs.listdir( path )
        for file in files:
            if file.endswith(".mkv"):
                movie = file
                break

        outMovie = "%s.mkv" % self.movieName
        db.insert(path, inMovie=movie, outMovie=outMovie)


    def _cleanTitle(self):
        """
            Removes the extra bits in the title and removes whitespace

            Inputs:
                None

            Outputs:
                None
        """
        tmpName = self.movieName
        # A little fix for extended editions (eg; Die Hard 4)
        tmpName = tmpName.title().replace("Extended_Edition", "")

        # Remove Special Edition
        tmpName = tmpName.replace("Special_Edition", "")

        # Remove Disc X from the title
        tmpName = re.sub(r"Disc_(\d)", "", tmpName)

        # Clean up the disc title so IMDb can identify it easier
        tmpName = tmpName.replace("\"", "").replace("_", " ")

        # Clean up the edges and remove whitespace
        self.movieName = tmpName.strip().replace( " ", "_" )
        


    def setTitle(self, movieName):
        self.movieName = movieName


    def setIndex(self, index):
        self.discIndex = int(index)


    def ripDisc(self, path, output):
        """
            Passes in all of the arguments to makemkvcon to start the ripping
                of the currently inserted DVD or BD

            Inputs:
                path    (Str):  Where the movie will be saved to
                output  (Str):  Temp file to save output to

            Outputs:
                Success (Bool)
        """
        self.path = path

        fullPath = os.path.join( self.path, self.movieName )
        command = [
            self.makemkvcon_path,
            'mkv',
            'disc:%d' % self.discIndex,
            '0',
            fullPath,
            '--cache=%d' % self.cacheSize,
            '--noscan',
            '--minlength=%d' % self.minLength
        ]

        proc = subprocess.Popen(
            command,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE
        )

        if proc.stderr is not None:
            output = proc.stderr.read()
            if len(output) is not 0:
                # TODO: Need pop up for user
                self.log.error("MakeMKV encountered the following error: ")
                self.log.error(output)
                return False

        checks = 0
        output = proc.stdout.read()
        lines = output.split("\n")
        for line in lines:
            if "skipped" in line:
                continue

            badStrings = [
                "failed",
                "Fail",
                "error"
            ]

            if any(x in line.lower() for x in badStrings):
                self.log.error(line)
                return False

            if "Copy complete" in line:
                checks += 1

            if "titles saved" in line:
                checks += 1

        if checks >= 2:
            self._queueMovie()
            return True
        else:
            return False

    def findDisc(self, output):
        """
            Use makemkvcon to list all DVDs or BDs inserted
            If more then one disc is inserted, use the first result

            Inputs:
                output  (Str): Temp file to save output to

            Outputs:
                Success (Bool)
        """
        drives = []
        proc = subprocess.Popen(
            [self.makemkvcon_path, '-r', 'info'],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        output = proc.stderr.read()
        if proc.stderr is not None:
            if len(output) is not 0:
                # TODO: Need pop up for user
                self.log.error("MakeMKV encountered the following error: ")
                self.log.error(output)
                return []

        output = proc.stdout.read()
        if "This application version is too old." in output:
            # TODO: Need pop up for user
            self.log.error("Your MakeMKV version is too old." \
                "Please download the latest version at http://www.makemkv.com" \
                " or enter a registration key to continue using MakeMKV.")

            return []

        # Passed the simple tests, now check for disk drives
        
        lines = output.split("\n")
        for line in lines:
            if line[:4] == "DRV:":
                if ("/dev/" in line) or ("\\\\CdRom" in line):
                    out = line.split(',')

                    if len(str(out[5])) > 3:

                        drives.append(
                            {
                                "discIndex": out[0].replace("DRV:", ""),
                                "discTitle": out[5],
                                "location": out[6]
                            }
                        )

        return drives


    def getDiscInfo(self):
        """
            Returns information about the selected disc

            Inputs:
                None

            Outputs:
                None
        """

        proc = subprocess.Popen(
            [
                self.makemkvcon_path,
                '-r',
                'info',
                'disc:%d' % self.discIndex,
                '--minlength=%d' % self.minLength,
                '--messages=%s/makemkvMessages' % self.temp_path
            ],
            stderr=subprocess.PIPE
        )

        output = proc.stderr.read()
        if proc.stderr is not None:
            if len(output) is not 0:
                # TODO: need pop up for user
                self.log.error("MakeMKV encountered the following error: ")
                self.log.error(output)
                return False

        self.readMKVMessages("TCOUNT")
        for titleNo in set(self.readMKVMessages("TINFO")):
            print titleNo


    def readMKVMessages(self, search, searchIndex = None):
        """
            Returns a list of messages that match the search string

            Inputs:
                search      (Str)
                searchIndex (Str)

            Outputs:
                toReturn    (List)
        """
        toReturn = []
        f = xbmcvfs.File( os.path.join( self.temp_path, "makemkvMessages" ) )
        messages = f.read().splitlines()
        for line in messages:
            
            if line[:len(search)] == search:
                values = line.replace("%s:" % search, "").strip()

                cr = csv.reader([values])

                if searchIndex is not None:
                    for row in cr:
                        if int(row[0]) == int(searchIndex):
                            #print row
                            toReturn.append(row[3])
                else:
                    for row in cr:
                        toReturn.append(row[0])

        return toReturn

    def getTitle(self):
        """
            Returns the current movies title

            Inputs:
                None

            Outputs:
                movieName   (Str)
        """
        self._cleanTitle()
        return self.movieName
