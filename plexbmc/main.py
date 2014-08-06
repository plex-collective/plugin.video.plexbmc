from urlparse import parse_qs, urlparse
import sys
import urllib
import xbmc  # pylint: disable=F0401
import xbmcgui  # pylint: disable=F0401
import xbmcplugin  # pylint: disable=F0401

from plexbmc import DEBUG, printDebug
import plexbmc.cache as cache
import plexbmc
import plexbmc.skins
import plexbmc.skins_amber
import plexbmc.gui
import plexbmc.servers
import plexbmc.utils


def parseQueryString(query, lowercase_key=True, value_list=False):
    '''
    Take the query string or list and parse them to create a dictionary
    of key/value pairs.  Any string that is not a valid query string is
    ignored.
    @ input: (string or list) query - url or parts of url to parse
    @ input: (bool) lowercase_key - convert keys to lowercase
    @ input: (bool) value_list - return values as a list.  If Fasle and
             there are multiple values, only the last value will be included
             in result
    @ return: dictionary of key (lowercase) / [value] parameters
    '''
    printDebug("== ENTER: parseQueryString ==", False)
    printDebug("Query string/list: " + str(query))

    # Make sure parmlist is a list, not a string
    query = query if isinstance(query, list) else [query]

    parameters = {}
    for query_string in query:
        parameters.update(parse_qs(urlparse(query_string.strip()).query, keep_blank_values=True))
    print "PleXBMC -> Detected parameters: " + str(parameters)
    if lowercase_key:
        parameters = dict((k.lower(), v) for k, v in parameters.items())
    if not value_list:
        parameters = dict((k, v[0]) for k, v in parameters.items())
    return parameters

    #try:
        #params = {}
        # for query_string in query:
            # if len(query_string) >= 2:
                # params = query_string

                # if params[0] == "?":
                    # cleanedparams = params[1:]
                # else:
                    # cleanedparams = params

                # if (params[len(params) - 1] == '/'):
                    # params = params[0:len(params) - 2]

                # pairsofparams = cleanedparams.split('&')
                # for i in range(len(pairsofparams)):
                    # splitparams = {}
                    # splitparams = pairsofparams[i].split('=')
                    # if (len(splitparams)) == 2:
                        # param[splitparams[0]] = splitparams[1]
                    # elif (len(splitparams)) == 3:
                        # param[splitparams[0]] = splitparams[
                            # 1] + "=" + splitparams[2]
            # print "PleXBMC -> Detected parameters: " + str(param)
    #except:
    #    printDebug("Parameter parsing failed: " + str(query))
    #return param

