import os, sys
import xbmc, xbmcaddon, xbmcvfs

__addon__                = xbmcaddon.Addon( "service.makemkv.rip" )
__addon_name__           = __addon__.getAddonInfo( 'name' )
__addonID__              = __addon__.getAddonInfo( 'id' )
__addon_author__         = __addon__.getAddonInfo( 'author' )
__addon_version__        = __addon__.getAddonInfo( 'version' )
__addon_data__           = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode('utf-8')
__addon_path__           = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode('utf-8')
__language__             = __addon__.getLocalizedString
#sys.path.append( os.path.join( __addon_path__, "resources", "lib" ) )
from resources.lib import utils, settings, stopwatch, logger
_settings = settings.Settings()
general_settings   = _settings.general_settings
makemkv_settings   = _settings.makemkv_settings
handbrake_settings = _settings.handbrake_settings
filebot_settings   = _settings.filebot_settings

from resources.lib import makemkv, handbrake

class makeMKV():
    def __init__(self, *args, **kwargs):
        return
        
    def rip(self):        
        log = logger.logger( "Rip", True )

        mkv_save_path = general_settings[ "temp_folder" ]
        mkv_tmp_output = general_settings[ "temp_folder" ]

        mkv_api = makemkv.makeMKV( makemkv_settings )

        log.debug("Ripping started successfully")
        log.debug("Checking for DVDs")

        dvds = mkv_api.findDisc(mkv_tmp_output)

        log.debug("%d DVDs found" % len(dvds))

        if (len(dvds) > 0):
            # Best naming convention ever
            for dvd in dvds:
                mkv_api.setTitle(dvd["discTitle"])
                mkv_api.setIndex(dvd["discIndex"])

                movie_title = mkv_api.getTitle()

                if not xbmcvfs.exists( os.path.join(mkv_save_path, movie_title) ):
                    xbmcvfs.mkdir( os.path.join(mkv_save_path, movie_title) )

                    mkv_api.getDiscInfo()

                    with stopwatch.stopwatch() as t:
                        status = mkv_api.ripDisc(mkv_save_path, mkv_tmp_output)

                    if status:
                        if makemkv_settings[ "eject_disc_upon_completion" ]:
                            #place eject here
                            pass

                        log.info("It took %s minute(s) to complete the ripping of %s" %
                             (t.minutes, movie_title)
                        )

                    else:
                        log.info("MakeMKV did not did not complete successfully")
                        log.info("See log for more details")
                        log.debug("Movie title: %s" % movie_title)

                else:
                    log.info("Movie folder %s already exists" % movie_title)

        else:
            log.info("Could not find any DVDs in drive list")

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
    while ( not xbmc.abortRequested ):
        xbmc.sleep( 250 )
        if xbmc.getDVDState() == 4:
            utils.log( "Disc Detected, Checking", xbmc.LOGNOTICE )
            disc = makemkv.makeMKV( makemkv_settings ).findDisc( general_settings[ "temp_folder" ] )
            
            if disc:
                utils.log( "Movie Disc Detected", xbmc.LOGNOTICE )
                makeMKV().rip()

if ( __name__ == "__main__" ):
    utils.log( "############################################################", xbmc.LOGNOTICE )
    utils.log( "#  MakeMKV Rip Started                                     #", xbmc.LOGNOTICE )
    utils.log( "#                                                          #", xbmc.LOGNOTICE )
    utils.log( "#     Version: %-41s #" % __addon_version__, xbmc.LOGNOTICE )
    utils.log( "############################################################", xbmc.LOGNOTICE )
    _settings.settings_to_log()
    _daemon()