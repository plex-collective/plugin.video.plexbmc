import random
import re
import sys
import urllib
import xbmc  # pylint: disable=F0401
import xbmcgui  # pylint: disable=F0401
import xbmcplugin  # pylint: disable=F0401

from plexbmc import settings, THUMB, CACHE_DATA, printDebug
import plexbmc.cache as cache
import plexbmc
import plexbmc.skins
import plexbmc.servers
import plexbmc.main


def displaySections(filter=None, shared=False):
    printDebug("== ENTER: displaySections() ==", False)
    xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'files')

    ds_servers = plexbmc.servers.PlexServers.discoverAll()
    numOfServers = len(ds_servers)
    printDebug(
        "Using list of " + str(numOfServers) + " servers: " + str(ds_servers))

    for section in plexbmc.servers.Sections.getAllSections(ds_servers):
        if shared and section.get('owned') == '1':
            continue

        details = {'title': section.get('title', 'Unknown')}

        if len(ds_servers) > 1:
            details['title'] = section.get(
                'serverName') + ": " + details['title']

        extraData = {'fanart_image': Media.getFanart(section, section.get('address')),
                     'type': "Video",
                     'thumb': THUMB,
                     'token': section.get('token', None)}

        # Determine what we are going to do process after a link is
        # selected by the user, based on the content we find

        path = section['path']

        if section.get('type') == 'show':
            mode = plexbmc.MODE_TVSHOWS
            if (filter is not None) and (filter != "tvshows"):
                continue

        elif section.get('type') == 'movie':
            mode = plexbmc.MODE_MOVIES
            if (filter is not None) and (filter != "movies"):
                continue

        elif section.get('type') == 'artist':
            mode = plexbmc.MODE_ARTISTS
            if (filter is not None) and (filter != "music"):
                continue

        elif section.get('type') == 'photo':
            mode = plexbmc.MODE_PHOTOS
            if (filter is not None) and (filter != "photos"):
                continue
        else:
            printDebug(
                "Ignoring section " + details['title'] + " of type " + section.get('type') + " as unable to process")
            continue

        if settings('secondary'):
            mode = plexbmc.MODE_GETCONTENT
        else:
            path = path + '/all'

        extraData['mode'] = mode
        s_url = 'http://%s%s' % (section['address'], path)

        if not settings("skipcontextmenus"):
            context = []
            refreshURL = "http://" + section.get('address') + section.get('path') + "/refresh"
            libraryRefresh = "RunScript(plugin.video.plexbmc, update ," + refreshURL + ")"
            context.append(('Refresh library section', libraryRefresh, ))
        else:
            context = None

        # Build that listing..
        GUI.addGUIItem(s_url, details, extraData, context)

    if shared:
        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)
        return

    # For each of the servers we have identified
    allservers = ds_servers
    numOfServers = len(allservers)

    if plexbmc.__settings__.getSetting('myplex_user') != '':
        GUI.addGUIItem('http://myplexqueue', {'title': 'myplex Queue'}, {
                       'thumb': THUMB, 'type': 'Video', 'mode': plexbmc.MODE_MYPLEXQUEUE})

    for server in allservers.itervalues():

        if server['class'] == "secondary":
            continue

        # Plex plugin handling
        if (filter is not None) and (filter != "plugins"):
            continue

        if numOfServers > 1:
            prefix = server['serverName'] + ": "
        else:
            prefix = ""

        details = {'title': prefix + "Channels"}
        extraData = {'type': "Video",
                     'thumb': THUMB,
                     'token': server.get('token', None)}

        extraData['mode'] = plexbmc.MODE_CHANNELVIEW
        u = "http://" + server['server'] + ":" + server['port'] + "/system/plugins/all"
        GUI.addGUIItem(u, details, extraData)

        # Create plexonline link
        details['title'] = prefix + "Plex Online"
        extraData['type'] = "file"
        extraData['thumb'] = THUMB
        extraData['mode'] = plexbmc.MODE_PLEXONLINE

        u = "http://" + server['server'] + ":" + server['port'] + "/system/plexonline"
        GUI.addGUIItem(u, details, extraData)

    if plexbmc.__settings__.getSetting("cache") == "true":
        details = {'title': "Refresh Data"}
        extraData = {}
        extraData['type'] = "file"

        extraData['mode'] = plexbmc.MODE_DELETE_REFRESH

        u = "http://nothing"
        GUI.addGUIItem(u, details, extraData)

    # All XML entries have been parsed and we are ready to allow the user
    # to browse around.  So end the screen listing.
    xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=False)


