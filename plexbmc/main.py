import sys
import urllib
import xbmc  # pylint: disable=F0401
import xbmcgui  # pylint: disable=F0401
import xbmcplugin  # pylint: disable=F0401

import plexbmc
import plexbmc.skins
import plexbmc.gui
import plexbmc.servers


class PleXBMC(object):
    '''
    '''
    _plugin_handle = None
    _token = None

    def __init__(self):
        print "============================================================================================="
        print "============================================================================================="
        print "============================================================================================="
        print "============================================================================================="
        print "============================================================================================="
        print "============================================================================================="
        print "============================================================================================="
        print "============================================================================================="
        plexbmc.printDebug("PleXBMC -> Script argument is " + str(sys.argv), False)
        print "PleXBMC -> Script argument is " + str(sys.argv)

        params = plexbmc.gui.Utility.get_params(sys.argv)

        # Now try and assign some data to them
        param_url = params.get('url', None)
        if param_url and (param_url.startswith('http') or param_url.startswith('file')):
            param_url = urllib.unquote(param_url)

        param_name = urllib.unquote_plus(params.get('name', ''))
        param_indirect = params.get('indirect', None)
        param_identifier = params.get('identifier', None)
        param_transcodeOverride = int(params.get('transcode', 0))

        # setToken
        token = params.get('X-Plex-Token', None)
        self.setToken(token)
        #self.setToken(params.get('X-Plex-Token', None))

        # plugin handle
        plugin_handle = None if not (len(sys.argv) >= 1 and sys.argv[1].isdigit()) else int(sys.argv[1])
        self.setHandle(plugin_handle)
        #self.setHandle(None if not (len(sys.argv) >= 1 and sys.argv[1].isdigit()) else int(sys.argv[1]))

        mode = - 1 if not params.get('mode', '').isdigit() else int(params.get('mode'))
        force = params.get('force', False)
        content = params.get('content', None)

        print 'self.getHandle(cls): %s' % str(self.getHandle())
        if content:
            # Don't overwrite contents, append it
            container_id = None if not params.get(
                'append', '').isdigit() else int(params.get('append'))

            if 'sections' in content:
                plexbmc.skins.Skin.amberskin(container_id)
            # displaySections()

        # Populate Skin variables
        # if str(sys.argv[1]) == "skin":
        #    try:
        #        type=sys.argv[2]
        #    except:
        #        type=None
        #    skin(type=type)

        # elif str(sys.argv[1]) == "amberskin":
        #    amberskin()

        # Populate recently OR on deck shelf items
        if str(sys.argv[1]) == "shelf":
            plexbmc.skins.Skin.shelf()

        # Populate both recently AND on deck shelf items
        elif str(sys.argv[1]) == "fullshelf":
            plexbmc.skins.Skin.fullShelf()

        # Populate channel recently viewed items
        elif str(sys.argv[1]) == "channelShelf":
            plexbmc.skins.Skin.shelfChannel()

        # Send a library update to Plex
        elif sys.argv[1] == "update":
            url = sys.argv[2]
            plexbmc.gui.Commands.libraryRefresh(url)

        # Mark an item as watched/unwatched in plex
        elif sys.argv[1] == "watch":
            url = sys.argv[2]
            plexbmc.gui.Commands.watched(url)

        # Open the add-on settings page, then refresh plugin
        elif sys.argv[1] == "setting":
            plexbmc.__settings__.openSettings()
            WINDOW = xbmcgui.getCurrentWindowId()
            if WINDOW == 10000:
                plexbmc.printDebug(
                    "Currently in home - refreshing to allow new settings to be taken")
                xbmc.executebuiltin("XBMC.ActivateWindow(Home)")

        # nt currently used
        elif sys.argv[1] == "refreshplexbmc":
            server_list = plexbmc.servers.PlexServers.discoverAll()
            plexbmc.skins.Skin.skin(server_list)
            plexbmc.skins.Skin.shelf(server_list)
            plexbmc.skins.Skin.shelfChannel(server_list)

        # delete media from PMS
        elif sys.argv[1] == "delete":
            url = sys.argv[2]
            plexbmc.gui.Commands.deleteMedia(url)

        # Refresh the current XBMC listing
        elif sys.argv[1] == "refresh":
            xbmc.executebuiltin("Container.Refresh")

        # Display subtitle selection screen
        elif sys.argv[1] == "subs":
            url = sys.argv[2]
            plexbmc.gui.Commands.alterSubs(url)

        # Display audio streanm selection screen
        elif sys.argv[1] == "audio":
            url = sys.argv[2]
            plexbmc.gui.Commands.alterAudio(url)

        # Allow a mastre server to be selected (for myplex queue)
        elif sys.argv[1] == "master":
            plexbmc.servers.PlexServers.setMasterServer()

        # Delete cache and refresh it
        elif str(sys.argv[1]) == "cacherefresh":
            plexbmc.Cache.delete()
            xbmc.executebuiltin("ReloadSkin()")

        # XXX  WE be sending non ints for some reason
        # elif not str(sys.argv[1]).isdigit():
        #    pass

        # else move to the main code
        elif self.getHandle():
           #pluginhandle = int(sys.argv[1])

            WINDOW = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            WINDOW.clearProperty("heading")
            WINDOW.clearProperty("heading2")

            if plexbmc.g_debug == "true":
                print "PleXBMC -> Mode: " + str(mode)
                print "PleXBMC -> URL: " + str(param_url)
                print "PleXBMC -> Name: " + str(param_name)
                print "PleXBMC -> identifier: " + str(param_identifier)
                print "PleXBMC -> token: " + str(self.getToken())

            # Run a function based on the mode variable that was passed in the URL
            if (mode is None) or (param_url is None) or (len(param_url) < 1):
                plexbmc.gui.Sections.displaySections()

            elif mode == plexbmc._MODE_GETCONTENT:
                plexbmc.gui.Media.getContent(param_url)

            elif mode == plexbmc._MODE_TVSHOWS:
                plexbmc.gui.GUI.TVShows(param_url)

            elif mode == plexbmc._MODE_MOVIES:
                xbmcplugin.addSortMethod(
                    self.getHandle(), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
                plexbmc.gui.GUI.Movies(param_url)

            elif mode == plexbmc._MODE_ARTISTS:
                plexbmc.gui.GUI.artist(param_url)

            elif mode == plexbmc._MODE_TVSEASONS:
                plexbmc.gui.GUI.TVSeasons(param_url)

            elif mode == plexbmc._MODE_PLAYLIBRARY:
                plexbmc.servers.Media.playLibraryMedia(
                    param_url, force=force, override=param_transcodeOverride)

            elif mode == plexbmc._MODE_PLAYSHELF:
                plexbmc.servers.Media.playLibraryMedia(param_url, full_data=True, shelf=True)

            elif mode == plexbmc._MODE_TVEPISODES:
                plexbmc.gui.GUI.TVEpisodes(param_url)

            elif mode == plexbmc._MODE_PLEXPLUGINS:
                plexbmc.gui.OtherModes.PlexPlugins(param_url)

            elif mode == plexbmc._MODE_PROCESSXML:
                plexbmc.gui.Utility.processXML(param_url)

            elif mode == plexbmc._MODE_BASICPLAY:
                plexbmc.gui.Commands.PLAY(param_url)

            elif mode == plexbmc._MODE_ALBUMS:
                plexbmc.gui.GUI.albums(param_url)

            elif mode == plexbmc._MODE_TRACKS:
                plexbmc.gui.GUI.tracks(param_url)

            elif mode == plexbmc._MODE_PHOTOS:
                plexbmc.gui.GUI.photo(param_url)

            elif mode == plexbmc._MODE_MUSIC:
                plexbmc.gui.GUI.music(param_url)

            elif mode == plexbmc._MODE_VIDEOPLUGINPLAY:
                plexbmc.gui.Commands.videoPluginPlay(
                    param_url, param_identifier, param_indirect)

            elif mode == plexbmc._MODE_PLEXONLINE:
                plexbmc.gui.OtherModes.plexOnline(param_url)

            elif mode == plexbmc._MODE_CHANNELINSTALL:
                plexbmc.gui.OtherModes.install(param_url, param_name)

            elif mode == plexbmc._MODE_CHANNELVIEW:
                plexbmc.gui.OtherModes.channelView(param_url)

            elif mode == plexbmc._MODE_DISPLAYSERVERS:
                plexbmc.gui.OtherModes.displayServers(param_url)

            elif mode == plexbmc._MODE_PLAYLIBRARY_TRANSCODE:
                plexbmc.servers.Media.playLibraryMedia(param_url, override=True)

            elif mode == plexbmc._MODE_MYPLEXQUEUE:
                plexbmc.gui.OtherModes.myPlexQueue()

            elif mode == plexbmc._MODE_CHANNELSEARCH:
                plexbmc.gui.OtherModes.channelSearch(param_url, params.get('prompt'))

            elif mode == plexbmc._MODE_CHANNELPREFS:
                plexbmc.gui.OtherModes.channelSettings(param_url, params.get('id'))

            elif mode == plexbmc._MODE_SHARED_MOVIES:
                plexbmc.gui.Sections.displaySections(filter="movies", shared=True)

            elif mode == plexbmc._MODE_SHARED_SHOWS:
                plexbmc.gui.Sections.displaySections(filter="tvshows", shared=True)

            elif mode == plexbmc._MODE_SHARED_PHOTOS:
                plexbmc.gui.Sections.displaySections(filter="photos", shared=True)

            elif mode == plexbmc._MODE_SHARED_MUSIC:
                plexbmc.gui.Sections.displaySections(filter="music", shared=True)

            elif mode == plexbmc._MODE_SHARED_ALL:
                plexbmc.gui.Sections.displaySections(shared=True)

            elif mode == plexbmc._MODE_DELETE_REFRESH:
                plexbmc.Cache.delete()
                xbmc.executebuiltin("Container.Refresh")

    @classmethod
    def reset(cls):
        cls._plugin_handle = None

    @classmethod
    def setHandle(cls, value):
        cls._plugin_handle = value
        print 'setHandle: %s' % str(cls._plugin_handle)

    @classmethod
    def getHandle(cls):
        print 'getHandle: %s' % str(cls._plugin_handle)
        return cls._plugin_handle

    @classmethod
    def setToken(cls, value):
        cls._token = value
        print 'SetToken: %s' % str(cls._token)

    @classmethod
    def getToken(cls):
        print 'GetToken: %s' % str(cls._token)
        return cls._token