import xbmcgui
class MyWinXML(xbmcgui.WindowXML):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, forceFallback):
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        pass

    def onInit(self):
        # Put your List Populating code/ and GUI startup stuff here
        self.close()

    def onAction(self, action):
        # Same as normal python Windows.
        if action == ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """
        pass

    def onFocus(self, controlID):
        pass

import os
def test():
    print 'test start'
    #win = MyWinXML('special://skin/1080i/Static2.xml', os.getcwd())
    #win = MyWinXML('Static2.xml', '/home/jason/src/skin.amber/resources/skins')
    win = MyWinXML('custom12345.xml', '/home/jason/src/skin.amber', 'Default', '720p')
    win.doModal()

    print 'test'

def contentHandler(content, params):
    '''
    Prepares and calls specific content handlers based on paramaters received
    '''
    if 'sections' in content:
        # XXX: append will not work with current implementation of XBMC
        # Don't overwrite contents, append it
        static_xml_text = None
        items = []

        container_id = None if not params.get('append', '').isdigit() else int(params.get('append'))
        static = params.get('static', '')

        if static:
            static_xml_text = plexbmc.utils.readFile(static)

            ids = params.get('ids', None)
            if ids:
                ids = ids.split(',')

            if static_xml_text and ids:
                items = plexbmc.skins.Skin.createStaticListitems(static_xml_text, ids)

        #test()
        plexbmc.skins.Skin.popluateLibrarySections(container_id, items)
    #elif 'recentlyadded' in content:
    #    section = params.get('section', None)
    #    if not section:
    #        return
    #    plexbmc.skins.deckRecentlyAdded(section)
    #    #plexbmc.skins.deck(section)
    #elif 'ondeck' in content:
    #    section = params.get('section', None)
    #    if not section:
    #        return
    #    plexbmc.skins.deckOnDeck(section)
    #    #plexbmc.skins.deck(section)
    elif content in ['ondeck', 'recentlyadded', 'recentlyviewed']:
        section = params.get('section', None)
        if not section:
            return
        plexbmc.skins.deck(section)


class PleXBMC(object):
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
        printDebug("PleXBMC -> Script argument is " + str(sys.argv), False)
        print "PleXBMC -> Script argument is " + str(sys.argv)

        params = parseQueryString(sys.argv)

        # Now try and assign some data to them
        param_url = params.get('url', None)
        if param_url and (param_url.startswith('http') or param_url.startswith('file')):
            param_url = urllib.unquote(param_url)

        param_name = urllib.unquote_plus(params.get('name', ''))
        param_indirect = params.get('indirect', None)
        param_identifier = params.get('identifier', None)
        param_transcodeOverride = int(params.get('transcode', 0))

        # setToken
        self.setToken(params.get('X-Plex-Token', None))

        # plugin handle
        self.setHandle(None if not (len(sys.argv) >= 1 and sys.argv[1].isdigit()) else int(sys.argv[1]))

        # mode
        mode = - 1 if not params.get('mode', '').isdigit() else int(params.get('mode'))

        force = params.get('force', False)
        content = params.get('content', None)

        # Begin process of parsing request
        if content:
            contentHandler(content, params)

        # Populate Skin variables
        elif str(sys.argv[1]) == "skin":
            try:
                skin_type = sys.argv[2]
            except:
                skin_type = None
            plexbmc.skins.skin(skin_type = skin_type)

        elif str(sys.argv[1]) == "amberskin":
            plexbmc.skins_amber.amberskin()

        # Populate recently OR on deck shelf items
        elif str(sys.argv[1]) == "shelf":
            plexbmc.skins.shelf()

        # Populate both recently AND on deck shelf items
        elif str(sys.argv[1]) == "fullshelf":
            plexbmc.skins_amber.fullShelf()

        # Populate channel recently viewed items
        elif str(sys.argv[1]) == "channelShelf":
            plexbmc.skins_amber.shelfChannel()

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
                printDebug(
                    "Currently in home - refreshing to allow new settings to be taken")
                xbmc.executebuiltin("XBMC.ActivateWindow(Home)")

        # not currently used
        elif sys.argv[1] == "refreshplexbmc":
            server_list = plexbmc.servers.PlexServers.discoverAll()
            plexbmc.skins.skin(server_list)
            plexbmc.skins.shelf(server_list)
            plexbmc.skins_amber.shelfChannel(server_list)

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

        # Display audio stream selection screen
        elif sys.argv[1] == "audio":
            url = sys.argv[2]
            plexbmc.gui.Commands.alterAudio(url)

        # Allow a master server to be selected (for myplex queue)
        elif sys.argv[1] == "master":
            plexbmc.servers.PlexServers.setMasterServer()

        # Delete cache and refresh it
        elif str(sys.argv[1]) == "cacherefresh":
            cache.delete()
            xbmc.executebuiltin("ReloadSkin()")

        # XXX  WE be sending non ints for some reason
        # elif not str(sys.argv[1]).isdigit():
        #    pass

        # else move to the main code
        elif self.getHandle():
            WINDOW = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            WINDOW.clearProperty("heading")
            WINDOW.clearProperty("heading2")

            if DEBUG:
                print "PleXBMC -> Mode: " + str(mode)
                print "PleXBMC -> URL: " + str(param_url)
                print "PleXBMC -> Name: " + str(param_name)
                print "PleXBMC -> identifier: " + str(param_identifier)
                print "PleXBMC -> token: " + str(self.getToken())

            # Run a function based on the mode variable that was passed in the URL
            if (mode is None) or (param_url is None) or (len(param_url) < 1):
                plexbmc.gui.displaySections()

            elif mode == plexbmc.MODE_GETCONTENT:
                plexbmc.gui.Media.getContent(param_url)

            elif mode == plexbmc.MODE_TVSHOWS:
                plexbmc.gui.GUI.TVShows(param_url)

            elif mode == plexbmc.MODE_MOVIES:
                xbmcplugin.addSortMethod(
                    self.getHandle(), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
                plexbmc.gui.GUI.Movies(param_url)

            elif mode == plexbmc.MODE_ARTISTS:
                plexbmc.gui.GUI.artist(param_url)

            elif mode == plexbmc.MODE_TVSEASONS:
                plexbmc.gui.GUI.TVSeasons(param_url)

            elif mode == plexbmc.MODE_PLAYLIBRARY:
                plexbmc.servers.Media.playLibraryMedia(
                    param_url, force=force, override=param_transcodeOverride)

            elif mode == plexbmc.MODE_PLAYSHELF:
                plexbmc.servers.Media.playLibraryMedia(param_url, full_data=True, shelf=True)

            elif mode == plexbmc.MODE_TVEPISODES:
                plexbmc.gui.GUI.TVEpisodes(param_url)

            elif mode == plexbmc.MODE_PLEXPLUGINS:
                plexbmc.gui.OtherModes.PlexPlugins(param_url)

            elif mode == plexbmc.MODE_PROCESSXML:
                plexbmc.gui.Utility.processXML(param_url)

            elif mode == plexbmc.MODE_BASICPLAY:
                plexbmc.gui.Commands.PLAY(param_url)

            elif mode == plexbmc.MODE_ALBUMS:
                plexbmc.gui.GUI.albums(param_url)

            elif mode == plexbmc.MODE_TRACKS:
                plexbmc.gui.GUI.tracks(param_url)

            elif mode == plexbmc.MODE_PHOTOS:
                plexbmc.gui.GUI.photo(param_url)

            elif mode == plexbmc.MODE_MUSIC:
                plexbmc.gui.GUI.music(param_url)

            elif mode == plexbmc.MODE_VIDEOPLUGINPLAY:
                plexbmc.gui.Commands.videoPluginPlay(
                    param_url, param_identifier, param_indirect)

            elif mode == plexbmc.MODE_PLEXONLINE:
                plexbmc.gui.OtherModes.plexOnline(param_url)

            elif mode == plexbmc.MODE_CHANNELINSTALL:
                plexbmc.gui.OtherModes.install(param_url, param_name)

            elif mode == plexbmc.MODE_CHANNELVIEW:
                plexbmc.gui.OtherModes.channelView(param_url)

            elif mode == plexbmc.MODE_DISPLAYSERVERS:
                plexbmc.gui.OtherModes.displayServers(param_url)

            elif mode == plexbmc.MODE_PLAYLIBRARY_TRANSCODE:
                plexbmc.servers.Media.playLibraryMedia(param_url, override=True)

            elif mode == plexbmc.MODE_MYPLEXQUEUE:
                plexbmc.gui.OtherModes.myPlexQueue()

            elif mode == plexbmc.MODE_CHANNELSEARCH:
                plexbmc.gui.OtherModes.channelSearch(param_url, params.get('prompt'))

            elif mode == plexbmc.MODE_CHANNELPREFS:
                plexbmc.gui.OtherModes.channelSettings(param_url, params.get('id'))

            elif mode == plexbmc.MODE_SHARED_MOVIES:
                plexbmc.gui.displaySections(filter="movies", shared=True)

            elif mode == plexbmc.MODE_SHARED_SHOWS:
                plexbmc.gui.displaySections(filter="tvshows", shared=True)

            elif mode == plexbmc.MODE_SHARED_PHOTOS:
                plexbmc.gui.displaySections(filter="photos", shared=True)

            elif mode == plexbmc.MODE_SHARED_MUSIC:
                plexbmc.gui.displaySections(filter="music", shared=True)

            elif mode == plexbmc.MODE_SHARED_ALL:
                plexbmc.gui.displaySections(shared=True)

            elif mode == plexbmc.MODE_DELETE_REFRESH:
                cache.delete()
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