class OtherModes:
    @staticmethod
    def displayServers(url):
        printDebug("== ENTER: displayServers ==", False)
        url_type = url.split('/')[2]
        printDebug("Displaying entries for " + url_type)
        server_list = plexbmc.servers.PlexServers.discoverAll()
        number_of_servers = len(server_list)

        # For each of the servers we have identified
        for mediaserver in server_list.values():

            if mediaserver['class'] == "secondary":
                continue

            details = {'title': mediaserver.get('serverName', 'Unknown')}

            if mediaserver.get('token', None):
                extraData = {'token': mediaserver.get('token')}
            else:
                extraData = {}

            if url_type == "video":
                extraData['mode'] = plexbmc.MODE_PLEXPLUGINS
                s_url = 'http://%s:%s/video' % (
                    mediaserver.get('server', ''), mediaserver.get('port'))
                if number_of_servers == 1:
                    OtherModes.PlexPlugins(s_url + plexbmc.servers.MyPlexServers.getAuthDetails(extraData, prefix="?"))
                    return

            elif url_type == "online":
                extraData['mode'] = plexbmc.MODE_PLEXONLINE
                s_url = 'http://%s:%s/system/plexonline' % (
                    mediaserver.get('server', ''), mediaserver.get('port'))
                if number_of_servers == 1:
                    OtherModes.plexOnline(s_url + plexbmc.servers.MyPlexServers.getAuthDetails(extraData, prefix="?"))
                    return

            elif url_type == "music":
                extraData['mode'] = plexbmc.MODE_MUSIC
                s_url = 'http://%s:%s/music' % (
                    mediaserver.get('server', ''), mediaserver.get('port'))
                if number_of_servers == 1:
                    GUI.music(
                        s_url + plexbmc.servers.MyPlexServers.getAuthDetails(extraData, prefix="?"))
                    return

            elif url_type == "photo":
                extraData['mode'] = plexbmc.MODE_PHOTOS
                s_url = 'http://%s:%s/photos' % (
                    mediaserver.get('server', ''), mediaserver.get('port'))
                if number_of_servers == 1:
                    GUI.photo(
                        s_url + plexbmc.servers.MyPlexServers.getAuthDetails(extraData, prefix="?"))
                    return

            GUI.addGUIItem(s_url, details, extraData)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def myPlexQueue():
        printDebug("== ENTER: myplexqueue ==", False)

        if plexbmc.__settings__.getSetting('myplex_user') == '':
            xbmc.executebuiltin("XBMC.Notification(myplex not configured,)")
            return

        html = plexbmc.servers.MyPlexServers.getMyPlexURL('/pms/playlists/queue/all')
        tree = plexbmc.etree.fromstring(html)

        OtherModes.PlexPlugins(
            'http://my.plexapp.com/playlists/queue/all', tree)
        return

    @staticmethod
    def channelView(url):
        printDebug("== ENTER: channelView ==", False)
        tree = Utility.getXML(url)
        if tree is None:
            return
        server = Utility.getServerFromURL(url)
        GUI.setWindowHeading(tree)
        for channels in tree.getiterator('Directory'):

            if channels.get('local', '') == "0":
                continue

            # XXX: Unused variable 'arguments'
            arguments = dict(channels.items())

            extraData = {'fanart_image': Media.getFanart(channels, server),
                         'thumb': Media.getThumb(channels, server)}

            details = {'title': channels.get('title', 'Unknown')}

            suffix = channels.get('path').split('/')[1]

            if channels.get('unique', '') == '0':
                details['title'] = details['title'] + " (" + suffix + ")"

            # Alter data sent into getlinkurl, as channels use path rather than
            # key
            p_url = Utility.getLinkURL(url, {'key': channels.get(
                'path', None), 'identifier': channels.get('path', None)}, server)

            if suffix == "photos":
                extraData['mode'] = plexbmc.MODE_PHOTOS
            elif suffix == "video":
                extraData['mode'] = plexbmc.MODE_PLEXPLUGINS
            elif suffix == "music":
                extraData['mode'] = plexbmc.MODE_MUSIC
            else:
                extraData['mode'] = plexbmc.MODE_GETCONTENT

            GUI.addGUIItem(p_url, details, extraData)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def install(url, name):
        printDebug("== ENTER: install ==", False)
        tree = Utility.getXML(url)
        if tree is None:
            return

        operations = {}
        i = 0
        for plums in tree.findall('Directory'):
            operations[i] = plums.get('title')

            # If we find an install option, switch to a yes/no dialog box
            if operations[i].lower() == "install":
                printDebug("Not installed.  Print dialog")
                ret = xbmcgui.Dialog().yesno(
                    "Plex Online", "About to install " + name)

                if ret:
                    printDebug("Installing....")
                    installed = plexbmc.servers.PlexServers.getURL(url + "/install")
                    tree = plexbmc.etree.fromstring(installed)

                    msg = tree.get('message', '(blank)')
                    printDebug(msg)
                    xbmcgui.Dialog().ok("Plex Online", msg)
                return

            i += 1

        # Else continue to a selection dialog box
        ret = xbmcgui.Dialog().select(
            "This plugin is already installed..", operations.values())

        if ret == -1:
            printDebug("No option selected, cancelling")
            return

        printDebug(
            "Option " + str(ret) + " selected.  Operation is " + operations[ret])
        u = url + "/" + operations[ret].lower()

        action = plexbmc.servers.PlexServers.getURL(u)
        tree = plexbmc.etree.fromstring(action)

        msg = tree.get('message')
        printDebug(msg)
        xbmcgui.Dialog().ok("Plex Online", msg)
        xbmc.executebuiltin("Container.Refresh")
        return

    @staticmethod
    def plexOnline(url):
        printDebug("== ENTER: plexOnline ==")

        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'addons')
        server = Utility.getServerFromURL(url)
        tree = Utility.getXML(url)

        if tree is None:
            return

        for plugin in tree:
            details = {
                'title': plugin.get('title', plugin.get('name', 'Unknown')).encode('utf-8')}
            extraData = {'type': "Video",
                         'installed': int(plugin.get('installed', 2)),
                         'key': plugin.get('key', ''),
                         'thumb': Media.getThumb(plugin, server)}

            extraData['mode'] = plexbmc.MODE_CHANNELINSTALL

            if extraData['installed'] == 1:
                details['title'] = details['title'] + " (installed)"

            elif extraData['installed'] == 2:
                extraData['mode'] = plexbmc.MODE_PLEXONLINE

            u = Utility.getLinkURL(url, plugin, server)

            extraData['parameters'] = {'name': details['title']}

            GUI.addGUIItem(u, details, extraData)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def channelSettings(url, settingID):
        '''
        Take the setting XML and parse it to create an updated
        string with the new settings.  For the selected value, create
        a user input screen (text or list) to update the setting.
        @ input: url
        @ return: nothing
        '''
        printDebug("== ENTER: channelSettings ==", False)
        printDebug("Setting preference for ID: %s" % settingID)

        if not settingID:
            printDebug("ID not set")
            return

        tree = Utility.getXML(url)
        if tree is None:
            return

        GUI.setWindowHeading(tree)
        setString = None
        for plugin in tree:

            if plugin.get('id') == settingID:
                printDebug("Found correct id entry for: %s" % settingID)
                id = settingID

                label = plugin.get('label', "Enter value").encode('utf-8')
                option = plugin.get('option').encode('utf-8')
                value = plugin.get('value').encode('utf-8')

                if plugin.get('type') == "text":
                    printDebug("Setting up a text entry screen")
                    kb = xbmc.Keyboard(value, 'heading')
                    kb.setHeading(label)

                    if option == "hidden":
                        kb.setHiddenInput(True)
                    else:
                        kb.setHiddenInput(False)

                    kb.doModal()
                    if (kb.isConfirmed()):
                        value = kb.getText()
                        printDebug("Value input: " + value)
                    else:
                        printDebug("User cancelled dialog")
                        return False

                elif plugin.get('type') == "enum":
                    printDebug("Setting up an enum entry screen")

                    values = plugin.get('values').split('|')

                    settingScreen = xbmcgui.Dialog()
                    value = settingScreen.select(label, values)
                    if value == -1:
                        printDebug("User cancelled dialog")
                        return False
                else:
                    printDebug('Unknown option type: %s' % plugin.get('id'))

            else:
                value = plugin.get('value')
                id = plugin.get('id')

            if setString is None:
                setString = '%s/set?%s=%s' % (url, id, value)
            else:
                setString = '%s&%s=%s' % (setString, id, value)

        printDebug("Settings URL: %s" % setString)
        plexbmc.servers.PlexServers.getURL(setString)
        xbmc.executebuiltin("Container.Refresh")

        return False

    @staticmethod
    def PlexPlugins(url, tree=None):
        '''
        Main function to parse plugin XML from PMS
        Will create dir or item links depending on what the
        main tag is.
        @input: plugin page URL
        @return: nothing, creates XBMC GUI listing
        '''
        printDebug("== ENTER: PlexPlugins ==", False)
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'addons')

        tree = Utility.getXML(url, tree)
        if tree is None:
            return

        myplex_url = False
        server = Utility.getServerFromURL(url)
        if (tree.get('identifier') != "com.plexapp.plugins.myplex") and ("node.plexapp.com" in url):
            myplex_url = True
            printDebug(
                "This is a myplex URL, attempting to locate master server")
            server = plexbmc.servers.PlexServers.getMasterServer()['address']

        for plugin in tree:

            details = {'title': plugin.get('title', 'Unknown').encode('utf-8')}

            if details['title'] == "Unknown":
                details['title'] = plugin.get(
                    'name', "Unknown").encode('utf-8')

            if plugin.get('summary'):
                details['plot'] = plugin.get('summary')

            extraData = {'thumb': Media.getThumb(plugin, server),
                         'fanart_image': Media.getFanart(plugin, server),
                         'identifier': tree.get('identifier', ''),
                         'type': "Video",
                         'key': plugin.get('key', '')}

            if myplex_url:
                extraData['key'] = extraData['key'].replace(
                    'node.plexapp.com:32400', server)

            if extraData['fanart_image'] == "":
                extraData['fanart_image'] = Media.getFanart(tree, server)

            p_url = Utility.getLinkURL(url, extraData, server)

            if plugin.tag == "Directory" or plugin.tag == "Podcast":

                if plugin.get('search') == '1':
                    extraData['mode'] = plexbmc.MODE_CHANNELSEARCH
                    extraData['parameters'] = {
                        'prompt': plugin.get('prompt', "Enter Search Term").encode('utf-8')}
                else:
                    extraData['mode'] = plexbmc.MODE_PLEXPLUGINS

                GUI.addGUIItem(p_url, details, extraData)

            elif plugin.tag == "Video":
                extraData['mode'] = plexbmc.MODE_VIDEOPLUGINPLAY

                for child in plugin:
                    if child.tag == "Media":
                        extraData['parameters'] = {
                            'indirect': child.get('indirect', '0')}

                GUI.addGUIItem(p_url, details, extraData, folder=False)

            elif plugin.tag == "Setting":

                if plugin.get('option') == 'hidden':
                    value = "********"
                elif plugin.get('type') == "text":
                    value = plugin.get('value')
                elif plugin.get('type') == "enum":
                    value = plugin.get('values').split(
                        '|')[int(plugin.get('value', 0))]
                else:
                    value = plugin.get('value')

                details[
                    'title'] = "%s - [%s]" % (plugin.get('label', 'Unknown').encode('utf-8'), value)
                extraData['mode'] = plexbmc.MODE_CHANNELPREFS
                extraData['parameters'] = {'id': plugin.get('id')}
                GUI.addGUIItem(url, details, extraData)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def processDirectory(url, tree=None):
        printDebug("== ENTER: processDirectory ==", False)
        printDebug("Processing secondary menus")
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), "")

        server = Utility.getServerFromURL(url)
        GUI.setWindowHeading(tree)
        for directory in tree:
            details = {
                'title': directory.get('title', 'Unknown').encode('utf-8')}
            extraData = {'thumb': Media.getThumb(tree, server),
                         'fanart_image': Media.getFanart(tree, server)}

            # if extraData['thumb'] == '':
            #    extraData['thumb']=extraData['fanart_image']

            extraData['mode'] = plexbmc.MODE_GETCONTENT
            u = '%s' % (Utility.getLinkURL(url, directory, server))

            GUI.addGUIItem(u, details, extraData)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def channelSearch(url, prompt):
        '''
        When we encounter a search request, branch off to this function to generate the keyboard
        and accept the terms.  This URL is then fed back into the correct function for
        onward processing.
        '''
        printDebug("== ENTER: channelsearch ==", False)

        if prompt:
            prompt = urllib.unquote(prompt)
        else:
            prompt = "Enter Search Term..."

        kb = xbmc.Keyboard('', 'heading')
        kb.setHeading(prompt)
        kb.doModal()
        if (kb.isConfirmed()):
            text = kb.getText()
            printDebug("Search term input: " + text)
            url = url + '&query=' + urllib.quote(text)
            OtherModes.PlexPlugins(url)
        return


