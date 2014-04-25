import os, sys
from classes import handbrake, logger, makemkv, stopwatch

class makeMKV(object):
    def __init__(self, name, debug):
        return

    def load_settings(self):
        return
        
    def rip(self):        
        log = logger.logger("Rip", config['debug'])

        mkv_save_path = config['savePath']
        mkv_tmp_output = config['temp']

        mkv_api = makemkv.makeMKV(config)

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

                if not os.path.exists('%s/%s' % (mkv_save_path, movie_title)):
                    os.makedirs('%s/%s' % (mkv_save_path, movie_title))

                    mkv_api.getDiscInfo()

                    with stopwatch.stopwatch() as t:
                        status = mkv_api.ripDisc(mkv_save_path, mkv_tmp_output)

                    if status:
                        if config['eject']:
                            eject(dvd['location'])

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