# -*- coding: utf-8 -*- 
import sys, os, traceback, re
import xbmcgui, xbmc, xbmcaddon, xbmcvfs

__script__               = sys.modules[ "__main__" ].__script__
__scriptID__             = sys.modules[ "__main__" ].__scriptID__
__addon_data__           = sys.modules[ "__main__" ].__addon_data__
__addon_path__           = sys.modules[ "__main__" ].__addon_path__
settings_path            = os.path.join( __addon_data__, "settings.xml" )
sys.path.append( os.path.join( __addon_path__, "lib" ) )

import utils

true = True
false = False
null = None

class settings():
    def __init__( self, *args, **kwargs ):
        utils.log( 'settings() - __init__' )
        self.start()
      
    def start( self ):
        utils.log('settings() - start')
        self.setting_values = self.read_settings_xml()
        self.general_settings            = { "movie_disc_insertion": ( "Nothing", "Rip", "Notify" )[ int( __addon__.getSetting( "movie_disc_insertion" ) ) ],
                                      "eject_disc_upon_completion": eval( __addon__.getSetting( "eject_disc_upon_completion" ) ),
                                          "notify_upon_completion": eval( __addon__.getSetting( "notify_upon_completion" ) ),
                                      "override_addon_data_folder": eval( __addon__.getSetting( "override_addon_data_folder" ) ),
                                                     "temp_folder": xbmc.translatePath( __addon__.getSetting( "temp_folder" ) ).decode('utf-8'),
                                        "final_destination_folder": xbmc.translatePath( __addon__.getSetting( "final_destination_folder" ) ).decode('utf-8'),
                                           }

        self.makemkv_settings            = {          "mkv_folder": xbmc.translatePath( __addon__.getSetting( "mkv_folder" ) ).decode('utf-8'),
                                                  "mkv_min_length": int( __addon__.getSetting( "mkv_min_length" ) ),
                                                       "mkv_cache": int( __addon__.getSetting( "mkv_cache" ) ),
                                          "mkv_prompt_on_multiple": eval( __addon__.getSetting( "mkv_prompt_on_multiple" ) ),
                                           }
                                          
        self.handbrake_settings          = {       "use_handbrake": eval( __addon__.getSetting( "use_handbrake" ) ),
                                                "handbrake_folder": xbmc.translatePath( __addon__.getSetting( "handbrake_folder" ).decode('utf-8'),
                                                   "handbrake_cli": __addon__.getSetting( "handbrake_cli" ),
                                           }
                                           
        self.filebot_settings            = {         "use_filebot": eval( __addon__.getSetting( "use_filebot" ) ),
                                                  "filebot_folder": xbmc.translatePath( __addon__.getSetting( "filebot_folder" ).decode('utf-8'),
                                                     "filebot_cli": __addon__.getSetting( "filebot_cli" ),
                                           }

    def read_settings_xml( self ):
        setting_values = {}
        try:
            utils.log( "Reading settings.xml" )
            settings_file = xbmcvfs.File( settings_path ).read()
            settings_list = settings_file.replace("<settings>\n","").replace("</settings>\n","").split("/>\n")
            for setting in settings_list:
                match = re.search('    <setting id="(.*?)" value="(.*?)"', setting)
                if match:
                    setting_values[ match.group( 1 ) ] =  match.group( 2 ) 
                else:
                    match = re.search("""    <setting id="(.*?)" value='(.*?)'""", setting)
                    if match:
                        setting_values[ match.group( 1 ) ] =  match.group( 2 )
        except:
            traceback.print_exc()
        return setting_values
        
    def settings_to_log( self ):
        try:
            utils.log( "Settings" )
            setting_values = self.read_settings_xml()
            for k, v in sorted( setting_values.items() ):
                utils.log( "%30s: %s" % ( k, str( utils.unescape( v.decode('utf-8', 'ignore') ) ) ) )
        except:
            traceback.print_exc()
            
    def store_settings( self ):
        try:
            utils.log( "Storing Settings" )
            setting_values = self.read_settings_xml()
            for k, v in sorted( setting_values.items() ):
                __addon__.setSetting( id=k, value=v )
        except:
            traceback.print_exc()
        return True
            
        