class Utility:
    @staticmethod
    def displayContent(acceptable_level, content_level):
        '''
        Takes a content Rating and decides whether it is an allowable
        level, as defined by the content filter
        @input: content rating
        @output: boolean
        '''
        printDebug("Checking rating flag [%s] against [%s]" % (
            content_level, acceptable_level))

        if acceptable_level == "Adults":
            printDebug("OK to display")
            return True

        content_map = {'Kids': 0,
                       'Teens': 1,
                       'Adults': 2}

        rating_map = {'G': 0,       # MPAA Kids
                      'PG': 0,      # MPAA Kids
                      'PG-13': 1,   # MPAA Teens
                      'R': 2,       # MPAA Adults
                      'NC-17': 2,   # MPAA Adults
                      'NR': 2,      # MPAA Adults
                      'Unrated': 2,  # MPAA Adults

                      'U': 0,       # BBFC Kids
                      'PG': 0,      # BBFC Kids
                      '12': 1,      # BBFC Teens
                      '12A': 1,     # BBFC Teens
                      '15': 1,      # BBFC Teens
                      '18': 2,      # BBFC Adults
                      'R18': 2,     # BBFC Adults

                      'E': 0,  # ACB Kids (hopefully)
                      'G': 0,  # ACB Kids
                      'PG': 0,  # ACB Kids
                      'M': 1,  # ACB Teens
                      'MA15+': 2,  # ADC Adults
                      'R18+': 2,  # ACB Adults
                      'X18+': 2,  # ACB Adults

                      'TV-Y': 0,   # US TV - Kids
                      'TV-Y7': 0,   # US TV - Kids
                      'TV-G': 0,   # Us TV - kids
                      'TV-PG': 1,   # US TV - Teens
                      'TV-14': 1,   # US TV - Teens
                      'TV-MA': 2,   # US TV - Adults

                      'G': 0,      # CAN - kids
                      'PG': 0,      # CAN - kids
                      '14A': 1,     # CAN - teens
                      '18A': 2,     # CAN - Adults
                      'R': 2,       # CAN - Adults
                      'A': 2}       # CAN - Adults

        if content_level is None or content_level == "None":
            printDebug("Setting [None] rating as %s" %
                               (plexbmc.__settings__.getSetting('contentNone'), ))
            if content_map[plexbmc.__settings__.getSetting('contentNone')] <= content_map[acceptable_level]:
                printDebug("OK to display")
                return True
        else:
            try:
                if rating_map[content_level] <= content_map[acceptable_level]:
                    printDebug("OK to display")
                    return True
            except:
                print "Unknown rating flag [%s] whilst lookuing for [%s] - will filter for now, but needs to be added" % (content_level, acceptable_level)

        printDebug("NOT OK to display")
        return False

    @staticmethod
    def photoTranscode(server, url, width=1280, height=720):
        return 'http://%s/photo/:/transcode?url=%s&width=%s&height=%s' % (server, urllib.quote_plus(url), width, height)

    @staticmethod
    def getLinkURL(url, pathData, server, season_shelf=False):
        '''
        Investigate the passed URL and determine what is required to
        turn it into a usable URL
        @ input: url, XML data and PM server address
        @ return: Usable http URL
        '''
        printDebug("== ENTER: getLinkURL ==")
        if not season_shelf:
            path = pathData.get('key', '')
            printDebug("Path is " + path)

        else:
            path = pathData.get('parentKey', '') + "/children"
            printDebug("Path is " + path)

        if path == '':
            printDebug("Empty Path")
            return

        # If key starts with http, then return it
        if path[0:4] == "http":
            printDebug("Detected http link")
            return path

        # If key starts with a / then prefix with server address
        elif path[0] == '/':
            printDebug("Detected base path link")
            return 'http://%s%s' % (server, path)

        # If key starts with plex:// then it requires transcoding
        elif path[0:5] == "plex:":
            printDebug("Detected plex link")
            components = path.split('&')
            for i in components:
                if 'prefix=' in i:
                    del components[components.index(i)]
                    break
            if pathData.get('identifier', None):
                components.append('identifier=' + pathData['identifier'])

            path = '&'.join(components)
            return 'plex://' + server + '/' + '/'.join(path.split('/')[3:])

        elif path[0:5] == "rtmp:" or path[0:6] == "rtmpe:":
            printDebug("Detected RTMP link")
            return path

        # Any thing else is assumed to be a relative path and is built on
        # existing url
        else:
            printDebug("Detected relative link")
            return "%s/%s" % (url, path)

        return url

    @staticmethod
    def getServerFromURL(url):
        '''
        Simply split the URL up and get the server portion, sans port
        @ input: url, woth or without protocol
        @ return: the URL server
        '''
        if url[0:4] == "http" or url[0:4] == "plex":
            return url.split('/')[2]
        else:
            return url.split('/')[0]

    @staticmethod
    def processXML(url, tree=None):
        '''
        Main function to parse plugin XML from PMS
        Will create dir or item links depending on what the
        main tag is.
        @input: plugin page URL
        @return: nothing, creates XBMC GUI listing
        '''
        printDebug("== ENTER: processXML ==", False)
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'movies')
        server = Utility.getServerFromURL(url)
        tree = Utility.getXML(url, tree)
        if tree is None:
            return
        GUI.setWindowHeading(tree)
        for plugin in tree:
            details = {'title': plugin.get('title', 'Unknown').encode('utf-8')}

            if details['title'] == "Unknown":
                details['title'] = plugin.get(
                    'name', "Unknown").encode('utf-8')

            extraData = {'thumb': Media.getThumb(plugin, server),
                         'fanart_image': Media.getFanart(plugin, server),
                         'identifier': tree.get('identifier', ''),
                         'type': "Video"}

            if extraData['fanart_image'] == "":
                extraData['fanart_image'] = Media.getFanart(tree, server)

            p_url = Utility.getLinkURL(url, plugin, server)

            if plugin.tag == "Directory" or plugin.tag == "Podcast":
                extraData['mode'] = plexbmc.MODE_PROCESSXML
                GUI.addGUIItem(p_url, details, extraData)

            elif plugin.tag == "Track":
                GUI.trackTag(server, tree, plugin)

            elif tree.get('viewGroup') == "movie":
                GUI.Movies(url, tree)
                return

            elif tree.get('viewGroup') == "episode":
                GUI.TVEpisodes(url, tree)
                return
        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def getXML(url, media=None):
        printDebug("== ENTER: getXML ==", False)
        if media is None:
            tree = plexbmc.servers.PlexServers.getURL(url)

            if tree is False:
                print "PleXBMC -> Server [%s] offline, not responding or no data was receieved" % Utility.getServerFromURL(url)
                return None
            media = plexbmc.etree.fromstring(tree)

        if media.get('message'):
            xbmcgui.Dialog().ok(
                media.get('header', 'Message'), media.get('message', ''))
            return None

        # setWindowHeading(media)
        return media

    @staticmethod
    def remove_html_tags(data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)


