import os, sys, traceback
import xbmc, xbmcaddon, xbmcvfs

__addon__                = xbmcaddon.Addon( "service.makemkv.rip" )
__addon_name__           = __addon__.getAddonInfo( 'name' )
__addonID__              = __addon__.getAddonInfo( 'id' )
__addon_author__         = __addon__.getAddonInfo( 'author' )
__addon_version__        = __addon__.getAddonInfo( 'version' )
__addon_data__           = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode('utf-8')
__addon_path__           = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode('utf-8')
__language__             = __addon__.getLocalizedString
from resources.lib import utils, settings, stopwatch, logger
_settings = settings.Settings()
original_settings = _settings.read_settings_xml()
general_settings   = _settings.general_settings

from resources.lib import makemkv, handbrake

class CE_Monitor( xbmc.Monitor ):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        self.original_settings = _settings.read_settings_xml()
        self.enabled = kwargs['enabled']
        self.update_settings = kwargs['update_settings']
        
    def onSettingsChanged( self ):
        try:
            xbmc.sleep( 10000 )
            if not self.original_settings == _settings.read_settings_xml():
                self.new_settings = self.update_settings( self.original_settings )
                self.original_settings = self.new_settings
        except:
            traceback.print_exc()
            
class makeMKV():
    def __init__(self, *args, **kwargs):
        return
        
    def rip(self, discs):        
        log = logger.logger( "Rip", True )

        mkv_save_path = general_settings[ "temp_folder" ]
        mkv_tmp_output = general_settings[ "temp_folder" ]

        mkv_api = makemkv.makeMKV( general_settings )

        log.debug("Ripping started successfully")
        
        log.debug("%d Movie Disc%s found" % ( len(discs), ( "", "s" )[len(discs) > 1] ) )

        if (len(discs) > 0):
            # Best naming convention ever
            for disc in discs:
                mkv_api.setTitle(disc["discTitle"])
                mkv_api.setIndex(disc["discIndex"])

                movie_title = mkv_api.getTitle()

                if not xbmcvfs.exists( os.path.join(mkv_save_path, movie_title) ):
                    xbmcvfs.mkdir( os.path.join(mkv_save_path, movie_title) )

                    mkv_api.getDiscInfo()

                    with stopwatch.stopwatch() as t:
                        status = mkv_api.ripDisc(mkv_save_path, mkv_tmp_output)

                    if status:
                        if general_settings[ "eject_disc_upon_completion" ]:
                            xbmc.executebuiltin( "EjectTray()" )
                            
                        log.info("It took %s minute(s) to complete the ripping of %s" %
                             (t.minutes, movie_title)
                        )

                    else:
                        log.error("MakeMKV did not did not complete successfully")
                        log.error("See log for more details")
                        log.error("Movie title: %s" % movie_title)

                else:
                    log.info("Movie folder %s already exists" % movie_title)

        else:
            log.info("Could not find any Movie Discs in drive list")

    def compress(config):
        """
            Main function for compressing
            Does everything
            Returns nothing
        """
        log = logger.logger("Compress", config['debug'])

        hb = handbrake.handBrake(config['debug'])

        log.debug("Compressing started successfully")
        log.debug("Looking for movies to compress")

        if hb.loadMovie():
            log.info( "Compressing %s" % hb.getMovieTitle())

            with stopwatch.stopwatch() as t:
                convert = hb.convert(
                    args=config['com'],
                    nice=int(config['nice'])
                )

            if convert:
                log.info("Movie was compressed and encoded successfully")

                log.info( ("It took %s minutes to compress %s" %
                        (t.minutes, hb.getMovieTitle()))
                )
            else:
                log.info( "HandBrake did not complete successfully")

        else:
            log.info( "Queue does not exist or is empty")
           
def _daemon():
    previous_getDVDState = 4 # this should insure only on rip is done
    while ( not xbmc.abortRequested ):
        xbmc.sleep( 250 )
        if xbmc.getDVDState() == 4 and previous_getDVDState != 4:
            utils.log( "Disc Detected, Checking for Movie Disc(s)", xbmc.LOGNOTICE )
            xbmc.sleep( 3000 )
            previous_getDVDState = xbmc.getDVDState()
            disc = makemkv.makeMKV( general_settings ).findDisc( general_settings[ "temp_folder" ] )
            if disc:
                utils.log( "Movie Disc Detected", xbmc.LOGNOTICE )
                if general_settings[ "movie_disc_insertion" ] == "Rip":
                    makeMKV().rip( disc )
                elif general_settings[ "movie_disc_insertion" ] == "Notify":
                    pass
                elif general_settings[ "movie_disc_insertion" ] == "Stream":
                    pass
                elif general_settings[ "movie_disc_insertion" ] == "Ask":
                    pass
                elif general_settings[ "movie_disc_insertion" ] == "Backup":
                    pass
                else: #do nothing
                    pass
        elif xbmc.getDVDState() !=4:
            previous_getDVDState = xbmc.getDVDState()
            
def update_settings( original_settings ):
    utils.log( "service.py - Settings loaded" )
    new_settings = settings.read_settings_xml()
    if not original_settings == new_settings:
        settings.store_settings()
        original_settings = new_settings
        settings.settings_to_log()
        settings.start()
        general_settings = _settings.general_settings
    return original_settings

if ( __name__ == "__main__" ):
    utils.log( "############################################################", xbmc.LOGNOTICE )
    utils.log( "#  MakeMKV Rip Started                                     #", xbmc.LOGNOTICE )
    utils.log( "#                                                          #", xbmc.LOGNOTICE )
    utils.log( "#     Version: %-43s #" % __addon_version__, xbmc.LOGNOTICE )
    utils.log( "############################################################", xbmc.LOGNOTICE )
    _settings.settings_to_log()
    Monitor = CE_Monitor( enabled = True, update_settings = update_settings )
    _daemon()
    del Monitor