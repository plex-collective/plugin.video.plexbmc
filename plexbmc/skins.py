import random
import xbmc  # pylint: disable=F0401
import xbmcgui  # pylint: disable=F0401
import xbmcplugin  # pylint: disable=F0401
import plexbmc


class Skin:
    '''
    '''
    @staticmethod
    def enforceSkinView(mode):
        '''
        Ensure that the views are consistance across plugin usage, depending
        upon view selected by user
        @input: User view selection
        @return: view id for skin
        '''
        plexbmc.printDebug("== ENTER: enforceSkinView ==", False)

        if plexbmc.__settings__.getSetting('skinoverride') == "false":
            return None

        skinname = plexbmc.__settings__.getSetting('skinname')

        current_skin_name = xbmc.getSkinDir()

        skin_map = {'2': 'skin.confluence',
                    '0': 'skin.quartz',
                    '1': 'skin.quartz3',
                    '3': 'skin.amber'}

        if skin_map[skinname] not in current_skin_name:
            plexbmc.printDebug("Do not have the correct skin [%s] selected in settings [%s] - ignoring" % (
                current_skin_name, skin_map[skinname]))
            return None

        if mode == "movie":
            plexbmc.printDebug("Looking for movie skin settings")
            viewname = plexbmc.__settings__.getSetting('mo_view_%s' % skinname)

        elif mode == "tv":
            plexbmc.printDebug("Looking for tv skin settings")
            viewname = plexbmc.__settings__.getSetting('tv_view_%s' % skinname)

        elif mode == "music":
            plexbmc.printDebug("Looking for music skin settings")
            viewname = plexbmc.__settings__.getSetting('mu_view_%s' % skinname)

        elif mode == "episode":
            plexbmc.printDebug("Looking for music skin settings")
            viewname = plexbmc.__settings__.getSetting('ep_view_%s' % skinname)

        elif mode == "season":
            plexbmc.printDebug("Looking for music skin settings")
            viewname = plexbmc.__settings__.getSetting('se_view_%s' % skinname)

        else:
            viewname = "None"

        plexbmc.printDebug("view name is %s" % viewname)

        if viewname == "None":
            return None

        QuartzV3_views = {'List': 50,
                          'Big List': 51,
                          'MediaInfo': 52,
                          'MediaInfo 2': 54,
                          'Big Icons': 501,
                          'Icons': 53,
                          'Panel': 502,
                          'Wide': 55,
                          'Fanart 1': 57,
                          'Fanart 2': 59,
                          'Fanart 3': 500}

        Quartz_views = {'List': 50,
                        'MediaInfo': 51,
                        'MediaInfo 2': 52,
                        'Icons': 53,
                        'Wide': 54,
                        'Big Icons': 55,
                        'Icons 2': 56,
                        'Panel': 57,
                        'Fanart': 58,
                        'Fanart 2': 59}

        Confluence_views = {'List': 50,
                            'Big List': 51,
                            'Thumbnail': 500,
                            'Poster Wrap': 501,
                            'Fanart': 508,
                            'Media Info': 504,
                            'Media Info 2': 503,
                            'Media Info 3': 515,
                            'Wide Icons': 505}

        Amber_views = {'List': 50,
                       'Big List': 52,
                       'Panel': 51,
                       'Low List': 54,
                       'Icons': 53,
                       'Big Panel': 55,
                       'Fanart': 59}

        skin_list = {"0": Quartz_views,
                     "1": QuartzV3_views,
                     "2": Confluence_views,
                     "3": Amber_views}

        plexbmc.printDebug("Using skin view: %s" % skin_list[skinname][viewname])

        try:
            return skin_list[skinname][viewname]
        except:
            print "PleXBMC -> skin name or view name error"
            return None

    @staticmethod
    def skin(server_list=None, type=None):
        # Gather some data and set the window properties
        plexbmc.printDebug("== ENTER: skin() ==", False)
        # Get the global host variable set in settings
        WINDOW = xbmcgui.Window(10000)

        sectionCount = 0
        serverCount = 0

        # XXX: Unused variable 'sharedCount'
        sharedCount = 0
        shared_flag = {}
        hide_shared = plexbmc.__settings__.getSetting('hide_shared')

        if server_list is None:
            server_list = plexbmc.PlexServers.discoverAll()

        # For each of the servers we have identified
        for section in plexbmc.Sections.getAllSections(server_list):
            extraData = {
                'fanart_image': plexbmc.Media.getFanart(
                    section, section['address']), 'thumb': plexbmc.Media.getFanart(
                    section, section['address'], False)}

            # Determine what we are going to do process after a link is
            # selected by the user, based on the content we find
            path = section['path']

            if section['type'] == 'show':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['show'] = True
                    continue
                window = "VideoLibrary"
                mode = plexbmc._MODE_TVSHOWS
            if section['type'] == 'movie':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['movie'] = True
                    continue
                window = "VideoLibrary"
                mode = plexbmc._MODE_MOVIES
            if section['type'] == 'artist':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['artist'] = True
                    continue
                window = "MusicFiles"
                mode = plexbmc._MODE_ARTISTS
            if section['type'] == 'photo':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['photo'] = True
                    continue
                window = "Pictures"
                mode = plexbmc._MODE_PHOTOS

            aToken = plexbmc.MyPlexServers.getAuthDetails(section)
            qToken = plexbmc.MyPlexServers.getAuthDetails(section, prefix='?')

            if plexbmc.g_secondary == "true":
                mode = plexbmc._MODE_GETCONTENT
            else:
                path = path + '/all'

            s_url = 'http://%s%s&mode=%s%s' % (
                section['address'], path, mode, aToken)

            # Build that listing..
            WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), section['title'])
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), section['serverName'])
            WINDOW.setProperty(
                "plexbmc.%d.path" %
                (sectionCount),
                "ActivateWindow(" +
                window +
                ",plugin://plugin.video.plexbmc/?url=" +
                s_url +
                ",return)")
            WINDOW.setProperty("plexbmc.%d.art" % (sectionCount), extraData['fanart_image'] + qToken)
            WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), section['type'])
            WINDOW.setProperty("plexbmc.%d.icon" % (sectionCount), extraData['thumb'] + qToken)
            WINDOW.setProperty("plexbmc.%d.thumb" % (sectionCount), extraData['thumb'] + qToken)
            WINDOW.setProperty(
                "plexbmc.%d.partialpath" %
                (sectionCount),
                "ActivateWindow(" +
                window +
                ",plugin://plugin.video.plexbmc/?url=http://" +
                section['address'] +
                section['path'])
            WINDOW.setProperty(
                "plexbmc.%d.search" %
                (sectionCount),
                "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                (window,
                 section['address'],
                    section['path'],
                    "/search?type=1",
                    mode,
                    aToken))
            WINDOW.setProperty(
                "plexbmc.%d.recent" %
                (sectionCount),
                "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                (window,
                 section['address'],
                    section['path'],
                    "/recentlyAdded",
                    mode,
                    aToken))
            WINDOW.setProperty(
                "plexbmc.%d.all" %
                (sectionCount),
                "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                (window,
                 section['address'],
                    section['path'],
                    "/all",
                    mode,
                    aToken))
            WINDOW.setProperty(
                "plexbmc.%d.viewed" %
                (sectionCount),
                "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                (window,
                 section['address'],
                    section['path'],
                    "/recentlyViewed",
                    mode,
                    aToken))
            WINDOW.setProperty(
                "plexbmc.%d.ondeck" %
                (sectionCount),
                "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                (window,
                 section['address'],
                    section['path'],
                    "/onDeck",
                    mode,
                    aToken))
            WINDOW.setProperty(
                "plexbmc.%d.released" %
                (sectionCount),
                "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                (window,
                 section['address'],
                    section['path'],
                    "/newest",
                    mode,
                    aToken))
            WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "false")

            if section['type'] == "artist":
                WINDOW.setProperty(
                    "plexbmc.%d.album" %
                    (sectionCount),
                    "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                    (window,
                     section['address'],
                        section['path'],
                        "/albums",
                        mode,
                        aToken))
                WINDOW.setProperty(
                    "plexbmc.%d.search" %
                    (sectionCount),
                    "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                    (window,
                     section['address'],
                        section['path'],
                        "/search?type=10",
                        mode,
                        aToken))
            elif section['type'] == "photo":
                WINDOW.setProperty(
                    "plexbmc.%d.year" %
                    (sectionCount),
                    "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                    (window,
                     section['address'],
                        section['path'],
                        "/year",
                        mode,
                        aToken))
            elif section['type'] == "show":
                WINDOW.setProperty(
                    "plexbmc.%d.search" %
                    (sectionCount),
                    "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                    (window,
                     section['address'],
                        section['path'],
                        "/search?type=4",
                        mode,
                        aToken))
            elif section['type'] == "movie":
                WINDOW.setProperty(
                    "plexbmc.%d.search" %
                    (sectionCount),
                    "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                    (window,
                     section['address'],
                        section['path'],
                        "/search?type=1",
                        mode,
                        aToken))

            plexbmc.printDebug("Building window properties index [" + str(sectionCount) + "] which is [" + section['title'] + "]")
            plexbmc.printDebug(
                "PATH in use is: ActivateWindow(" +
                window +
                ",plugin://plugin.video.plexbmc/?url=" +
                s_url +
                ",return)")
            sectionCount += 1

        if type == "nocat":
            WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
            WINDOW.setProperty("plexbmc.%d.path" %
                               (sectionCount), "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode=" +
                               str(plexbmc._MODE_SHARED_ALL) +
                               ",return)")
            WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "movie")
            WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
            sectionCount += 1
        else:
            if shared_flag.get('movie'):
                WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
                WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
                WINDOW.setProperty("plexbmc.%d.path" %
                                   (sectionCount), "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode=" +
                                   str(plexbmc._MODE_SHARED_MOVIES) +
                                   ",return)")
                WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "movie")
                WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
                sectionCount += 1

            if shared_flag.get('show'):
                WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
                WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
                WINDOW.setProperty("plexbmc.%d.path" %
                                   (sectionCount), "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode=" +
                                   str(plexbmc._MODE_SHARED_SHOWS) +
                                   ",return)")
                WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "show")
                WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
                sectionCount += 1

            if shared_flag.get('artist'):
                WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
                WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
                WINDOW.setProperty("plexbmc.%d.path" %
                                   (sectionCount), "ActivateWindow(MusicFiles,plugin://plugin.video.plexbmc/?url=/&mode=" +
                                   str(plexbmc._MODE_SHARED_MUSIC) +
                                   ",return)")
                WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "artist")
                WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
                sectionCount += 1

            if shared_flag.get('photo'):
                WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
                WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
                WINDOW.setProperty("plexbmc.%d.path" %
                                   (sectionCount), "ActivateWindow(Pictures,plugin://plugin.video.plexbmc/?url=/&mode=" +
                                   str(plexbmc._MODE_SHARED_PHOTOS) +
                                   ",return)")
                WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "photo")
                WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
                sectionCount += 1

        # For each of the servers we have identified
        numOfServers = len(server_list)
        for server in server_list.values():
            if server['class'] == "secondary":
                continue

            aToken = plexbmc.MyPlexServers.getAuthDetails(server)
            qToken = plexbmc.MyPlexServers.getAuthDetails(server, prefix='?')

            if plexbmc.g_channelview == "true":
                WINDOW.setProperty("plexbmc.channel", "1")
                WINDOW.setProperty(
                    "plexbmc.%d.server.channel" %
                    (serverCount),
                    "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=http://" +
                    server['server'] +
                    ":" +
                    server['port'] +
                    "/system/plugins/all&mode=21" +
                    aToken +
                    ",return)")
            else:
                WINDOW.clearProperty("plexbmc.channel")
                WINDOW.setProperty(
                    "plexbmc.%d.server.video" %
                    (serverCount),
                    "http://" +
                    server['server'] +
                    ":" +
                    server['port'] +
                    "/video&mode=7" +
                    aToken)
                WINDOW.setProperty(
                    "plexbmc.%d.server.music" %
                    (serverCount),
                    "http://" +
                    server['server'] +
                    ":" +
                    server['port'] +
                    "/music&mode=17" +
                    aToken)
                WINDOW.setProperty(
                    "plexbmc.%d.server.photo" %
                    (serverCount),
                    "http://" +
                    server['server'] +
                    ":" +
                    server['port'] +
                    "/photos&mode=16" +
                    aToken)

            WINDOW.setProperty(
                "plexbmc.%d.server.online" %
                (serverCount),
                "http://" +
                server['server'] +
                ":" +
                server['port'] +
                "/system/plexonline&mode=19" +
                aToken)
            WINDOW.setProperty("plexbmc.%d.server" % (serverCount), server['serverName'])

            plexbmc.printDebug("Name mapping is :" + server['serverName'])

            serverCount += 1

        # Clear out old data
        try:
            plexbmc.printDebug(
                "Clearing properties from [" +
                str(sectionCount) +
                "] to [" +
                WINDOW.getProperty("plexbmc.sectionCount") +
                "]")

            for i in range(sectionCount, int(WINDOW.getProperty("plexbmc.sectionCount")) + 1):
                WINDOW.clearProperty("plexbmc.%d.uuid" % (i))
                WINDOW.clearProperty("plexbmc.%d.title" % (i))
                WINDOW.clearProperty("plexbmc.%d.subtitle" % (i))
                WINDOW.clearProperty("plexbmc.%d.url" % (i))
                WINDOW.clearProperty("plexbmc.%d.path" % (i))
                WINDOW.clearProperty("plexbmc.%d.window" % (i))
                WINDOW.clearProperty("plexbmc.%d.art" % (i))
                WINDOW.clearProperty("plexbmc.%d.type" % (i))
                WINDOW.clearProperty("plexbmc.%d.icon" % (i))
                WINDOW.clearProperty("plexbmc.%d.thumb" % (i))
                WINDOW.clearProperty("plexbmc.%d.recent" % (i))
                WINDOW.clearProperty("plexbmc.%d.all" % (i))
                WINDOW.clearProperty("plexbmc.%d.search" % (i))
                WINDOW.clearProperty("plexbmc.%d.viewed" % (i))
                WINDOW.clearProperty("plexbmc.%d.ondeck" % (i))
                WINDOW.clearProperty("plexbmc.%d.released" % (i))
                WINDOW.clearProperty("plexbmc.%d.shared" % (i))
                WINDOW.clearProperty("plexbmc.%d.album" % (i))
                WINDOW.clearProperty("plexbmc.%d.year" % (i))
        except:
            pass

        plexbmc.printDebug("Total number of skin sections is [" + str(sectionCount) + "]")
        plexbmc.printDebug("Total number of servers is [" + str(numOfServers) + "]")
        WINDOW.setProperty("plexbmc.sectionCount", str(sectionCount))
        WINDOW.setProperty("plexbmc.numServers", str(numOfServers))
        if plexbmc.__settings__.getSetting('myplex_user') != '':
            WINDOW.setProperty(
                "plexbmc.queue",
                "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=http://myplexqueue&mode=24,return)")
            WINDOW.setProperty("plexbmc.myplex", "1")
        else:
            WINDOW.clearProperty("plexbmc.myplex")

        return

    @staticmethod
    def amberskin(container_id=None):
        # Gather some data and set the window properties
        plexbmc.printDebug("== ENTER: amberskin() ==", False)
        # Get the global host variable set in settings

        # XXX: Unused variable 'WINDOW'
        WINDOW = xbmcgui.Window(10000)

        # XXX: Unused variable 'sectionCount'
        # XXX: Unused variable 'serverCount'
        # XXX: Unused variable 'sharedCount'
        sectionCount = 0
        serverCount = 0
        sharedCount = 0

        shared_flag = {}
        hide_shared = plexbmc.__settings__.getSetting('hide_shared')

        server_list = plexbmc.PlexServers.discoverAll()
        plexbmc.printDebug("Using list of " + str(len(server_list)) + " servers: " + str(server_list))

        # For each of the servers we have identified
        sections = plexbmc.Sections.getAllSections(server_list)
        plexbmc.printDebug("Total sections: " + str(len(sections)), False)

        listitems = list()

        for section in sections:
            plexbmc.printDebug("=Enter amberskin section=", False)
            plexbmc.printDebug(str(section), False)
            plexbmc.printDebug("=/section=", False)

            # XXX: Unused variable 'extraData'
            extraData = {'fanart_image': plexbmc.Media.getFanart(section, section['address']), 'thumb': plexbmc.g_thumb}

            # Determine what we are going to do process after a link is
            # selected by the user, based on the content we find
            path = section['path']

            if section['type'] == 'show':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['show'] = True
                    sharedCount += 1
                    continue
                window = "VideoLibrary"
                mode = plexbmc._MODE_TVSHOWS
            elif section['type'] == 'movie':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['movie'] = True
                    sharedCount += 1
                    continue
                window = "VideoLibrary"
                mode = plexbmc._MODE_MOVIES
            elif section['type'] == 'artist':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['artist'] = True
                    sharedCount += 1
                    continue
                window = "MusicFiles"
                mode = plexbmc._MODE_ARTISTS
            elif section['type'] == 'photo':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['photo'] = True
                    sharedCount += 1
                    continue
                window = "Pictures"
            else:
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['movie'] = True
                    sharedCount += 1
                    continue
                window = "Videos"
                mode = plexbmc._MODE_PHOTOS

            aToken = plexbmc.MyPlexServers.getAuthDetails(section)

            # XXX: Unused variable 'qToken'
            qToken = plexbmc.MyPlexServers.getAuthDetails(section, prefix='?')

            print 'g_secondary: %s' % plexbmc.g_secondary
            if plexbmc.g_secondary == "true":
                mode = plexbmc._MODE_GETCONTENT
            else:
                path = path + '/all'

            # mode not working with directl server connect
            s_url = 'http://%s%s&mode=%s%s' % (
                section['address'], path, mode, aToken)

            #xbmcplugin.setContent(pluginhandle, 'movies')
            print 'Entering jason_test'
            # XXX:
            path = "plugin://plugin.video.plexbmc/?url={0}".format(s_url)
            partial_path = "plugin://plugin.video.plexbmc/?url=http://{0}{1}".format(section['address'], section['path'])

            path2 = "ActivateWindow({0},plugin://plugin.video.plexbmc/?url={1},return)".format(window, s_url)
            path3 = "ActivateWindow(" + window + ",plugin://plugin.video.plexbmc/?url=" + s_url + ",return)"

            #path = "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=http://10.0.0.10:32400/library/sections/5,return)"
            print 'path: %s' % path
            print 'path2: %s' % path2
            print 'path3: %s' % path3

            info = {}
            info['label'] = section['title']
            info['label2'] = section['serverName']
            info['iconImage'] = None
            info['thumbnailImage'] = None
            info['path'] = path2

            listitem = xbmcgui.ListItem(**info)
            listitem.setProperty('token', aToken)
            listitem.setProperty('mode', str(mode))
            listitem.setProperty('partial_path', partial_path)
            #listitem.setProperty('path', path2)

            listitem.setProperty('title', section['title'])
            listitem.setProperty('subtitle', section['serverName'])
            listitem.setProperty('path', section['path'])
            listitem.setProperty('uuid', section['sectionuuid'])
            listitem.setProperty('type', section['type'])
            listitem.setProperty(
                'partial',
                "ActivateWindow(" +
                window +
                ",plugin://plugin.video.plexbmc/?url=http://" +
                section['address'] +
                section['path'])
            listitem.setProperty(
                'search',
                "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                (window,
                 section['address'],
                    section['path'],
                    "/search?type=1",
                    mode,
                    aToken))
            listitem.setProperty(
                'recent',
                "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                (window,
                 section['address'],
                    section['path'],
                    "/recentlyAdded",
                    mode,
                    aToken))
            listitem.setProperty(
                'viewed',
                "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                (window,
                 section['address'],
                    section['path'],
                    "/recentlyViewed",
                    mode,
                    aToken))
            listitem.setProperty(
                'ondeck',
                "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                (window,
                 section['address'],
                    section['path'],
                    "/onDeck",
                    mode,
                    aToken))
            listitem.setProperty(
                'newest',
                "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" %
                (window,
                 section['address'],
                    section['path'],
                    "/newest",
                    mode,
                    aToken))
            listitem.setProperty('shared', "false")
            listitem.setProperty('node.target', window)
            #listitem.setProperty('node.target_url', path2)

            # Missing
            #<property name="album">$INFO[Window(Home).Property(plexbmc.0.album)]</property>
            #<property name="year">$INFO[Window(Home).Property(plexbmc.0.year)]</property>

            # listitem.setIconImage('DefaultVideoCover.png')
            # listitem.setArt('DefaultVideoCover.png')
            # listitem.setThumbnailImage('DefaultVideoCover.png')
            # listitem.setIconImage('DefaultVideoCover.png')
            #listitem.setProperty("fanart_image", 'DefaultVideoCover.png')
            #listitem.setProperty('ItemType', 'On Deck')
            listitems.append((path, listitem, True))

            print "***************************************************************************************"
            print "***************************************************************************************"
            print "***************************************************************************************"
            print "***************************************************************************************"
            print "***************************************************************************************"
            print "***************************************************************************************"
            print dir(listitem)
            print str(listitem)
            # print vars(listitem)
            #import inspect
            # print inspect.getargspec(listitem)
            # print listitem.data
            # print getattr(listitem, 'data')
            # print listitem.__getattribute__('data')
            print "***************************************************************************************"

        '''
        print 'Finished amberskin Content Library population'##So this is where we really start the plugin.

        #Build that listing..
        WINDOW.setProperty("plexbmc.%d.uuid" % (sectionCount) , section['sectionuuid'])
        WINDOW.setProperty("plexbmc.%d.title"    % (sectionCount) , section['title'])
        WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount) , section['serverName'])
        WINDOW.setProperty("plexbmc.%d.path"     % (sectionCount) , "ActivateWindow("+window+",plugin://plugin.video.plexbmc/?url="+s_url+",return)")
        WINDOW.setProperty("plexbmc.%d.art"      % (sectionCount) , extraData['fanart_image']+qToken)
        WINDOW.setProperty("plexbmc.%d.type"     % (sectionCount) , section['type'])
        WINDOW.setProperty("plexbmc.%d.icon"     % (sectionCount) , extraData['thumb']+qToken)
        WINDOW.setProperty("plexbmc.%d.thumb"    % (sectionCount) , extraData['thumb']+qToken)
        WINDOW.setProperty("plexbmc.%d.partialpath" % (sectionCount) , "ActivateWindow("+window+",plugin://plugin.video.plexbmc/?url=http://"+section['address']+section['path'])
        WINDOW.setProperty("plexbmc.%d.search" % (sectionCount) , "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" % (window, section['address'], section['path'], "/search?type=1", mode, aToken) )
        WINDOW.setProperty("plexbmc.%d.recent" % (sectionCount) , "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" % (window, section['address'], section['path'], "/recentlyAdded", mode, aToken) )
        WINDOW.setProperty("plexbmc.%d.all" % (sectionCount) , "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" % (window, section['address'], section['path'], "/all", mode, aToken) )
        WINDOW.setProperty("plexbmc.%d.viewed" % (sectionCount) , "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" % (window, section['address'], section['path'], "/recentlyViewed", mode, aToken) )
        WINDOW.setProperty("plexbmc.%d.ondeck" % (sectionCount) , "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" % (window, section['address'], section['path'], "/onDeck", mode, aToken) )
        WINDOW.setProperty("plexbmc.%d.released" % (sectionCount) , "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" % (window, section['address'], section['path'], "/newest", mode, aToken) )
        WINDOW.setProperty("plexbmc.%d.shared"     % (sectionCount) , "false")

        if section['type'] == "artist":
            WINDOW.setProperty("plexbmc.%d.album" % (sectionCount) , "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" % (window, section['address'], section['path'], "/albums", mode, aToken) )
            WINDOW.setProperty("plexbmc.%d.search" % (sectionCount) , "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" % (window, section['address'], section['path'], "/search?type=10", mode, aToken) )
        elif section['type'] == "photo":
            WINDOW.setProperty("plexbmc.%d.year" % (sectionCount) , "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" % (window, section['address'], section['path'], "/year", mode, aToken) )
        elif section['type'] == "show":
            WINDOW.setProperty("plexbmc.%d.search" % (sectionCount) , "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" % (window, section['address'], section['path'], "/search?type=4", mode, aToken) )
        elif section['type'] == "movie":
            WINDOW.setProperty("plexbmc.%d.search" % (sectionCount) , "ActivateWindow(%s,plugin://plugin.video.plexbmc/?url=http://%s%s%s&mode=%s%s,return)" % (window, section['address'], section['path'], "/search?type=1", mode, aToken) )

        printDebug("Building window properties index [" + str(sectionCount) + "] which is [" + section['title'] + "]")
        printDebug("PATH in use is: ActivateWindow("+window+",plugin://plugin.video.plexbmc/?url="+s_url+",return)")
        sectionCount += 1

    if __settings__.getSetting('myplex_user') != '' and hide_shared == 'true' and sharedCount != 0:
        WINDOW.setProperty("plexbmc.%d.title"    % (sectionCount) , "Shared Content")
        WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount) , "Shared")
        WINDOW.setProperty("plexbmc.%d.path"     % (sectionCount) , "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode="+str(_MODE_SHARED_ALL)+",return)")
        WINDOW.setProperty("plexbmc.%d.type"     % (sectionCount) , "shared")
        WINDOW.setProperty("plexbmc.%d.shared"     % (sectionCount) , "true")
        sectionCount += 1

    elif sharedCount != 0:

        if shared_flag.get('movie'):
            WINDOW.setProperty("plexbmc.%d.title"    % (sectionCount) , "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount) , "Shared")
            WINDOW.setProperty("plexbmc.%d.path"     % (sectionCount) , "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode="+str(_MODE_SHARED_MOVIES)+",return)")
            WINDOW.setProperty("plexbmc.%d.type"     % (sectionCount) , "shared")
            WINDOW.setProperty("plexbmc.%d.shared"     % (sectionCount) , "true")
            sectionCount += 1

        if shared_flag.get('show'):
            WINDOW.setProperty("plexbmc.%d.title"    % (sectionCount) , "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount) , "Shared")
            WINDOW.setProperty("plexbmc.%d.path"     % (sectionCount) , "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode="+str(_MODE_SHARED_SHOWS)+",return)")
            WINDOW.setProperty("plexbmc.%d.type"     % (sectionCount) , "shared")
            WINDOW.setProperty("plexbmc.%d.shared"     % (sectionCount) , "true")
            sectionCount += 1

        if shared_flag.get('artist'):
            WINDOW.setProperty("plexbmc.%d.title"    % (sectionCount) , "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount) , "Shared")
            WINDOW.setProperty("plexbmc.%d.path"     % (sectionCount) , "ActivateWindow(MusicFiles,plugin://plugin.video.plexbmc/?url=/&mode="+str(_MODE_SHARED_MUSIC)+",return)")
            WINDOW.setProperty("plexbmc.%d.type"     % (sectionCount) , "shared")
            WINDOW.setProperty("plexbmc.%d.shared"     % (sectionCount) , "true")
            sectionCount += 1

        if shared_flag.get('photo'):
            WINDOW.setProperty("plexbmc.%d.title"    % (sectionCount) , "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount) , "Shared")
            WINDOW.setProperty("plexbmc.%d.path"     % (sectionCount) , "ActivateWindow(Pictures,plugin://plugin.video.plexbmc/?url=/&mode="+str(_MODE_SHARED_PHOTOS)+",return)")
            WINDOW.setProperty("plexbmc.%d.type"     % (sectionCount) , "shared")
            WINDOW.setProperty("plexbmc.%d.shared"     % (sectionCount) , "true")
            sectionCount += 1

    else:
        pass

    #For each of the servers we have identified
    numOfServers=len(server_list)
    #XXX: shelfChannel (server_list)

    for server in server_list.values():

        if server['class'] == "secondary":
            continue

        aToken=getAuthDetails(server)
        #qToken=getAuthDetails(server, prefix='?')

        if g_channelview == "true":
            WINDOW.setProperty("plexbmc.channel", "1")
            WINDOW.setProperty("plexbmc.%d.server.channel" % (serverCount) , "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=http://"+server['server']+":"+server['port']+"/system/plugins/all&mode=21"+aToken+",return)")
        else:
            WINDOW.clearProperty("plexbmc.channel")
            WINDOW.setProperty("plexbmc.%d.server.video" % (serverCount) , "http://"+server['server']+":"+server['port']+"/video&mode=7"+aToken)
            WINDOW.setProperty("plexbmc.%d.server.music" % (serverCount) , "http://"+server['server']+":"+server['port']+"/music&mode=17"+aToken)
            WINDOW.setProperty("plexbmc.%d.server.photo" % (serverCount) , "http://"+server['server']+":"+server['port']+"/photos&mode=16"+aToken)

        WINDOW.setProperty("plexbmc.%d.server.online" % (serverCount) , "http://"+server['server']+":"+server['port']+"/system/plexonline&mode=19"+aToken)

        WINDOW.setProperty("plexbmc.%d.server" % (serverCount) , server['serverName'])
        printDebug ("Name mapping is :" + server['serverName'])

        serverCount+=1

    #Clear out old data
    try:
        printDebug("Clearing properties from [" + str(sectionCount) + "] to [" + WINDOW.getProperty("plexbmc.sectionCount") + "]")

        for i in range(sectionCount, int(WINDOW.getProperty("plexbmc.sectionCount"))+1):
            WINDOW.clearProperty("plexbmc.%d.uuid"    % (i) )
            WINDOW.clearProperty("plexbmc.%d.title"    % (i) )
            WINDOW.clearProperty("plexbmc.%d.subtitle" % (i) )
            WINDOW.clearProperty("plexbmc.%d.url"      % (i) )
            WINDOW.clearProperty("plexbmc.%d.path"     % (i) )
            WINDOW.clearProperty("plexbmc.%d.window"   % (i) )
            WINDOW.clearProperty("plexbmc.%d.art"      % (i) )
            WINDOW.clearProperty("plexbmc.%d.type"     % (i) )
            WINDOW.clearProperty("plexbmc.%d.icon"     % (i) )
            WINDOW.clearProperty("plexbmc.%d.thumb"    % (i) )
            WINDOW.clearProperty("plexbmc.%d.recent"    % (i) )
            WINDOW.clearProperty("plexbmc.%d.all"    % (i) )
            WINDOW.clearProperty("plexbmc.%d.search"    % (i) )
            WINDOW.clearProperty("plexbmc.%d.viewed"    % (i) )
            WINDOW.clearProperty("plexbmc.%d.ondeck" % (i) )
            WINDOW.clearProperty("plexbmc.%d.released" % (i) )
            WINDOW.clearProperty("plexbmc.%d.shared"     % (i) )
            WINDOW.clearProperty("plexbmc.%d.album"     % (i) )
            WINDOW.clearProperty("plexbmc.%d.year"     % (i) )

    except:
        pass

    printDebug("Total number of skin sections is [" + str(sectionCount) + "]")
    printDebug("Total number of servers is ["+str(numOfServers)+"]")
    WINDOW.setProperty("plexbmc.sectionCount", str(sectionCount))
    WINDOW.setProperty("plexbmc.numServers", str(numOfServers))

    if __settings__.getSetting('myplex_user') != '':
        WINDOW.setProperty("plexbmc.queue" , "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=http://myplexqueue&mode=24,return)")
        WINDOW.setProperty("plexbmc.myplex",  "1" )

        #Now let's populate queue shelf items since we have MyPlex login
        if __settings__.getSetting('homeshelf') != '3':
            printDebug("== ENTER: Queue Shelf ==", False)
            aToken = getMyPlexToken()
            myplex_server = getMyPlexURL('/pms/playlists/queue/all')
            root = etree.fromstring(myplex_server)
            server_address = getMasterServer()['address']
            queue_count = 1

            for media in root:
                printDebug("Found a queue item entry: [%s]" % (media.get('title', '').encode('UTF-8') , ))
                m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&indirect=%s&t=%s" % (getLinkURL('http://'+server_address, media, server_address), 18, 1, aToken)
                m_thumb = getShelfThumb(media, server_address, seasonThumb=0)+aToken

                try:
                    movie_runtime = str(int(float(media.get('duration'))/1000/60))
                except:
                    movie_runtime = ""

                WINDOW.setProperty("Plexbmc.Queue.%s.Path" % queue_count, m_url)
                WINDOW.setProperty("Plexbmc.Queue.%s.Title" % queue_count, media.get('title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.Queue.%s.Year" % queue_count, media.get('originallyAvailableAt', '').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.Queue.%s.Duration" % queue_count, movie_runtime)
                WINDOW.setProperty("Plexbmc.Queue.%s.Thumb" % queue_count, m_thumb)

                queue_count += 1

                printDebug("Building Queue item: %s" % media.get('title', 'Unknown').encode('UTF-8'))
                printDebug("Building Queue item url: %s" % m_url)
                printDebug("Building Queue item thumb: %s" % m_thumb)

            clearQueueShelf(queue_count)

    else:
        WINDOW.clearProperty("plexbmc.myplex")

    #XXX: fullShelf(server_list)
    '''
        info = {}
        # Channels
        info['label'] = plexbmc.__localize__(30098)
        info['label2'] = 'channels'
        info['iconImage'] = None
        info['thumbnailImage'] = "special://skin/backgrounds/Channels.jpg"
        #info['path'] = "plugin://plugin.video.plexbmc/?mode=22&amp;url=http://online%2fsystem%2fplugins%2fall"
        info['path'] = "plugin://plugin.video.plexbmc/?mode=22&url=http://online%2fsystem%2fplugins%2fall"
        listitem = xbmcgui.ListItem(**info)
        listitem.setProperty('node.target', 'Videos')
        listitems.append((info['path'], listitem, True))
        '''
        <item id="50" description="Channels">
          <visible>Skin.HasSetting(plexbmc) + !Skin.HasSetting(Channels.Hide)</visible>
          <label>$LOCALIZE[31975]</label>
          <thumb>special://skin/backgrounds/Channels.jpg</thumb>
          <onclick>ActivateWindow(Videos,"plugin://plugin.video.plexbmc/?mode=22&amp;url=http://online%2fsystem%2fplugins%2fall",return)</onclick>
        </item>
        <item id="49" description="Queue">
          <visible>Skin.HasSetting(plexbmc) + !Skin.HasSetting(Queue.Hide)</visible>
          <label>$LOCALIZE[31010]</label>
          <thumb fallback="special://skin/backgrounds/Network.jpg">$INFO[Skin.String(Network.Background)]</thumb>
          <onclick>$INFO[Window(Home).Property(plexbmc.queue)]</onclick>
          <visible>!IsEmpty(Window(Home).Property(plexbmc.myplex))</visible>
        </item>
        '''
        # XXX:
        # If we have a container_id, we were meant to append to the list
        if False:
            pass
        elif container_id:
            plexbmc.printDebug('container_id: %s' % str(container_id))
            try:
                window = xbmcgui.Window(10000)
                home_list = window.getControl(container_id)

                print 'GOT CONTROL'
                print home_list.size()
                testitems = []
                print listitems
                for (target, listitem, isFolder) in listitems:
                    print listitem
                    # home_list.addItem(listitem)
                    # home_list.setStaticContent(listitem)
                    testitems.append(listitem)
                # home_list.setStaticContent(items=testitems)
                home_list.addItems(items=testitems)

                # home_list.addItems(testitems)
                # home_list.setVisible(True)

                # window.doModal()
                li = home_list.getListItem(0)
                print li.getLabel()
                print home_list.size()
                # print dir(home_list)
                print home_list.getId()
                print window.getFocusId()
                print xbmcgui.getCurrentWindowId()
            except Exception:
                plexbmc.printDebug('Unable to getControl(%s)' % str(container_id))
            #xbmcplugin.addDirectoryItems(300, listitems)
            # xbmcplugin.endOfDirectory(handle=container_id)
        else:
            xbmcplugin.addDirectoryItems(plexbmc.PleXBMC.getHandle(), listitems)
            xbmcplugin.endOfDirectory(handle=plexbmc.PleXBMC.getHandle())
            #xbmcplugin.endOfDirectory(pluginhandle, succeeded=True, updateListing=False, cacheToDisc=False)

    @staticmethod
    def fullShelf(server_list={}):
        # pylint: disable=E1103
        # Instance of 'dict' has no 'xxx' member

        # Gather some data and set the window properties
        plexbmc.printDebug("== ENTER: fullShelf ==", False)

        if plexbmc.__settings__.getSetting('homeshelf') == '3' or ((plexbmc.__settings__.getSetting(
                'movieShelf') == "false" and plexbmc.__settings__.getSetting('tvShelf') == "false" and plexbmc.__settings__.getSetting('musicShelf') == "false")):
            plexbmc.printDebug("Disabling all shelf items")
            server_list.clearShelf()
            server_list.clearOnDeckShelf()
            return

        # Get the global host variable set in settings
        WINDOW = xbmcgui.Window(10000)

        recentMovieCount = 1
        recentSeasonCount = 1
        recentMusicCount = 1
        recentPhotoCount = 1
        ondeckMovieCount = 1
        ondeckSeasonCount = 1
        recent_list = {}
        ondeck_list = {}
        full_count = 0

        if server_list == {}:
            server_list = plexbmc.PlexServers.discoverAll()

        if server_list == {}:
            xbmc.executebuiltin("XBMC.Notification(Unable to see any media servers,)")
            server_list.clearShelf(0, 0, 0, 0)
            return

        randomNumber = str(random.randint(1000000000, 9999999999))
        '''
        logfile = PLUGINPATH+"/_server_list.txt"
        logfileh = open(logfile, "w")
        logfileh.write(str(server_list))
        logfileh.close()
        '''
        serverList = []

        for key, value in server_list.iteritems():
            temp = [key, value]
            serverList.append(temp)

        for index in serverList:
            for server_details in server_list.values():
                if not server_details['owned'] == '1':
                    continue

                #global token
                token = server_details.get('token', '')
                aToken = plexbmc.MyPlexServers.getAuthDetails({'token': token})
                qToken = '?' + aToken

                sections = plexbmc.Sections.getAllSections(server_list)

                # XXX: Unused variable 'ra_log_count'
                ra_log_count = 1

                if plexbmc.__settings__.getSetting('homeshelf') == '0' or plexbmc.__settings__.getSetting('homeshelf') == '2':
                    '''
                    logfile = PLUGINPATH+"/_shelf_sections_.txt"
                    logfileh = open(logfile, "w")
                    logfileh.write(str(sections))
                    logfileh.close()
                    '''
                    for section in sections:
                        recent_url = section.get('address') + section.get("path") + "/recentlyAdded"
                        #token = section.get('token', '')
                        tree = plexbmc.PlexServers.getURL(recent_url)
                        tree = plexbmc.etree.fromstring(tree)
                        token = server_details.get('token', '')
                        '''
                        eetee = etree.ElementTree()
                        eetee._setroot(tree)
                        logfile = PLUGINPATH+"/RecentlyAdded"+ str(ra_log_count) + ".xml"
                        logfileh = open(logfile, "w")
                        eetee.write(logfileh)
                        logfileh.close()
                        ra_log_count += 1
                        '''
                        if tree is None:
                            plexbmc.printDebug("PLEXBMC -> RecentlyAdded items not found on: " + recent_url, False)
                            continue
                        libraryuuid = tree.attrib["librarySectionUUID"]
                        ep_helper = {}  # helper season counter
                        ra_item_count = 1
                        for eachitem in tree:
                            if ra_item_count > 15:
                                break
                            if eachitem.get("type", "") == "episode":
                                # season identifier
                                key = int(eachitem.get("parentRatingKey"))
                                if key in ep_helper or (
                                    (plexbmc.__settings__.getSetting('hide_watched_recent_items') == 'true' and int(
                                        eachitem.get(
                                            "viewCount",
                                            0)) > 0)):
                                    pass
                                else:
                                    recent_list[full_count] = (eachitem, section.get('address'), aToken, qToken, libraryuuid)
                                    # use seasons as dict key so we can check
                                    ep_helper[key] = key
                                    full_count += 1
                                    ra_item_count += 1
                            else:
                                recent_list[full_count] = (eachitem, section.get('address'), aToken, qToken, libraryuuid)
                                full_count += 1
                                ra_item_count += 1
                    full_count = 0
                    '''
                    logfile = PLUGINPATH+"/Recent_list.log"
                    logfileh = open(logfile, "w")
                    for item in recent_list:
                        logfileh.write("%s\n" % item)
                    logfileh.close()
                    '''
                    #deck_log_count = 1
                if plexbmc.__settings__.getSetting('homeshelf') == '1' or plexbmc.__settings__.getSetting('homeshelf') == '2':
                    for section in sections:
                        ondeck_url = section.get('address') + section.get("path") + "/onDeck"
                        #token = section.get('token', '')
                        tree = plexbmc.PlexServers.getURL(ondeck_url)
                        tree = plexbmc.etree.fromstring(tree)
                        token = server_details.get('token', '')
                        '''
                        eetee = etree.ElementTree()
                        eetee._setroot(tree)
                        logfile = PLUGINPATH+"/OnDeck"+ str(deck_file_count) + ".xml"
                        logfileh = open(logfile, "w")
                        eetee.write(logfileh)
                        logfileh.close()
                        deck_log_count += 1
                        '''
                        if tree is None:
                            #xbmc.executebuiltin("XBMC.Notification(Unable to contact server: "+server_details['serverName']+",)")
                            # clearShelf()
                            # return
                            print ("PLEXBMC -> OnDeck items not found on: " + ondeck_url, False)
                            continue
                        deck_item_count = 1
                        libraryuuid = tree.attrib["librarySectionUUID"]
                        for eachitem in tree:
                            if deck_item_count > 15:
                                break
                            deck_item_count += 1
                            #libraryuuid = tree.attrib["librarySectionUUID"]
                            ondeck_list[full_count] = (eachitem, section.get('address'), aToken, qToken, libraryuuid)
                            full_count += 1
        # For each of the servers we have identified
        for index in recent_list:
            media = recent_list[index][0]
            server_address = recent_list[index][1]
            aToken = recent_list[index][2]
            qToken = recent_list[index][3]
            libuuid = recent_list[index][4]

            if media.get('type', None) == "movie":
                plexbmc.printDebug("Found a recent movie entry: [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))
                if plexbmc.__settings__.getSetting('movieShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestMovie.1.Path")
                    continue
                if plexbmc.__settings__.getSetting('hide_watched_recent_items') == 'false' or media.get("viewCount", 0) == 0:
                    m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s" % (plexbmc.Utility.getLinkURL(
                        'http://' + server_address,
                        media,
                        server_address),
                        plexbmc._MODE_PLAYSHELF,
                        randomNumber,
                        aToken)
                    m_thumb = server_list.getShelfThumb(media, server_address, seasonThumb=0) + aToken
                    if media.get('duration') > 0:
                        #movie_runtime = media.get('duration', '0')
                        movie_runtime = str(int(float(media.get('duration')) / 1000 / 60))
                    else:
                        movie_runtime = ""
                    if media.get('rating') > 0:
                        movie_rating = str(round(float(media.get('rating')), 1))
                    else:
                        movie_rating = ''

                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.Path" % recentMovieCount, m_url)
                    WINDOW.setProperty(
                        "Plexbmc.LatestMovie.%s.Title" %
                        recentMovieCount,
                        media.get(
                            'title',
                            'Unknown').encode('UTF-8'))
                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.Year" % recentMovieCount, media.get('year', '').encode('UTF-8'))
                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.Rating" % recentMovieCount, movie_rating)
                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.Duration" % recentMovieCount, movie_runtime)
                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.Thumb" % recentMovieCount, m_thumb)
                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.uuid" % recentMovieCount, libuuid.encode('UTF-8'))
                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.Plot" % recentMovieCount, media.get('summary', '').encode('UTF-8'))

                    m_genre = []

                    for child in media:
                        if child.tag == "Genre":
                            m_genre.append(child.get('tag'))
                        else:
                            continue

                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.Genre" % recentMovieCount, ", ".join(m_genre).encode('UTF-8'))

                    recentMovieCount += 1

                    plexbmc.printDebug("Building Recent window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
                    plexbmc.printDebug("Building Recent window url: %s" % m_url)
                    plexbmc.printDebug("Building Recent window thumb: %s" % m_thumb)
                else:
                    continue
            elif media.get('type', None) == "season":
                plexbmc.printDebug("Found a recent season entry [%s]" % (media.get('parentTitle', 'Unknown').encode('UTF-8'), ))

                if plexbmc.__settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
                    continue

                s_url = "ActivateWindow(VideoLibrary, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address),
                    plexbmc._MODE_TVEPISODES,
                    aToken)
                s_thumb = server_list.getShelfThumb(media, server_address, seasonThumb=0) + aToken

                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Path" % recentSeasonCount, s_url)
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeTitle" % recentSeasonCount, '')
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.EpisodeSeason" %
                    recentSeasonCount,
                    media.get(
                        'title',
                        '').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.ShowTitle" %
                    recentSeasonCount,
                    media.get(
                        'parentTitle',
                        'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Thumb" % recentSeasonCount, s_thumb)
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.uuid" %
                    recentSeasonCount,
                    media.get(
                        'librarySectionUUID',
                        '').encode('UTF-8'))

                recentSeasonCount += 1

                plexbmc.printDebug("Building Recent window title: %s" % media.get('parentTitle', 'Unknown').encode('UTF-8'))
                plexbmc.printDebug("Building Recent window url: %s" % s_url)
                plexbmc.printDebug("Building Recent window thumb: %s" % s_thumb)

            elif media.get('type') == "album":
                if plexbmc.__settings__.getSetting('musicShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestAlbum.1.Path")
                    continue
                plexbmc.printDebug("Found a recent album entry")

                s_url = "ActivateWindow(MusicFiles, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address),
                    plexbmc._MODE_TRACKS,
                    aToken)
                s_thumb = server_list.getShelfThumb(media, server_address, seasonThumb=0) + aToken

                WINDOW.setProperty("Plexbmc.LatestAlbum.%s.Path" % recentMusicCount, s_url)
                WINDOW.setProperty("Plexbmc.LatestAlbum.%s.Title" % recentMusicCount, media.get('title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestAlbum.%s.Artist" %
                    recentMusicCount,
                    media.get(
                        'parentTitle',
                        'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestAlbum.%s.Thumb" % recentMusicCount, s_thumb)

                recentMusicCount += 1

                plexbmc.printDebug("Building Recent window title: %s" % media.get('parentTitle', 'Unknown').encode('UTF-8'))
                plexbmc.printDebug("Building Recent window url: %s" % s_url)
                plexbmc.printDebug("Building Recent window thumb: %s" % s_thumb)

            elif media.get('type') == "photo":
                plexbmc.printDebug("Found a recent photo entry: [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))

                p_url = "ActivateWindow(Pictures, plugin://plugin.video.plexbmc/?url=http://%s%s&mode=%s%s,return" % (
                    server_address, "/recentlyAdded", plexbmc._MODE_PHOTOS, aToken)
                p_thumb = server_list.getShelfThumb(media, server_address, seasonThumb=0) + aToken

                WINDOW.setProperty("Plexbmc.LatestPhoto.%s.Path" % recentPhotoCount, p_url)
                WINDOW.setProperty("Plexbmc.LatestPhoto.%s.Title" % recentPhotoCount, media.get('title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestPhoto.%s.Thumb" % recentPhotoCount, p_thumb)

                recentPhotoCount += 1

                plexbmc.printDebug("Building Recent photo window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
                plexbmc.printDebug("Building Recent photo window url: %s" % p_url)
                plexbmc.printDebug("Building Recent photo window thumb: %s" % p_thumb)
            elif media.get('type', None) == "episode":
                plexbmc.printDebug("Found an Recent episode entry [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))

                if plexbmc.__settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
                    continue

                s_url = "ActivateWindow(Videos, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address,
                    season_shelf=True),
                    plexbmc._MODE_TVEPISODES,
                    aToken)
                s_thumb = server_list.getShelfThumb(media, server_address, seasonThumb=1) + aToken

                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Path" % recentSeasonCount, s_url)
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.EpisodeTitle" %
                    recentSeasonCount,
                    media.get(
                        'title',
                        '').encode('utf-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.EpisodeNumber" %
                    recentSeasonCount,
                    media.get(
                        'index',
                        '').encode('utf-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.EpisodeSeason" %
                    recentSeasonCount,
                    media.get(
                        'parentIndex',
                        '').encode('UTF-8') +
                    '.' +
                    media.get(
                        'index',
                        'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.EpisodeSeasonNumber" %
                    recentSeasonCount,
                    media.get(
                        'parentIndex',
                        '').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.ShowTitle" %
                    recentSeasonCount,
                    media.get(
                        'grandparentTitle',
                        '').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Thumb" % recentSeasonCount, s_thumb)
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.uuid" % recentSeasonCount, libuuid.encode('utf-8'))

                plexbmc.printDebug("Building RecentEpisode window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
                plexbmc.printDebug("Building RecentEpisode window url: %s" % s_url)
                plexbmc.printDebug("Building RecentEpisode window thumb: %s" % s_thumb)

                recentSeasonCount += 1
        server_list.clearShelf(
            recentMovieCount, recentSeasonCount, recentMusicCount, recentPhotoCount)

        # For each of the servers we have identified
        for index in sorted(ondeck_list):
            media = ondeck_list[index][0]
            server_address = ondeck_list[index][1]
            aToken = ondeck_list[index][2]
            qToken = ondeck_list[index][3]
            libuuid = ondeck_list[index][4]

            if media.get('type', None) == "movie":
                plexbmc.printDebug("Found a OnDeck movie entry: [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))
                if plexbmc.__settings__.getSetting('movieShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.OnDeckMovie.1.Path")
                    continue

                m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s" % (plexbmc.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address),
                    plexbmc._MODE_PLAYSHELF,
                    randomNumber,
                    aToken)
                m_thumb = server_list.getShelfThumb(media, server_address, seasonThumb=0) + aToken

                if media.get('duration') > 0:
                    #movie_runtime = media.get('duration', '0')
                    movie_runtime = str(int(float(media.get('duration')) / 1000 / 60))
                else:
                    movie_runtime = ""

                if media.get('rating') > 0:
                    m_rating = str(round(float(media.get('rating')), 1))
                else:
                    m_rating = ''

                WINDOW.setProperty("Plexbmc.OnDeckMovie.%s.Path" % ondeckMovieCount, m_url)
                WINDOW.setProperty("Plexbmc.OnDeckMovie.%s.Title" % ondeckMovieCount, media.get('title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.OnDeckMovie.%s.Year" % ondeckMovieCount, media.get('year', '').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.OnDeckMovie.%s.Rating" % ondeckMovieCount, m_rating)
                WINDOW.setProperty("Plexbmc.OnDeckMovie.%s.Duration" % ondeckMovieCount, movie_runtime)
                WINDOW.setProperty("Plexbmc.OnDeckMovie.%s.Thumb" % ondeckMovieCount, m_thumb)
                WINDOW.setProperty("Plexbmc.OnDeckMovie.%s.uuid" % ondeckMovieCount, libuuid.encode('UTF-8'))

                ondeckMovieCount += 1

                plexbmc.printDebug("Building OnDeck Movie window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
                plexbmc.printDebug("Building OnDeck Movie window url: %s" % m_url)
                plexbmc.printDebug("Building OnDeck Movie window thumb: %s" % m_thumb)

            elif media.get('type', None) == "season":
                plexbmc.printDebug("Found a OnDeck season entry [%s]" % (media.get('parentTitle', 'Unknown').encode('UTF-8'), ))
                if plexbmc.__settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.OnDeckEpisode.1.Path")
                    continue

                s_url = "ActivateWindow(VideoLibrary, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address),
                    plexbmc._MODE_TVEPISODES,
                    aToken)
                s_thumb = server_list.getShelfThumb(media, server_address, seasonThumb=0) + aToken

                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.Path" % ondeckSeasonCount, s_url)
                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.EpisodeTitle" % ondeckSeasonCount, '')
                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.EpisodeSeason" %
                    ondeckSeasonCount,
                    media.get(
                        'title',
                        '').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.ShowTitle" %
                    ondeckSeasonCount,
                    media.get(
                        'parentTitle',
                        'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.Thumb" % ondeckSeasonCount, s_thumb)

                ondeckSeasonCount += 1

                plexbmc.printDebug("Building OnDeck window title: %s" % media.get('parentTitle', 'Unknown').encode('UTF-8'))
                plexbmc.printDebug("Building OnDeck window url: %s" % s_url)
                plexbmc.printDebug("Building OnDeck window thumb: %s" % s_thumb)
            elif media.get('type', None) == "episode":
                plexbmc.printDebug("Found an onDeck episode entry [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))

                if plexbmc.__settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.OnDeckEpisode.1.Path")
                    continue

                s_url = "PlayMedia(plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s)" % (plexbmc.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address),
                    plexbmc._MODE_PLAYSHELF,
                    randomNumber,
                    aToken)
                # s_thumb="http://"+server_address+media.get('grandparentThumb','')
                s_thumb = server_list.getShelfThumb(media, server_address, seasonThumb=1)

                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.Path" % ondeckSeasonCount, s_url)
                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.EpisodeTitle" %
                    ondeckSeasonCount,
                    media.get(
                        'title',
                        '').encode('utf-8'))
                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.EpisodeNumber" %
                    ondeckSeasonCount,
                    media.get(
                        'index',
                        '').encode('utf-8'))
                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.EpisodeSeason" %
                    ondeckSeasonCount,
                    media.get(
                        'grandparentTitle',
                        'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.EpisodeSeasonNumber" %
                    ondeckSeasonCount,
                    media.get(
                        'parentIndex',
                        '').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.ShowTitle" %
                    ondeckSeasonCount,
                    media.get(
                        'title',
                        'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.Thumb" % ondeckSeasonCount, s_thumb + aToken)
                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.uuid" % ondeckSeasonCount, libuuid.encode('UTF-8'))

                ondeckSeasonCount += 1

                plexbmc.printDebug("Building OnDeck window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
                plexbmc.printDebug("Building OnDeck window url: %s" % s_url)
                plexbmc.printDebug("Building OnDeck window thumb: %s" % s_thumb)

        server_list.clearOnDeckShelf(ondeckMovieCount, ondeckSeasonCount)

        if plexbmc.__settings__.getSetting('channelShelf') == "true" or plexbmc.__settings__.getSetting('homeshelf') != '3':
            server_list.shelfChannel(server_list)
        else:
            plexbmc.printDebug("Disabling channel shelf items")
            server_list.clearChannelShelf()

    @staticmethod
    def shelf(server_list=None):
        # pylint: disable=E1103
        # Instance of 'dict' has no 'xxx' member

        # Gather some data and set the window properties
        plexbmc.printDebug("== ENTER: shelf() ==", False)

        if (plexbmc.__settings__.getSetting('movieShelf') == "false" and plexbmc.__settings__.getSetting('tvShelf') ==
                "false" and plexbmc.__settings__.getSetting('musicShelf') == "false") or plexbmc.__settings__.getSetting('homeshelf') == '3':
            plexbmc.printDebug("Disabling all shelf items")
            server_list.clearShelf()
            return

        # Get the global host variable set in settings
        WINDOW = xbmcgui.Window(10000)

        movieCount = 1
        seasonCount = 1
        musicCount = 1
        added_list = {}
        direction = True
        full_count = 0

        if server_list is None:
            server_list = plexbmc.PlexServers.discoverAll()

        if server_list == {}:
            xbmc.executebuiltin("XBMC.Notification(Unable to see any media servers,)")
            server_list.clearShelf(0, 0, 0)
            return

        if plexbmc.__settings__.getSetting('homeshelf') == '0' or plexbmc.__settings__.getSetting('homeshelf') == '2':
            endpoint = "/library/recentlyAdded"
        else:
            direction = False
            endpoint = "/library/onDeck"

        randomNumber = str(random.randint(1000000000, 9999999999))
        for server_details in server_list.values():
            if server_details['class'] == "secondary":
                continue

            if not server_details['owned'] == '1':
                continue

            #global token
            token = server_details.get('token', '')
            aToken = plexbmc.MyPlexServers.getAuthDetails({'token': token})
            qToken = plexbmc.MyPlexServers.getAuthDetails({'token': token}, prefix='?')

            tree = plexbmc.Utility.getXML('http://' + server_details['server'] + ":" + server_details['port'] + endpoint)
            if tree is None:
                xbmc.executebuiltin("XBMC.Notification(Unable to contact server: " + server_details['serverName'] + ",)")
                server_list.clearShelf()
                return

            for eachitem in tree:
                if direction:
                    added_list[int(eachitem.get('addedAt', 0))] = (
                        eachitem, server_details['server'] + ":" + server_details['port'], aToken, qToken)
                else:
                    added_list[full_count] = (eachitem, server_details['server'] + ":" + server_details['port'], aToken, qToken)
                    full_count += 1

        library_filter = plexbmc.__settings__.getSetting('libraryfilter')
        acceptable_level = plexbmc.__settings__.getSetting('contentFilter')

        # For each of the servers we have identified
        for index in sorted(added_list, reverse=direction):
            media = added_list[index][0]
            server_address = added_list[index][1]
            aToken = added_list[index][2]
            qToken = added_list[index][3]

            if media.get('type', None) == "movie":
                plexbmc.printDebug("Found a recent movie entry: [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))

                if plexbmc.__settings__.getSetting('movieShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestMovie.1.Path")
                    continue
                if not plexbmc.Utility.displayContent(acceptable_level, media.get('contentRating')):
                    continue
                if media.get('librarySectionID') == library_filter:
                    plexbmc.printDebug("SKIPPING: Library Filter match: %s = %s " % (library_filter, media.get('librarySectionID')))
                    continue

                m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s" % (plexbmc.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address),
                    plexbmc._MODE_PLAYSHELF,
                    randomNumber,
                    aToken)
                m_thumb = plexbmc.Media.getThumb(media, server_address)

                WINDOW.setProperty("Plexbmc.LatestMovie.%s.Path" % movieCount, m_url)
                WINDOW.setProperty("Plexbmc.LatestMovie.%s.Title" % movieCount, media.get('title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestMovie.%s.Thumb" % movieCount, m_thumb + qToken)

                movieCount += 1

                plexbmc.printDebug("Building Recent window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
                plexbmc.printDebug("Building Recent window url: %s" % m_url)
                plexbmc.printDebug("Building Recent window thumb: %s" % m_thumb)
            elif media.get('type', None) == "season":
                plexbmc.printDebug("Found a recent season entry [%s]" % (media.get('parentTitle', 'Unknown').encode('UTF-8'), ))

                if plexbmc.__settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
                    continue

                s_url = "ActivateWindow(VideoLibrary, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address),
                    plexbmc._MODE_TVEPISODES,
                    aToken)
                s_thumb = plexbmc.Media.getThumb(media, server_address)

                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Path" % seasonCount, s_url)
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeTitle" % seasonCount, '')
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeSeason" % seasonCount, media.get('title', '').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.ShowTitle" %
                    seasonCount,
                    media.get(
                        'parentTitle',
                        'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Thumb" % seasonCount, s_thumb + qToken)
                seasonCount += 1

                plexbmc.printDebug("Building Recent window title: %s" % media.get('parentTitle', 'Unknown').encode('UTF-8'))
                plexbmc.printDebug("Building Recent window url: %s" % s_url)
                plexbmc.printDebug("Building Recent window thumb: %s" % s_thumb)
            elif media.get('type') == "album":
                if plexbmc.__settings__.getSetting('musicShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestAlbum.1.Path")
                    continue
                plexbmc.printDebug("Found a recent album entry")

                s_url = "ActivateWindow(MusicFiles, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address),
                    plexbmc._MODE_TRACKS,
                    aToken)
                s_thumb = plexbmc.Media.getThumb(media, server_address)

                WINDOW.setProperty("Plexbmc.LatestAlbum.%s.Path" % musicCount, s_url)
                WINDOW.setProperty("Plexbmc.LatestAlbum.%s.Title" % musicCount, media.get('title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestAlbum.%s.Artist" %
                    musicCount,
                    media.get(
                        'parentTitle',
                        'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestAlbum.%s.Thumb" % musicCount, s_thumb + qToken)
                musicCount += 1

                plexbmc.printDebug("Building Recent window title: %s" % media.get('parentTitle', 'Unknown').encode('UTF-8'))
                plexbmc.printDebug("Building Recent window url: %s" % s_url)
                plexbmc.printDebug("Building Recent window thumb: %s" % s_thumb)

            elif media.get('type', None) == "episode":
                plexbmc.printDebug("Found an onDeck episode entry [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))

                if plexbmc.__settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
                    continue

                s_url = "PlayMedia(plugin://plugin.video.plexbmc?url=%s&mode=%s%s)" % (plexbmc.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address),
                    plexbmc._MODE_PLAYSHELF,
                    aToken)
                s_thumb = "http://" + server_address + media.get('grandparentThumb', '')

                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Path" % seasonCount, s_url)
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeTitle" % seasonCount, media.get('title', '').encode('utf-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.EpisodeSeason" %
                    seasonCount,
                    media.get(
                        'grandparentTitle',
                        'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.ShowTitle" %
                    seasonCount,
                    media.get(
                        'title',
                        'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Thumb" % seasonCount, s_thumb + qToken)
                seasonCount += 1

                plexbmc.printDebug("Building Recent window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
                plexbmc.printDebug("Building Recent window url: %s" % s_url)
                plexbmc.printDebug("Building Recent window thumb: %s" % s_thumb)

        server_list.clearShelf(movieCount, seasonCount, musicCount)

    @staticmethod
    def clearShelf(movieCount=0, seasonCount=0, musicCount=0, photoCount=0):
        # Clear out old data
        WINDOW = xbmcgui.Window(10000)
        plexbmc.printDebug("Clearing unused properties")

        try:
            for i in range(movieCount, 50 + 1):
                WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Path" % (i))
                WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Title" % (i))
                WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Year" % (i))
                WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Rating" % (i))
                WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Duration" % (i))
                WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Thumb" % (i))
                WINDOW.clearProperty("Plexbmc.LatestMovie.%s.uuid" % (i))
            plexbmc.printDebug("Done clearing movies")
        except:
            pass

        try:
            for i in range(seasonCount, 50 + 1):
                WINDOW.clearProperty("Plexbmc.LatestEpisode.%s.Path" % (i))
                WINDOW.clearProperty("Plexbmc.LatestEpisode.%s.EpisodeTitle" % (i))
                WINDOW.clearProperty("Plexbmc.LatestEpisode.%s.EpisodeSeason" % (i))
                WINDOW.clearProperty("Plexbmc.LatestEpisode.%s.ShowTitle" % (i))
                WINDOW.clearProperty("Plexbmc.LatestEpisode.%s.Thumb" % (i))
                WINDOW.clearProperty("Plexbmc.LatestEpisode.%s.uuid" % (i))
            plexbmc.printDebug("Done clearing tv")
        except:
            pass

        try:
            for i in range(musicCount, 25 + 1):
                WINDOW.clearProperty("Plexbmc.LatestAlbum.%s.Path" % (i))
                WINDOW.clearProperty("Plexbmc.LatestAlbum.%s.Title" % (i))
                WINDOW.clearProperty("Plexbmc.LatestAlbum.%s.Artist" % (i))
                WINDOW.clearProperty("Plexbmc.LatestAlbum.%s.Thumb" % (i))
            plexbmc.printDebug("Done clearing music")
        except:
            pass

        try:
            for i in range(photoCount, 25 + 1):
                WINDOW.clearProperty("Plexbmc.LatestPhoto.%s.Path" % (i))
                WINDOW.clearProperty("Plexbmc.LatestPhoto.%s.Title" % (i))
                WINDOW.clearProperty("Plexbmc.LatestPhoto.%s.Thumb" % (i))
            plexbmc.printDebug("Done clearing photos")
        except:
            pass

        return

    @staticmethod
    def clearOnDeckShelf(movieCount=0, seasonCount=0):
        # Clear out old data
        WINDOW = xbmcgui.Window(10000)
        plexbmc.printDebug("Clearing unused On Deck properties")

        try:
            for i in range(movieCount, 60 + 1):
                WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Path" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Title" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Thumb" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Rating" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Duration" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Year" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.uuid" % (i))
            plexbmc.printDebug("Done clearing On Deck movies")
        except:
            pass

        try:
            for i in range(seasonCount, 60 + 1):
                WINDOW.clearProperty("Plexbmc.OnDeckEpisode.%s.Path" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckEpisode.%s.EpisodeTitle" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckEpisode.%s.EpisodeSeason" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckEpisode.%s.ShowTitle" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckEpisode.%s.Thumb" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckEpisode.%s.uuid" % (i))
            plexbmc.printDebug("Done clearing On Deck tv")
        except:
            pass

        return

    @staticmethod
    def shelfChannel(server_list=None):
        # pylint: disable=E1103
        # Instance of 'dict' has no 'xxx' member

        # Gather some data and set the window properties
        plexbmc.printDebug("== ENTER: shelfChannels() ==", False)

        if plexbmc.__settings__.getSetting('channelShelf') == "false" or plexbmc.__settings__.getSetting('homeshelf') == '3':
            plexbmc.printDebug("Disabling channel shelf")
            server_list.clearChannelShelf()
            return

        # Get the global host variable set in settings
        WINDOW = xbmcgui.Window(10000)

        channelCount = 1

        if server_list is None:
            server_list = plexbmc.PlexServers.discoverAll()

        if server_list == {}:
            xbmc.executebuiltin("XBMC.Notification(Unable to see any media servers,)")
            server_list.clearChannelShelf()
            return

        for server_details in server_list.values():
            if server_details['class'] == "secondary":
                continue

            if not server_details['owned'] == '1':
                continue

            #global token
            token = server_details.get('token', '')
            aToken = plexbmc.MyPlexServers.getAuthDetails({'token': token})

            # XXX: Unused variable 'qToken'
            qToken = plexbmc.MyPlexServers.getAuthDetails({'token': token}, prefix='?')

            if plexbmc.__settings__.getSetting('channelShelf') == "false" or plexbmc.__settings__.getSetting('homeshelf') == '3':
                WINDOW.clearProperty("Plexbmc.LatestChannel.1.Path")
                return

            tree = plexbmc.Utility.getXML(
                'http://' +
                server_details['server'] +
                ":" +
                server_details['port'] +
                '/channels/recentlyViewed')
            if tree is None:
                xbmc.executebuiltin("XBMC.Notification(Unable to contact server: " + server_details['serverName'] + ",)")
                server_list.clearChannelShelf(0)
                return

            # For each of the servers we have identified
            for media in tree:
                plexbmc.printDebug("Found a recent channel entry")
                suffix = media.get('key').split('/')[1]

                if suffix == "photos":
                    mode = plexbmc._MODE_PHOTOS
                    channel_window = "Pictures"
                elif suffix == "video":
                    mode = plexbmc._MODE_PLEXPLUGINS
                    channel_window = "VideoLibrary"
                elif suffix == "music":
                    mode = plexbmc._MODE_MUSIC
                    channel_window = "MusicFiles"
                else:
                    mode = plexbmc._MODE_GETCONTENT
                    channel_window = "VideoLibrary"

                c_url = "ActivateWindow(%s, plugin://plugin.video.plexbmc?url=%s&mode=%s%s)" % (channel_window,
                                                                                                plexbmc.Utility.getLinkURL(
                                                                                                    'http://' + server_details['server'] + ":" + server_details['port'],
                                                                                                    media,
                                                                                                    server_details['server'] + ":" + server_details['port']),
                                                                                                mode,
                                                                                                aToken)
                pms_thumb = str(media.get('thumb', ''))

                if pms_thumb.startswith('/'):
                    c_thumb = 'http://' + server_details['server'] + ":" + server_details['port'] + pms_thumb
                else:
                    c_thumb = pms_thumb

                WINDOW.setProperty("Plexbmc.LatestChannel.%s.Path" % channelCount, c_url)
                WINDOW.setProperty("Plexbmc.LatestChannel.%s.Title" % channelCount, media.get('title', 'Unknown'))
                WINDOW.setProperty("Plexbmc.LatestChannel.%s.Thumb" % channelCount, c_thumb + aToken)

                channelCount += 1

                plexbmc.printDebug("Building Recent window title: %s" % media.get('title', 'Unknown'))
                plexbmc.printDebug("Building Recent window url: %s" % c_url)
                plexbmc.printDebug("Building Recent window thumb: %s" % c_thumb)

        server_list.clearChannelShelf(channelCount)
        return

    @staticmethod
    def clearChannelShelf(channelCount=0):
        WINDOW = xbmcgui.Window(10000)
        try:
            for i in range(channelCount, 30 + 1):
                WINDOW.clearProperty("Plexbmc.LatestChannel.%s.Path" % (i))
                WINDOW.clearProperty("Plexbmc.LatestChannel.%s.Title" % (i))
                WINDOW.clearProperty("Plexbmc.LatestChannel.%s.Thumb" % (i))
            plexbmc.printDebug("Done clearing channels")
        except:
            pass

        return

    @staticmethod
    def clearQueueShelf(queueCount=0):
        WINDOW = xbmcgui.Window(10000)

        try:
            for i in range(queueCount, 15 + 1):
                WINDOW.clearProperty("Plexbmc.Queue.%s.Path" % (i))
                WINDOW.clearProperty("Plexbmc.Queue.%s.Title" % (i))
                WINDOW.clearProperty("Plexbmc.Queue.%s.Thumb" % (i))
            plexbmc.printDebug("Done clearing Queue shelf")
        except:
            pass

        return

    @staticmethod
    def getShelfThumb(data, server, seasonThumb=0, width=400, height=400):
        '''
        Simply take a URL or path and determine how to format for images
        @ input: elementTree element, server name
        @ return formatted URL
        '''

        if seasonThumb == 1:
            thumbnail = data.get('grandparentThumb', '').split('?t')[0].encode('utf-8')

        else:
            thumbnail = data.get('thumb', '').split('?t')[0].encode('utf-8')

        if thumbnail == '':
            return plexbmc.g_thumb

        elif thumbnail[0:4] == "http":
            return thumbnail

        elif thumbnail[0] == '/':
            if plexbmc.__settings__.getSetting("fullres_thumbs") != "false":
                return 'http://' + server + thumbnail
            else:
                return plexbmc.Utility.photoTranscode(server, 'http://localhost:32400' + thumbnail, width, height)

        else:
            return plexbmc.g_thumb