class Commands:
    @staticmethod
    def alterAudio(url):
        '''
        Display a list of available audio streams and allow a user to select one.
        The currently selected stream will be annotated with a *
        '''
        printDebug("== ENTER: alterAudio ==", False)

        html = plexbmc.servers.PlexServers.getURL(url)
        tree = plexbmc.etree.fromstring(html)

        audio_list = []
        display_list = []
        for parts in tree.getiterator('Part'):
            part_id = parts.get('id')

            for streams in parts:
                if streams.get('streamType', '') == "2":

                    stream_id = streams.get('id')
                    audio_list.append(stream_id)
                    lang = streams.get('languageCode', "Unknown")

                    printDebug(
                        "Detected Audio stream [%s] [%s] " % (stream_id, lang))

                    if streams.get('channels', 'Unknown') == '6':
                        channels = "5.1"
                    elif streams.get('channels', 'Unknown') == '7':
                        channels = "6.1"
                    elif streams.get('channels', 'Unknown') == '2':
                        channels = "Stereo"
                    else:
                        channels = streams.get('channels', 'Unknown')

                    if streams.get('codec', 'Unknown') == "ac3":
                        codec = "AC3"
                    elif streams.get('codec', 'Unknown') == "dca":
                        codec = "DTS"
                    else:
                        codec = streams.get('codec', 'Unknown')

                    language = "%s (%s %s)" % (
                        streams.get('language', 'Unknown').encode('utf-8'), codec, channels)

                    if streams.get('selected') == '1':
                        language = language + "*"

                    display_list.append(language)
            break

        audioScreen = xbmcgui.Dialog()
        result = audioScreen.select('Select audio', display_list)
        if result == -1:
            return False

        authtoken = plexbmc.servers.MyPlexServers.getAuthTokenFromURL(url)
        audio_select_URL = "http://%s/library/parts/%s?audioStreamID=%s" % (Utility.getServerFromURL(
            url), part_id, audio_list[result]) + plexbmc.servers.MyPlexServers.getAuthDetails({'token': authtoken})
        printDebug("User has selected stream %s" % audio_list[result])
        printDebug("Setting via URL: %s" % audio_select_URL)

        # XXX: Unused variable 'outcome'
        outcome = plexbmc.servers.PlexServers.getURL(audio_select_URL, type="PUT")
        return True

    @staticmethod
    def alterSubs(url):
        '''
        Display a list of available Subtitle streams and allow a user to select one.
        The currently selected stream will be annotated with a *
        '''
        printDebug("== ENTER: alterSubs ==", False)
        html = plexbmc.servers.PlexServers.getURL(url)

        tree = plexbmc.etree.fromstring(html)

        sub_list = ['']
        display_list = ["None"]
        fl_select = False
        for parts in tree.getiterator('Part'):
            part_id = parts.get('id')

            for streams in parts:
                if streams.get('streamType', '') == "3":
                    stream_id = streams.get('id')
                    lang = streams.get(
                        'languageCode', "Unknown").encode('utf-8')
                    printDebug(
                        "Detected Subtitle stream [%s] [%s]" % (stream_id, lang))

                    if streams.get('format', streams.get('codec')) == "idx":
                        printDebug(
                            "Stream: %s - Ignoring idx file for now" % stream_id)
                        continue
                    else:
                        sub_list.append(stream_id)

                        if streams.get('selected', None) == '1':
                            fl_select = True
                            language = streams.get('language', 'Unknown') + "*"
                        else:
                            language = streams.get('language', 'Unknown')

                        display_list.append(language)
            break

        if not fl_select:
            display_list[0] = display_list[0] + "*"

        subScreen = xbmcgui.Dialog()
        result = subScreen.select('Select subtitle', display_list)
        if result == -1:
            return False

        authtoken = plexbmc.servers.MyPlexServers.getAuthTokenFromURL(url)
        sub_select_URL = "http://%s/library/parts/%s?subtitleStreamID=%s" % (Utility.getServerFromURL(
            url), part_id, sub_list[result]) + plexbmc.servers.MyPlexServers.getAuthDetails({'token': authtoken})

        printDebug("User has selected stream %s" % sub_list[result])
        printDebug("Setting via URL: %s" % sub_select_URL)

        # XXX: Unused variable 'outcome'
        outcome = plexbmc.servers.PlexServers.getURL(sub_select_URL, type="PUT")
        printDebug(sub_select_URL)

        return True

    @staticmethod
    def deleteMedia(url):
        printDebug("== ENTER: deleteMedia ==", False)
        printDebug("deleteing media at: " + url)

        return_value = xbmcgui.Dialog().yesno("Confirm file delete?",
                                              "Delete this item? This action will delete media and associated data files.")

        if return_value:
            printDebug("Deleting....")
            # XXX:  Unused variable 'installed'
            installed = plexbmc.servers.PlexServers.getURL(url, type="DELETE")
            xbmc.executebuiltin("Container.Refresh")
        return True

    @staticmethod
    def watched(url):
        printDebug("== ENTER: watched ==", False)

        if url.find("unscrobble") > 0:
            printDebug("Marking as unwatched with: " + url)
        else:
            printDebug("Marking as watched with: " + url)

        # XXX:  Unused variable 'html'
        html = plexbmc.servers.PlexServers.getURL(url)

        xbmc.executebuiltin("Container.Refresh")
        return

    @staticmethod
    def libraryRefresh(url):
        printDebug("== ENTER: libraryRefresh ==", False)

        # XXX:  Unused variable 'html'
        html = plexbmc.servers.PlexServers.getURL(url)

        printDebug("Library refresh requested")
        xbmc.executebuiltin(
            "XBMC.Notification(\"PleXBMC\",Library Refresh started,100)")
        return

    @staticmethod
    def videoPluginPlay(vids, prefix=None, indirect=None):
        '''
        Plays Plugin Videos, which do not require library feedback
        but require further processing
        @input: url of video, plugin identifier
        @return: nothing. End of Script
        '''
        printDebug(
            "== ENTER: videopluginplay with URL + " + vids + " ==", False)

        server = Utility.getServerFromURL(vids)
        if "node.plexapp.com" in server:
            server = plexbmc.servers.PlexServers.getMasterServer()['address']

        # If we find the url lookup service, then we probably have a standard
        # plugin, but possibly with resolution choices
        if '/services/url/lookup' in vids:
            printDebug("URL Lookup service")
            html = plexbmc.servers.PlexServers.getURL(vids, suppress=False)
            if not html:
                return
            tree = plexbmc.etree.fromstring(html)

            mediaCount = 0
            mediaDetails = []
            for media in tree.getiterator('Media'):
                mediaCount += 1
                tempDict = {
                    'videoResolution': media.get('videoResolution', "Unknown")}

                for child in media:
                    tempDict['key'] = child.get('key', '')

                tempDict['identifier'] = tree.get('identifier', '')
                mediaDetails.append(tempDict)
            printDebug(str(mediaDetails))

            # If we have options, create a dialog menu
            result = 0
            if mediaCount > 1:
                printDebug("Select from plugin video sources")
                dialogOptions = [x['videoResolution'] for x in mediaDetails]
                videoResolution = xbmcgui.Dialog()

                result = videoResolution.select(
                    'Select resolution..', dialogOptions)

                if result == -1:
                    return
            Commands.videoPluginPlay(
                Utility.getLinkURL('', mediaDetails[result], server))
            return

        # Check if there is a further level of XML required
        if indirect or '&indirect=1' in vids:
            printDebug("Indirect link")
            html = plexbmc.servers.PlexServers.getURL(vids, suppress=False)
            if not html:
                return
            tree = plexbmc.etree.fromstring(html)

            for bits in tree.getiterator('Part'):
                Commands.videoPluginPlay(Utility.getLinkURL(vids, bits, server))
                break

            return

        # if we have a plex URL, then this is a transcoding URL
        if 'plex://' in vids:
            printDebug("found webkit video, pass to transcoder")
            plexbmc.servers.PlexServers.getTranscodeSettings(True)
            if not (prefix):
                prefix = "system"
            vids = plexbmc.servers.PlexServers.transcode(0, vids, prefix)

            # Workaround for XBMC HLS request limit of 1024 byts
            if len(vids) > 1000:
                printDebug(
                    "XBMC HSL limit detected, will pre-fetch m3u8 playlist")

                playlist = plexbmc.servers.PlexServers.getURL(vids)

                if not playlist or not "#EXTM3U" in playlist:

                    printDebug(
                        "Unable to get valid m3u8 playlist from transcoder")
                    return

                server = Utility.getServerFromURL(vids)
                session = playlist.split()[-1]
                vids = "http://" + server + "/video/:/transcode/segmented/" + session + "?t=1"

        printDebug("URL to Play: " + vids)
        printDebug("Prefix is: " + str(prefix))

        # If this is an Apple movie trailer, add User Agent to allow access
        if 'trailers.apple.com' in vids:
            url = vids + "|User-Agent=QuickTime/7.6.5 (qtver=7.6.5;os=Windows NT 5.1Service Pack 3)"
        elif server in vids:
            url = vids + plexbmc.servers.MyPlexServers.getAuthDetails({'token': plexbmc.main.PleXBMC.getToken()})
        else:
            url = vids

        printDebug("Final URL is : " + url)

        item = xbmcgui.ListItem(path=url)

        # XXX:  Unused variable 'start'
        start = xbmcplugin.setResolvedUrl(plexbmc.main.PleXBMC.getHandle(), True, item)

        if 'transcode' in url:
            try:
                plexbmc.servers.PlexServers.pluginTranscodeMonitor(plexbmc.servers.PlexServers.getSessionID(), server)
            except:
                printDebug("Unable to start transcode monitor")
        else:
            printDebug("Not starting monitor")

        return

    @staticmethod
    def PLAY(url):
        printDebug("== ENTER: PLAY ==", False)

        if url[0:4] == "file":
            printDebug("We are playing a local file")
            # Split out the path from the URL
            playurl = url.split(':', 1)[1]
        elif url[0:4] == "http":
            printDebug("We are playing a stream")
            if '?' in url:
                playurl = url + plexbmc.servers.MyPlexServers.getAuthDetails({'token': plexbmc.main.PleXBMC.getToken()})
            else:
                playurl = url + plexbmc.servers.MyPlexServers.getAuthDetails(
                    {'token': plexbmc.main.PleXBMC.getToken()}, prefix="?")
        else:
            playurl = url

        item = xbmcgui.ListItem(path=playurl)
        return xbmcplugin.setResolvedUrl(plexbmc.main.PleXBMC.getHandle(), True, item)


class Media:
    @staticmethod
    def mediaType(partData, server, dvdplayback=False):
        printDebug("== ENTER: mediaType ==", False)
        stream = partData['key']
        file_ = partData['file']

        if (file_ is None) or (plexbmc.servers.PlexServers.getStreaming() == "1"):
            printDebug("Selecting stream")
            return "http://" + server + stream

        # First determine what sort of 'file' file_ is

        if file_[0:2] == "\\\\":
            printDebug("Looks like a UNC")
            file_type = "UNC"
        elif file_[0:1] == "/" or file_[0:1] == "\\":
            printDebug("looks like a unix file")
            file_type = "nixfile"
        elif file_[1:3] == ":\\" or file_[1:2] == ":/":
            printDebug("looks like a windows file")
            file_type = "winfile"
        else:
            printDebug("uknown file type")
            printDebug(str(file_))
            file_type = "notsure"

        # 0 is auto select.  basically check for local file first, then stream
        # if not found
        if plexbmc.servers.PlexServers.getStreaming() == "0":
            # check if the file can be found locally
            if file_type == "nixfile" or file_type == "winfile":
                try:
                    printDebug("Checking for local file")
                    exists = open(file_, 'r')
                    printDebug("Local file found, will use this")
                    exists.close()
                    return "file:" + file_
                except:
                    pass

            printDebug("No local file")
            if dvdplayback:
                printDebug("Forcing SMB for DVD playback")
                plexbmc.servers.PlexServers.setStreaming("2")
            else:
                return "http://" + server + stream

        # 2 is use SMB
        elif plexbmc.servers.PlexServers.getStreaming() == "2" or plexbmc.servers.PlexServers.getStreaming() == "3":
            if plexbmc.servers.PlexServers.getStreaming() == "2":
                protocol = "smb"
            else:
                protocol = "afp"

            printDebug("Selecting smb/unc")
            if file_type == "UNC":
                filelocation = protocol + ":" + file_.replace("\\", "/")
            else:
                # Might be OSX type, in which case, remove Volumes and replace
                # with server
                server = server.split(':')[0]
                loginstring = ""

                if plexbmc.nas.override:
                    if plexbmc.nas.override_ip:
                        server = plexbmc.nas.override_ip
                        printDebug("Overriding server with: " + server)

                    nasuser = plexbmc.__settings__.getSetting('nasuserid')
                    if not nasuser == "":
                        loginstring = plexbmc.__settings__.getSetting('nasuserid') + ":" + plexbmc.__settings__.getSetting('naspass') + "@"
                        printDebug("Adding AFP/SMB login info for user " + nasuser)

                if file_.find('Volumes') > 0:
                    filelocation = protocol + ":/" + file_.replace("Volumes", loginstring + server)
                else:
                    if file_type == "winfile":
                        filelocation = protocol + "://" + loginstring + server + "/" + file_[3:]
                    else:
                        # else assume its a file local to server available over
                        # smb/samba (now we have linux PMS).  Add server name
                        # to file path.
                        filelocation = protocol + "://" + loginstring + server + file_

            if plexbmc.nas.override and plexbmc.nas.root:
                # Re-root the file path
                printDebug("Altering path " + filelocation + " so root is: " + plexbmc.nas.root)
                if '/' + plexbmc.nas.root + '/' in filelocation:
                    components = filelocation.split('/')
                    index = components.index(plexbmc.nas.root)

                    # XXX: Unused variable 'i'
                    for i in range(3, index):
                        components.pop(3)
                    filelocation = '/'.join(components)
        else:
            printDebug("No option detected, streaming is safest to choose")
            filelocation = "http://" + server + stream

        printDebug("Returning URL: " + filelocation)
        return filelocation

    @staticmethod
    def getMediaData(tag_dict):
        '''
        Extra the media details from the XML
        @input: dict of <media /> tag attributes
        @output: dict of required values
        '''
        printDebug("== ENTER: getMediaData ==", False)

        return {'VideoResolution': tag_dict.get('videoResolution', ''),
                'VideoCodec': tag_dict.get('videoCodec', ''),
                'AudioCodec': tag_dict.get('audioCodec', ''),
                'AudioChannels': tag_dict.get('audioChannels', ''),
                'VideoAspect': tag_dict.get('aspectRatio', ''),
                'xbmc_height': tag_dict.get('height'),
                'xbmc_width': tag_dict.get('width'),
                'xbmc_VideoCodec': tag_dict.get('videoCodec'),
                'xbmc_AudioCodec': tag_dict.get('audioCodec'),
                'xbmc_AudioChannels': tag_dict.get('audioChannels'),
                'xbmc_VideoAspect': tag_dict.get('aspectRatio')}

    @staticmethod
    def getFanart(data, server, width=1280, height=720):
        '''
        Simply take a URL or path and determine how to format for fanart
        @ input: elementTree element, server name
        @ return formatted URL for photo resizing
        '''
        if settings('skipimages'):
            return ''

        fanart = data.get('art', '').encode('utf-8')

        if fanart == '':
            return ''

        elif fanart[0:4] == "http":
            return fanart

        elif fanart[0] == '/':
            if plexbmc.__settings__.getSetting("fullres_fanart") != "false":
                return 'http://%s%s' % (server, fanart)
            else:
                return Utility.photoTranscode(server, 'http://localhost:32400' + fanart, width, height)

        else:
            return ''

    @staticmethod
    def getThumb(data, server, width=720, height=720):
        '''
        Simply take a URL or path and determine how to format for images
        @ input: elementTree element, server name
        @ return formatted URL
        '''
        if settings('skipimages'):
            return ''

        thumbnail = data.get('thumb', '').split('?t')[0].encode('utf-8')

        if thumbnail == '':
            return THUMB

        elif thumbnail[0:4] == "http":
            return thumbnail

        elif thumbnail[0] == '/':
            if plexbmc.__settings__.getSetting("fullres_thumbs") != "false":
                return 'http://' + server + thumbnail

            else:
                return Utility.photoTranscode(server, 'http://localhost:32400' + thumbnail, width, height)

        else:
            return THUMB

    @staticmethod
    def getContent(url):
        '''
        This function takes teh URL, gets the XML and determines what the content is
        This XML is then redirected to the best processing function.
        If a search term is detected, then show keyboard and run search query
        @input: URL of XML page
        @return: nothing, redirects to another function
        '''
        printDebug("== ENTER: getContent ==", False)

        # XXX: Unused variable 'server'
        server = Utility.getServerFromURL(url)
        lastbit = url.split('/')[-1]
        printDebug("URL suffix: " + str(lastbit))

        # Catch search requests, as we need to process input before getting
        # results.
        if lastbit.startswith('search'):
            printDebug("This is a search URL.  Bringing up keyboard")
            kb = xbmc.Keyboard('', 'heading')
            kb.setHeading('Enter search term')
            kb.doModal()
            if (kb.isConfirmed()):
                text = kb.getText()
                printDebug("Search term input: " + text)
                url = url + '&query=' + urllib.quote(text)
            else:
                return

        html = plexbmc.servers.PlexServers.getURL(url, suppress=False, popup=1)

        if html is False:
            return

        tree = plexbmc.etree.fromstring(html)

        GUI.setWindowHeading(tree)

        if lastbit == "folder":
            Utility.processXML(url, tree)
            return

        view_group = tree.get('viewGroup', None)

        if view_group == "movie":
            printDebug("This is movie XML, passing to Movies")
            if not (lastbit.startswith('recently') or lastbit.startswith('newest') or lastbit.startswith('onDeck')):
                xbmcplugin.addSortMethod(plexbmc.main.PleXBMC.getHandle(), xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
            GUI.Movies(url, tree)
        elif view_group == "show":
            printDebug("This is tv show XML")
            GUI.TVShows(url, tree)
        elif view_group == "episode":
            printDebug("This is TV episode XML")
            GUI.TVEpisodes(url, tree)
        elif view_group == 'artist':
            printDebug("This is music XML")
            GUI.artist(url, tree)
        elif view_group == 'album' or view_group == 'albums':
            GUI.albums(url, tree)
        elif view_group == "track":
            printDebug("This is track XML")
            GUI.tracks(url, tree)
        elif view_group == "photo":
            printDebug("This is a photo XML")
            GUI.photo(url, tree)
        else:
            OtherModes.processDirectory(url, tree)

        return


class GUI:
    @staticmethod
    def addGUIItem(url, details, extraData, context=None, folder=True):
        item_title = details.get('title', 'Unknown')

        printDebug("== ENTER: addGUIItem ==", False)
        printDebug("Adding Dir for [%s]" % item_title)
        printDebug("Passed details: " + str(details))
        printDebug("Passed extraData: " + str(extraData))

        if item_title == '':
            return

        if (extraData.get('token', None) is None) and plexbmc.main.PleXBMC.getToken():
            extraData['token'] = plexbmc.main.PleXBMC.getToken()

        aToken = plexbmc.servers.MyPlexServers.getAuthDetails(extraData)
        qToken = plexbmc.servers.MyPlexServers.getAuthDetails(extraData, prefix='?')

        if extraData.get('mode', None) is None:
            mode = "&mode=0"
        else:
            mode = "&mode=%s" % extraData['mode']

        # Create the URL to pass to the item
        if (not folder) and (extraData['type'] == "image"):
            u = url + qToken
        elif url.startswith('http') or url.startswith('file'):
            u = sys.argv[0] + "?url=" + urllib.quote(url) + mode + aToken
        else:
            u = sys.argv[0] + "?url=" + str(url) + mode + aToken

        if extraData.get('parameters'):
            for argument, value in extraData.get('parameters').items():
                u = "%s&%s=%s" % (u, argument, urllib.quote(value))

        printDebug("URL to use for listing: " + u)

        thumb = str(extraData.get('thumb', ''))
        if thumb.startswith('http'):
            if '?' in thumb:
                thumbPath = thumb + aToken
            else:
                thumbPath = thumb + qToken
        else:
            thumbPath = thumb

        liz = xbmcgui.ListItem(item_title, thumbnailImage=thumbPath)

        printDebug("Setting thumbnail as " + thumbPath)

        # Set the properties of the item, such as summary, name, season, etc
        liz.setInfo(type=extraData.get('type', 'Video'), infoLabels=details)

        # Music related tags
        if extraData.get('type', '').lower() == "music":
            liz.setProperty('Artist_Genre', details.get('genre', ''))
            liz.setProperty('Artist_Description', extraData.get('plot', ''))
            liz.setProperty('Album_Description', extraData.get('plot', ''))

        # For all end items
        if (not folder):
            liz.setProperty('IsPlayable', 'true')

            if extraData.get('type', 'video').lower() == "video":
                liz.setProperty('TotalTime', str(extraData.get('duration')))
                liz.setProperty('ResumeTime', str(extraData.get('resume')))

                if not settings('skipflags'):
                    printDebug("Setting VrR as : %s" %
                                       extraData.get('VideoResolution', ''))
                    liz.setProperty(
                        'VideoResolution', extraData.get('VideoResolution', ''))
                    liz.setProperty(
                        'VideoCodec', extraData.get('VideoCodec', ''))
                    liz.setProperty(
                        'AudioCodec', extraData.get('AudioCodec', ''))
                    liz.setProperty(
                        'AudioChannels', extraData.get('AudioChannels', ''))
                    liz.setProperty(
                        'VideoAspect', extraData.get('VideoAspect', ''))

                    video_codec = {}
                    if extraData.get('xbmc_VideoCodec'):
                        video_codec['codec'] = extraData.get('xbmc_VideoCodec')
                    if extraData.get('xbmc_VideoAspect'):
                        video_codec['aspect'] = float(
                            extraData.get('xbmc_VideoAspect'))
                    if extraData.get('xbmc_height'):
                        video_codec['height'] = int(
                            extraData.get('xbmc_height'))
                    if extraData.get('xbmc_width'):
                        video_codec['width'] = int(
                            extraData.get('xbmc_height'))
                    if extraData.get('duration'):
                        video_codec['duration'] = int(
                            extraData.get('duration'))

                    audio_codec = {}
                    if extraData.get('xbmc_AudioCodec'):
                        audio_codec['codec'] = extraData.get('xbmc_AudioCodec')
                    if extraData.get('xbmc_AudioChannels'):
                        audio_codec['channels'] = int(
                            extraData.get('xbmc_AudioChannels'))

                    liz.addStreamInfo('video', video_codec)
                    liz.addStreamInfo('audio', audio_codec)

        try:
            # Then set the number of watched and unwatched, which will be
            # displayed per season
            liz.setProperty('TotalEpisodes', str(extraData['TotalEpisodes']))
            liz.setProperty(
                'WatchedEpisodes', str(extraData['WatchedEpisodes']))
            liz.setProperty(
                'UnWatchedEpisodes', str(extraData['UnWatchedEpisodes']))

            # Hack to show partial flag for TV shows and seasons
            if extraData.get('partialTV') == 1:
                liz.setProperty('TotalTime', '100')
                liz.setProperty('ResumeTime', '50')
        except:
            pass

        # Set the fanart image if it has been enabled
        fanart = str(extraData.get('fanart_image', 'None'))
        if fanart != 'None':
            if '?' in fanart:
                liz.setProperty('fanart_image', fanart + aToken)
            else:
                liz.setProperty('fanart_image', fanart + qToken)
            printDebug(
                "Setting fan art as " + fanart + " with headers: " + aToken)
        else:
            printDebug("Skipping fanart as None found", False)

        if extraData.get('banner'):
            bannerImg = str(extraData.get('banner', ''))
            if bannerImg.startswith('http'):
                if '?' in bannerImg:
                    bannerPath = bannerImg + aToken
                else:
                    bannerPath = bannerImg + qToken
            else:
                bannerPath = bannerImg

            liz.setProperty('banner', bannerPath)
            printDebug("Setting banner as " + bannerPath)

        if extraData.get('season_thumb'):
            seasonImg = str(extraData.get('season_thumb', ''))
            if seasonImg.startswith('http'):
                if '?' in seasonImg:
                    seasonPath = seasonImg + aToken
                else:
                    seasonPath = seasonImg + qToken
            else:
                seasonPath = seasonImg

            liz.setProperty('seasonThumb', seasonPath)
            printDebug("Setting season Thumb as " + seasonPath)

        # if extraData.get('banner'):
        #    liz.setProperty('banner', extraData.get('banner') + aToken)
        #    printDebug("Setting banner as " + extraData.get('banner') + aToken)

        if context is not None:
            printDebug("Building Context Menus")

            if (not folder) and extraData.get('type', 'video').lower() == "video":
                # Play Transcoded
                playTranscode = u + "&transcode=1"
                plugin_url = "XBMC.PlayMedia(" + playTranscode + ")"
                context.insert(0, ('Play Transcoded', plugin_url, ))
                printDebug("Setting transcode options to [%s]" % plugin_url)

            liz.addContextMenuItems(context, settings("contextreplace"))

        return xbmcplugin.addDirectoryItem(handle=plexbmc.main.PleXBMC.getHandle(), url=u, listitem=liz, isFolder=folder)

    @staticmethod
    def setWindowHeading(tree):
        WINDOW = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        try:
            WINDOW.setProperty("heading", tree.get('title1'))
        except:
            WINDOW.clearProperty("heading")
        try:
            WINDOW.setProperty("heading2", tree.get('title2'))
        except:
            WINDOW.clearProperty("heading2")

    @staticmethod
    def Movies(url, tree=None):
        printDebug("== ENTER: Movies() ==", False)
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'movies')

        # get the server name from the URL, which was passed via the on screen
        # listing..
        tree = Utility.getXML(url, tree)
        if tree is None:
            return

        server = Utility.getServerFromURL(url)

        GUI.setWindowHeading(tree)
        randomNumber = str(random.randint(1000000000, 9999999999))
        # Find all the video tags, as they contain the data we need to link to
        # a file.
        MovieTags = tree.findall('Video')

        # XXX: Unused variable 'fullList'
        fullList = []
        for movie in MovieTags:
            GUI.movieTag(url, server, tree, movie, randomNumber)

        printDebug("Skin override is: %s" %
                           plexbmc.__settings__.getSetting('skinoverride'))
        view_id = plexbmc.skins.enforceSkinView('movie')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle())

    @staticmethod
    def buildContextMenu(url, itemData):
        context = []
        server = Utility.getServerFromURL(url)
        refreshURL = url.replace("/all", "/refresh")
        plugin_url = "RunScript(plugin.video.plexbmc, "
        ID = itemData.get('ratingKey', '0')

        # Initiate Library refresh
        libraryRefresh = plugin_url + "update, " + \
            refreshURL.split('?')[0] + plexbmc.servers.MyPlexServers.getAuthDetails(itemData, prefix="?") + ")"
        context.append(('Rescan library section', libraryRefresh, ))

        # Mark media unwatched
        unwatchURL = "http://" + server + "/:/unscrobble?key=" + ID + \
            "&identifier=com.plexapp.plugins.library" + plexbmc.servers.MyPlexServers.getAuthDetails(itemData)
        unwatched = plugin_url + "watch, " + unwatchURL + ")"
        context.append(('Mark as Unwatched', unwatched, ))

        # Mark media watched
        watchURL = "http://" + server + "/:/scrobble?key=" + ID + \
            "&identifier=com.plexapp.plugins.library" + plexbmc.servers.MyPlexServers.getAuthDetails(itemData)
        watched = plugin_url + "watch, " + watchURL + ")"
        context.append(('Mark as Watched', watched, ))

        # Delete media from Library
        deleteURL = "http://" + server + "/library/metadata/" + ID + \
            plexbmc.servers.MyPlexServers.getAuthDetails(itemData, prefix="?")
        removed = plugin_url + "delete, " + deleteURL + ")"
        context.append(('Delete media', removed, ))

        # Display plugin setting menu
        settingDisplay = plugin_url + "setting)"
        context.append(('PleXBMC settings', settingDisplay, ))

        # Reload media section
        listingRefresh = plugin_url + "refresh)"
        context.append(('Reload Section', listingRefresh, ))

        # alter audio
        alterAudioURL = "http://" + server + "/library/metadata/" + ID + \
            plexbmc.servers.MyPlexServers.getAuthDetails(itemData, prefix="?")
        alterAudio = plugin_url + "audio, " + alterAudioURL + ")"
        context.append(('Select Audio', alterAudio, ))

        # alter subs
        alterSubsURL = "http://" + server + "/library/metadata/" + ID + \
            plexbmc.servers.MyPlexServers.getAuthDetails(itemData, prefix="?")
        alterSubs = plugin_url + "subs, " + alterSubsURL + ")"
        context.append(('Select Subtitle', alterSubs, ))

        printDebug("Using context menus " + str(context))
        return context

    @staticmethod
    def TVShows(url, tree=None):
        printDebug("== ENTER: TVShows() ==", False)
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'tvshows')

        # Get the URL and server name.  Get the XML and parse
        tree = Utility.getXML(url, tree)
        if tree is None:
            return

        server = Utility.getServerFromURL(url)
        GUI.setWindowHeading(tree)

        # For each directory tag we find
        ShowTags = tree.findall('Directory')
        for show in ShowTags:
            tempgenre = []
            for child in show:
                if child.tag == "Genre":
                    tempgenre.append(child.get('tag', ''))
            watched = int(show.get('viewedLeafCount', 0))

            # Create the basic data structures to pass up
            details = {'title': show.get('title', 'Unknown').encode('utf-8'),
                       'sorttitle': show.get('titleSort', show.get('title', 'Unknown')).encode('utf-8'),
                       'tvshowname': show.get('title', 'Unknown').encode('utf-8'),
                       'studio': show.get('studio', '').encode('utf-8'),
                       'plot': show.get('summary', '').encode('utf-8'),
                       'season': 0,
                       'episode': int(show.get('leafCount', 0)),
                       'mpaa': show.get('contentRating', ''),
                       'aired': show.get('originallyAvailableAt', ''),
                       'genre': " / ".join(tempgenre)}

            extraData = {'type': 'video',
                         'UnWatchedEpisodes': int(details['episode']) - watched,
                         'WatchedEpisodes': watched,
                         'TotalEpisodes': details['episode'],
                         'thumb': Media.getThumb(show, server),
                         'fanart_image': Media.getFanart(show, server),
                         'token': plexbmc.main.PleXBMC.getToken(),
                         'key': show.get('key', ''),
                         'ratingKey': str(show.get('ratingKey', 0))}

            # banner art
            if show.get('banner', None) is not None:
                extraData['banner'] = 'http://' + server + show.get('banner')
            else:
                extraData['banner'] = THUMB

            # Set up overlays for watched and unwatched episodes
            if extraData['WatchedEpisodes'] == 0:
                details['playcount'] = 0
            elif extraData['UnWatchedEpisodes'] == 0:
                details['playcount'] = 1
            else:
                extraData['partialTV'] = 1

            # Create URL based on whether we are going to flatten the season
            # view
            if settings('flatten') == "2":
                printDebug("Flattening all shows")
                extraData['mode'] = plexbmc.MODE_TVEPISODES
                u = 'http://%s%s' % (server,
                                     extraData['key'].replace("children", "allLeaves"))
            else:
                extraData['mode'] = plexbmc.MODE_TVSEASONS
                u = 'http://%s%s' % (server, extraData['key'])

            if not settings("skipcontextmenus"):
                context = GUI.buildContextMenu(url, extraData)
            else:
                context = None

            GUI.addGUIItem(u, details, extraData, context)

        printDebug("Skin override is: %s" %
                           plexbmc.__settings__.getSetting('skinoverride'))
        view_id = plexbmc.skins.enforceSkinView('tv')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def TVSeasons(url):
        printDebug("== ENTER: season() ==", False)
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'seasons')

        # Get URL, XML and parse
        server = Utility.getServerFromURL(url)
        tree = Utility.getXML(url)
        if tree is None:
            return

        willFlatten = False
        if settings('flatten') == "1":
            # check for a single season
            if int(tree.get('size', 0)) == 1:
                printDebug("Flattening single season show")
                willFlatten = True

        sectionart = Media.getFanart(tree, server)
        banner = tree.get('banner')
        GUI.setWindowHeading(tree)
        # For all the directory tags
        SeasonTags = tree.findall('Directory')
        for season in SeasonTags:
            if willFlatten:
                url = 'http://' + server + season.get('key')
                GUI.TVEpisodes(url)
                return
            watched = int(season.get('viewedLeafCount', 0))

            # Create the basic data structures to pass up
            details = {'title': season.get('title', 'Unknown').encode('utf-8'),
                       'tvshowname': season.get('title', 'Unknown').encode('utf-8'),
                       'sorttitle': season.get('titleSort', season.get('title', 'Unknown')).encode('utf-8'),
                       'studio': season.get('studio', '').encode('utf-8'),
                       'plot': season.get('summary', '').encode('utf-8'),
                       'season': 0,
                       'episode': int(season.get('leafCount', 0)),
                       'mpaa': season.get('contentRating', ''),
                       'aired': season.get('originallyAvailableAt', '')}

            if season.get('sorttitle'):
                details['sorttitle'] = season.get('sorttitle')

            extraData = {'type': 'video',
                         'WatchedEpisodes': watched,
                         'UnWatchedEpisodes': details['episode'] - watched,
                         'thumb': Media.getThumb(season, server),
                         'fanart_image': Media.getFanart(season, server),
                         'token': plexbmc.main.PleXBMC.getToken(),
                         'key': season.get('key', ''),
                         'ratingKey': str(season.get('ratingKey', 0)),
                         'mode': plexbmc.MODE_TVEPISODES}

            if banner:
                extraData['banner'] = "http://" + server + banner

            if extraData['fanart_image'] == "":
                extraData['fanart_image'] = sectionart

            # Set up overlays for watched and unwatched episodes
            if extraData['WatchedEpisodes'] == 0:
                details['playcount'] = 0
            elif extraData['UnWatchedEpisodes'] == 0:
                details['playcount'] = 1
            else:
                extraData['partialTV'] = 1

            url = 'http://%s%s' % (server, extraData['key'])

            if not settings("skipcontextmenus"):
                context = GUI.buildContextMenu(url, season)
            else:
                context = None

            # Build the screen directory listing
            GUI.addGUIItem(url, details, extraData, context)

        printDebug("Skin override is: %s" %
                           plexbmc.__settings__.getSetting('skinoverride'))
        view_id = plexbmc.skins.enforceSkinView('season')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def TVEpisodes(url, tree=None):
        printDebug("== ENTER: TVEpisodes() ==", False)
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'episodes')

        tree = Utility.getXML(url, tree)
        if tree is None:
            return

        GUI.setWindowHeading(tree)

        # get banner thumb
        banner = tree.get('banner')

        # get season thumb for SEASON NODE
        season_thumb = tree.get('thumb', '')

        ShowTags = tree.findall('Video')
        server = Utility.getServerFromURL(url)

        if not settings('skipimages'):
            sectionart = Media.getFanart(tree, server)

        randomNumber = str(random.randint(1000000000, 9999999999))

        for episode in ShowTags:
            printDebug("---New Item---")
            tempgenre = []
            tempcast = []
            tempdir = []
            tempwriter = []
            for child in episode:
                if child.tag == "Media":
                    mediaarguments = dict(child.items())
                elif child.tag == "Genre" and not settings('skipmetadata'):
                    tempgenre.append(child.get('tag'))
                elif child.tag == "Writer" and not settings('skipmetadata'):
                    tempwriter.append(child.get('tag'))
                elif child.tag == "Director" and not settings('skipmetadata'):
                    tempdir.append(child.get('tag'))
                elif child.tag == "Role" and not settings('skipmetadata'):
                    tempcast.append(child.get('tag'))
            printDebug("Media attributes are " + str(mediaarguments))

            # Gather some data
            view_offset = episode.get('viewOffset', 0)
            duration = int(
                mediaarguments.get('duration', episode.get('duration', 0))) / 1000

            # Required listItem entries for XBMC
            details = {'plot': episode.get('summary', '').encode('utf-8'),
                       'title': episode.get('title', 'Unknown').encode('utf-8'),
                       'sorttitle': episode.get('titleSort', episode.get('title', 'Unknown')).encode('utf-8'),
                       'rating': float(episode.get('rating', 0)),
                       'studio': episode.get('studio', tree.get('studio', '')).encode('utf-8'),
                       'mpaa': episode.get('contentRating', tree.get('grandparentContentRating', '')),
                       'year': int(episode.get('year', 0)),
                       'tagline': episode.get('tagline', '').encode('utf-8'),
                       'episode': int(episode.get('index', 0)),
                       'aired': episode.get('originallyAvailableAt', ''),
                       'tvshowtitle': episode.get('grandparentTitle', tree.get('grandparentTitle', '')).encode('utf-8'),
                       'season': int(episode.get('parentIndex', tree.get('parentIndex', 0)))}

            if episode.get('sorttitle'):
                details['sorttitle'] = episode.get('sorttitle').encode('utf-8')

            if tree.get('mixedParents', '0') == '1':
                details['title'] = "%s - %sx%s %s" % (details['tvshowtitle'], details[
                                                      'season'], str(details['episode']).zfill(2), details['title'])
            else:
                details['title'] = str(details['episode']).zfill(
                    2) + ". " + details['title']

            # Extra data required to manage other properties
            extraData = {'type': "Video",
                         'thumb': Media.getThumb(episode, server),
                         'fanart_image': Media.getFanart(episode, server),
                         'token': plexbmc.main.PleXBMC.getToken(),
                         'key': episode.get('key', ''),
                         'ratingKey': str(episode.get('ratingKey', 0)),
                         'duration': duration,
                         'resume': int(int(view_offset) / 1000)}

            if extraData['fanart_image'] == "" and not settings('skipimages'):
                extraData['fanart_image'] = sectionart

            if season_thumb:
                extraData['season_thumb'] = "http://" + server + season_thumb

            # get ALL SEASONS thumb
            if not season_thumb and episode.get('parentThumb', ""):
                extraData['season_thumb'] = "http://" + server + episode.get('parentThumb', "")

            if banner:
                extraData['banner'] = "http://" + server + banner

            # Determine what tupe of watched flag [overlay] to use
            if int(episode.get('viewCount', 0)) > 0:
                details['playcount'] = 1
            else:
                details['playcount'] = 0

            # Extended Metadata
            if not settings('skipmetadata'):
                details['cast'] = tempcast
                details['director'] = " / ".join(tempdir)
                details['writer'] = " / ".join(tempwriter)
                details['genre'] = " / ".join(tempgenre)

            # Add extra media flag data
            if not settings('skipflags'):
                extraData.update(Media.getMediaData(mediaarguments))

            # Build any specific context menu entries
            if not settings("skipcontextmenus"):
                context = GUI.buildContextMenu(url, extraData)
            else:
                context = None

            extraData['mode'] = plexbmc.MODE_PLAYLIBRARY
            # http:// <server> <path> &mode=<mode> &t=<rnd>
            separator = "?"
            if "?" in extraData['key']:
                separator = "&"
            u = "http://%s%s%st=%s" % (server,
                                       extraData['key'], separator, randomNumber)

            GUI.addGUIItem(u, details, extraData, context, folder=False)

        printDebug("Skin override is: %s" %
                           plexbmc.__settings__.getSetting('skinoverride'))
        view_id = plexbmc.skins.enforceSkinView('episode')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def artist(url, tree=None):
        '''
        Process artist XML and display data
        @input: url of XML page, or existing tree of XML page
        @return: nothing
        '''
        printDebug("== ENTER: artist ==", False)
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'artists')

        # Get the URL and server name.  Get the XML and parse
        tree = Utility.getXML(url, tree)
        if tree is None:
            return

        server = Utility.getServerFromURL(url)
        GUI.setWindowHeading(tree)
        ArtistTag = tree.findall('Directory')
        for artist in ArtistTag:

            details = {'artist': artist.get('title', '').encode('utf-8')}

            details['title'] = details['artist']

            extraData = {'type': "Music",
                         'thumb': Media.getThumb(artist, server),
                         'fanart_image': Media.getFanart(artist, server),
                         'ratingKey': artist.get('title', ''),
                         'key': artist.get('key', ''),
                         'mode': plexbmc.MODE_ALBUMS,
                         'plot': artist.get('summary', '')}

            url = 'http://%s%s' % (server, extraData['key'])
            GUI.addGUIItem(url, details, extraData)

        printDebug("Skin override is: %s" %
                           plexbmc.__settings__.getSetting('skinoverride'))
        view_id = plexbmc.skins.enforceSkinView('music')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def albums(url, tree=None):
        printDebug("== ENTER: albums ==", False)
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'albums')

        # Get the URL and server name.  Get the XML and parse
        tree = Utility.getXML(url, tree)
        if tree is None:
            return

        server = Utility.getServerFromURL(url)
        sectionart = Media.getFanart(tree, server)
        GUI.setWindowHeading(tree)
        AlbumTags = tree.findall('Directory')
        for album in AlbumTags:

            details = {'album': album.get('title', '').encode('utf-8'),
                       'year': int(album.get('year', 0)),
                       'artist': tree.get('parentTitle', album.get('parentTitle', '')).encode('utf-8')}

            details['title'] = details['album']

            extraData = {'type': "Music",
                         'thumb': Media.getThumb(album, server),
                         'fanart_image': Media.getFanart(album, server),
                         'key': album.get('key', ''),
                         'mode': plexbmc.MODE_TRACKS,
                         'plot': album.get('summary', '')}

            if extraData['fanart_image'] == "":
                extraData['fanart_image'] = sectionart

            url = 'http://%s%s' % (server, extraData['key'])

            GUI.addGUIItem(url, details, extraData)

        printDebug("Skin override is: %s" %
                           plexbmc.__settings__.getSetting('skinoverride'))
        view_id = plexbmc.skins.enforceSkinView('music')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def tracks(url, tree=None):
        printDebug("== ENTER: tracks ==", False)
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'songs')

        tree = Utility.getXML(url, tree)
        if tree is None:
            return

        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        playlist.clear()

        server = Utility.getServerFromURL(url)

        # XXX: Unused variable 'sectionart'
        sectionart = Media.getFanart(tree, server)

        GUI.setWindowHeading(tree)
        TrackTags = tree.findall('Track')
        for track in TrackTags:

            GUI.trackTag(server, tree, track)

        printDebug("Skin override is: %s" %
                           plexbmc.__settings__.getSetting('skinoverride'))
        view_id = plexbmc.skins.enforceSkinView('music')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def trackTag(server, tree, track, listing=True):
        printDebug("== ENTER: trackTAG ==", False)
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'songs')

        for child in track:
            for babies in child:
                if babies.tag == "Part":
                    partDetails = (dict(babies.items()))
        printDebug("Part is " + str(partDetails))

        details = {'TrackNumber': int(track.get('index', 0)),
                   'title': str(track.get('index', 0)).zfill(2) + ". " + track.get('title', 'Unknown').encode('utf-8'),
                   'rating': float(track.get('rating', 0)),
                   'album': track.get('parentTitle', tree.get('parentTitle', '')).encode('utf-8'),
                   'artist': track.get('grandparentTitle', tree.get('grandparentTitle', '')).encode('utf-8'),
                   'duration': int(track.get('duration', 0)) / 1000}

        extraData = {'type': "Music",
                     'fanart_image': Media.getFanart(track, server),
                     'thumb': Media.getThumb(track, server),
                     'ratingKey': track.get('key', '')}

        if '/resources/plex.png' in extraData['thumb']:
            printDebug("thumb is default")
            extraData['thumb'] = Media.getThumb(tree, server)

        if extraData['fanart_image'] == "":
            extraData['fanart_image'] = Media.getFanart(tree, server)

        # If we are streaming, then get the virtual location
        url = Media.mediaType(partDetails, server)

        extraData['mode'] = plexbmc.MODE_BASICPLAY
        u = "%s" % (url)

        if listing:
            GUI.addGUIItem(u, details, extraData, folder=False)
        else:
            return (url, details)

    @staticmethod
    def photo(url, tree=None):
        printDebug("== ENTER: photos ==", False)
        server = url.split('/')[2]

        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'photo')

        tree = Utility.getXML(url, tree)
        if tree is None:
            return

        sectionArt = Media.getFanart(tree, server)
        GUI.setWindowHeading(tree)
        for picture in tree:
            details = {
                'title': picture.get('title', picture.get('name', 'Unknown')).encode('utf-8')}

            if not details['title']:
                details['title'] = "Unknown"

            extraData = {'thumb': Media.getThumb(picture, server),
                         'fanart_image': Media.getFanart(picture, server),
                         'type': "image"}

            if extraData['fanart_image'] == "":
                extraData['fanart_image'] = sectionArt

            u = Utility.getLinkURL(url, picture, server)

            if picture.tag == "Directory":
                extraData['mode'] = plexbmc.MODE_PHOTOS
                GUI.addGUIItem(u, details, extraData)

            elif picture.tag == "Photo":
                if tree.get('viewGroup', '') == "photo":
                    for photo in picture:
                        if photo.tag == "Media":
                            for images in photo:
                                if images.tag == "Part":
                                    extraData['key'] = "http://" + server + images.get('key', '')
                                    details['size'] = int(
                                        images.get('size', 0))
                                    u = extraData['key']

                GUI.addGUIItem(u, details, extraData, folder=False)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    @staticmethod
    def music(url, tree=None):
        printDebug("== ENTER: music ==", False)
        xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'artists')

        server = Utility.getServerFromURL(url)

        tree = Utility.getXML(url, tree)
        if tree is None:
            return

        GUI.setWindowHeading(tree)
        for grapes in tree:
            if grapes.get('key', None) is None:
                continue

            details = {'genre': grapes.get('genre', '').encode('utf-8'),
                       'artist': grapes.get('artist', '').encode('utf-8'),
                       'year': int(grapes.get('year', 0)),
                       'album': grapes.get('album', '').encode('utf-8'),
                       'tracknumber': int(grapes.get('index', 0)),
                       'title': "Unknown"}

            extraData = {'type': "Music",
                         'thumb': Media.getThumb(grapes, server),
                         'fanart_image': Media.getFanart(grapes, server)}

            if extraData['fanart_image'] == "":
                extraData['fanart_image'] = Media.getFanart(tree, server)

            u = Utility.getLinkURL(url, grapes, server)

            if grapes.tag == "Track":
                printDebug("Track Tag")
                xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'songs')

                details['title'] = grapes.get(
                    'track', grapes.get('title', 'Unknown')).encode('utf-8')
                details['duration'] = int(
                    int(grapes.get('totalTime', 0)) / 1000)

                extraData['mode'] = plexbmc.MODE_BASICPLAY
                GUI.addGUIItem(u, details, extraData, folder=False)
            else:
                if grapes.tag == "Artist":
                    printDebug("Artist Tag")
                    xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'artists')
                    details['title'] = grapes.get(
                        'artist', 'Unknown').encode('utf-8')
                elif grapes.tag == "Album":
                    printDebug("Album Tag")
                    xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'albums')
                    details['title'] = grapes.get(
                        'album', 'Unknown').encode('utf-8')
                elif grapes.tag == "Genre":
                    details['title'] = grapes.get(
                        'genre', 'Unknown').encode('utf-8')
                else:
                    printDebug("Generic Tag: " + grapes.tag)
                    details['title'] = grapes.get(
                        'title', 'Unknown').encode('utf-8')

                extraData['mode'] = plexbmc.MODE_MUSIC
                GUI.addGUIItem(u, details, extraData)

        printDebug("Skin override is: %s" %
                           plexbmc.__settings__.getSetting('skinoverride'))
        view_id = plexbmc.skins.enforceSkinView('music')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(plexbmc.main.PleXBMC.getHandle(), cacheToDisc=True)

    # XXX: Unused variable 'tree'
    @staticmethod
    def movieTag(url, server, tree, movie, randomNumber):
        printDebug("---New Item---")
        tempgenre = []
        tempcast = []
        tempdir = []
        tempwriter = []

        # Lets grab all the info we can quickly through either a dictionary, or assignment to a list
        # We'll process it later
        for child in movie:
            if child.tag == "Media":
                mediaarguments = dict(child.items())
            elif child.tag == "Genre" and not settings('skipmetadata'):
                tempgenre.append(child.get('tag'))
            elif child.tag == "Writer" and not settings('skipmetadata'):
                tempwriter.append(child.get('tag'))
            elif child.tag == "Director" and not settings('skipmetadata'):
                tempdir.append(child.get('tag'))
            elif child.tag == "Role" and not settings('skipmetadata'):
                tempcast.append(child.get('tag'))

        printDebug("Media attributes are " + str(mediaarguments))

        # Gather some data
        view_offset = movie.get('viewOffset', 0)
        duration = int(
            mediaarguments.get('duration', movie.get('duration', 0))) / 1000

        # Required listItem entries for XBMC
        details = {'plot': movie.get('summary', '').encode('utf-8'),
                   'title': movie.get('title', 'Unknown').encode('utf-8'),
                   'sorttitle': movie.get('titleSort', movie.get('title', 'Unknown')).encode('utf-8'),
                   'rating': float(movie.get('rating', 0)),
                   'studio': movie.get('studio', '').encode('utf-8'),
                   'mpaa': movie.get('contentRating', '').encode('utf-8'),
                   'year': int(movie.get('year', 0)),
                   'tagline': movie.get('tagline', '')}

        # Extra data required to manage other properties
        extraData = {'type': "Video",
                     'thumb': Media.getThumb(movie, server),
                     'fanart_image': Media.getFanart(movie, server),
                     'token': plexbmc.main.PleXBMC.getToken(),
                     'key': movie.get('key', ''),
                     'ratingKey': str(movie.get('ratingKey', 0)),
                     'duration': duration,
                     'resume': int(int(view_offset) / 1000)}

        # Determine what tupe of watched flag [overlay] to use
        if int(movie.get('viewCount', 0)) > 0:
            details['playcount'] = 1
        elif int(movie.get('viewCount', 0)) == 0:
            details['playcount'] = 0

        # Extended Metadata
        if not settings('skipmetadata'):
            details['cast'] = tempcast
            details['director'] = " / ".join(tempdir)
            details['writer'] = " / ".join(tempwriter)
            details['genre'] = " / ".join(tempgenre)

        # Add extra media flag data
        if not settings('skipflags'):
            extraData.update(Media.getMediaData(mediaarguments))

        # Build any specific context menu entries
        if not settings("skipcontextmenus"):
            context = GUI.buildContextMenu(url, extraData)
        else:
            context = None
        # http:// <server> <path> &mode=<mode> &t=<rnd>
        extraData['mode'] = plexbmc.MODE_PLAYLIBRARY
        separator = "?"
        if "?" in extraData['key']:
            separator = "&"
        u = "http://%s%s%st=%s" % (server,
                                   extraData['key'], separator, randomNumber)

        GUI.addGUIItem(u, details, extraData, context, folder=False)
        return



