import urlparse
import urllib
import re
import random
import xbmc  # pylint: disable=F0401
import xbmcgui  # pylint: disable=F0401
import xbmcplugin  # pylint: disable=F0401

from plexbmc import settings, THUMB, printDebug
import plexbmc
import plexbmc.gui
import plexbmc.servers
import plexbmc.main


def enforceSkinView(mode):
    '''
    Ensure that the views are consistance across plugin usage, depending
    upon view selected by user
    @input: User view selection
    @return: view id for skin
    '''
    printDebug("== ENTER: enforceSkinView ==", False)

    if plexbmc.settings('skinoverride') == "false":
        return None

    skinname = plexbmc.settings('skinname')

    current_skin_name = xbmc.getSkinDir()

    skin_map = {'2': 'skin.confluence',
                '0': 'skin.quartz',
                '1': 'skin.quartz3',
                '3': 'skin.amber'}

    if skin_map[skinname] not in current_skin_name:
        printDebug("Do not have the correct skin [%s] selected in settings [%s] - ignoring" % (
            current_skin_name, skin_map[skinname]))
        return None

    if mode == "movie":
        printDebug("Looking for movie skin settings")
        viewname = plexbmc.settings('mo_view_%s' % skinname)

    elif mode == "tv":
        printDebug("Looking for tv skin settings")
        viewname = plexbmc.settings('tv_view_%s' % skinname)

    elif mode == "music":
        printDebug("Looking for music skin settings")
        viewname = plexbmc.settings('mu_view_%s' % skinname)

    elif mode == "episode":
        printDebug("Looking for music skin settings")
        viewname = plexbmc.settings('ep_view_%s' % skinname)

    elif mode == "season":
        printDebug("Looking for music skin settings")
        viewname = plexbmc.settings('se_view_%s' % skinname)

    else:
        viewname = "None"

    printDebug("view name is %s" % viewname)

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

    printDebug("Using skin view: %s" % skin_list[skinname][viewname])

    try:
        return skin_list[skinname][viewname]
    except:
        print "PleXBMC -> skin name or view name error"
        return None

def skin(server_list=None, skin_type=None):
    # Gather some data and set the window properties
    printDebug("== ENTER: skin() ==", False)
    # Get the global host variable set in settings
    WINDOW = xbmcgui.Window(10000)

    sectionCount = 0
    serverCount = 0

    # XXX: Unused variable 'sharedCount'
    sharedCount = 0
    shared_flag = {}
    hide_shared = plexbmc.settings('hide_shared')

    if server_list is None:
        server_list = plexbmc.servers.PlexServers.discoverAll()

    # For each of the servers we have identified
    for section in plexbmc.servers.Sections.getAllSections(server_list):
        extraData = {
            'fanart_image': plexbmc.gui.Media.getFanart(
                section, section['address']), 'thumb': plexbmc.gui.Media.getFanart(
                section, section['address'], False)}

        # Determine what we are going to do process after a link is
        # selected by the user, based on the content we find
        path = section['path']

        if section['type'] == 'show':
            if hide_shared == "true" and section.get('owned') == '0':
                shared_flag['show'] = True
                continue
            window = "VideoLibrary"
            mode = plexbmc.MODE_TVSHOWS
        if section['type'] == 'movie':
            if hide_shared == "true" and section.get('owned') == '0':
                shared_flag['movie'] = True
                continue
            window = "VideoLibrary"
            mode = plexbmc.MODE_MOVIES
        if section['type'] == 'artist':
            if hide_shared == "true" and section.get('owned') == '0':
                shared_flag['artist'] = True
                continue
            window = "MusicFiles"
            mode = plexbmc.MODE_ARTISTS
        if section['type'] == 'photo':
            if hide_shared == "true" and section.get('owned') == '0':
                shared_flag['photo'] = True
                continue
            window = "Pictures"
            mode = plexbmc.MODE_PHOTOS

        aToken = plexbmc.servers.MyPlexServers.getAuthDetails(section)
        qToken = plexbmc.servers.MyPlexServers.getAuthDetails(section, prefix='?')

        if settings('secondary'):
            mode = plexbmc.MODE_GETCONTENT
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

        printDebug("Building window properties index [" + str(sectionCount) + "] which is [" + section['title'] + "]")
        printDebug(
            "PATH in use is: ActivateWindow(" +
            window +
            ",plugin://plugin.video.plexbmc/?url=" +
            s_url +
            ",return)")
        sectionCount += 1

    if skin_type == "nocat":
        WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
        WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
        WINDOW.setProperty("plexbmc.%d.path" %
                           (sectionCount), "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode=" +
                           str(plexbmc.MODE_SHARED_ALL) +
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
                               str(plexbmc.MODE_SHARED_MOVIES) +
                               ",return)")
            WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "movie")
            WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
            sectionCount += 1

        if shared_flag.get('show'):
            WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
            WINDOW.setProperty("plexbmc.%d.path" %
                               (sectionCount), "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode=" +
                               str(plexbmc.MODE_SHARED_SHOWS) +
                               ",return)")
            WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "show")
            WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
            sectionCount += 1

        if shared_flag.get('artist'):
            WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
            WINDOW.setProperty("plexbmc.%d.path" %
                               (sectionCount), "ActivateWindow(MusicFiles,plugin://plugin.video.plexbmc/?url=/&mode=" +
                               str(plexbmc.MODE_SHARED_MUSIC) +
                               ",return)")
            WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "artist")
            WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
            sectionCount += 1

        if shared_flag.get('photo'):
            WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
            WINDOW.setProperty("plexbmc.%d.path" %
                               (sectionCount), "ActivateWindow(Pictures,plugin://plugin.video.plexbmc/?url=/&mode=" +
                               str(plexbmc.MODE_SHARED_PHOTOS) +
                               ",return)")
            WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "photo")
            WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
            sectionCount += 1

    # For each of the servers we have identified
    numOfServers = len(server_list)
    for server in server_list.values():
        if server['class'] == "secondary":
            continue

        aToken = plexbmc.servers.MyPlexServers.getAuthDetails(server)
        qToken = plexbmc.servers.MyPlexServers.getAuthDetails(server, prefix='?')

        if settings('channelview'):
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

        printDebug("Name mapping is :" + server['serverName'])

        serverCount += 1

    # Clear out old data
    try:
        printDebug(
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

    printDebug("Total number of skin sections is [" + str(sectionCount) + "]")
    printDebug("Total number of servers is [" + str(numOfServers) + "]")
    WINDOW.setProperty("plexbmc.sectionCount", str(sectionCount))
    WINDOW.setProperty("plexbmc.numServers", str(numOfServers))
    if plexbmc.settings('myplex_user') != '':
        WINDOW.setProperty(
            "plexbmc.queue",
            "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=http://myplexqueue&mode=24,return)")
        WINDOW.setProperty("plexbmc.myplex", "1")
    else:
        WINDOW.clearProperty("plexbmc.myplex")

    return


def shelf(server_list=None):
    # pylint: disable=E1103
    # Instance of 'dict' has no 'xxx' member

    # Gather some data and set the window properties
    printDebug("== ENTER: shelf() ==", False)

    if (plexbmc.settings('movieShelf') == "false" and plexbmc.settings('tvShelf') ==
            "false" and plexbmc.settings('musicShelf') == "false") or plexbmc.settings('homeshelf') == '3':
        printDebug("Disabling all shelf items")
        clearShelf()
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
        server_list = plexbmc.servers.PlexServers.discoverAll()

    if server_list == {}:
        xbmc.executebuiltin("XBMC.Notification(Unable to see any media servers,)")
        clearShelf(0, 0, 0)
        return

    if plexbmc.settings('homeshelf') == '0' or plexbmc.settings('homeshelf') == '2':
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
        aToken = plexbmc.servers.MyPlexServers.getAuthDetails({'token': token})
        qToken = plexbmc.servers.MyPlexServers.getAuthDetails({'token': token}, prefix='?')

        tree = plexbmc.gui.Utility.getXML('http://' + server_details['server'] + ":" + server_details['port'] + endpoint)
        if tree is None:
            xbmc.executebuiltin("XBMC.Notification(Unable to contact server: " + server_details['serverName'] + ",)")
            clearShelf()
            return

        for eachitem in tree:
            if direction:
                added_list[int(eachitem.get('addedAt', 0))] = (
                    eachitem, server_details['server'] + ":" + server_details['port'], aToken, qToken)
            else:
                added_list[full_count] = (eachitem, server_details['server'] + ":" + server_details['port'], aToken, qToken)
                full_count += 1

    library_filter = plexbmc.settings('libraryfilter')
    acceptable_level = plexbmc.settings('contentFilter')

    # For each of the servers we have identified
    for index in sorted(added_list, reverse=direction):
        media = added_list[index][0]
        server_address = added_list[index][1]
        aToken = added_list[index][2]
        qToken = added_list[index][3]

        if media.get('type', None) == "movie":
            printDebug("Found a recent movie entry: [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))

            if plexbmc.settings('movieShelf') == "false":
                WINDOW.clearProperty("Plexbmc.LatestMovie.1.Path")
                continue
            if not plexbmc.gui.Utility.displayContent(acceptable_level, media.get('contentRating')):
                continue
            if media.get('librarySectionID') == library_filter:
                printDebug("SKIPPING: Library Filter match: %s = %s " % (library_filter, media.get('librarySectionID')))
                continue

            m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s" % (plexbmc.gui.Utility.getLinkURL(
                'http://' + server_address,
                media,
                server_address),
                plexbmc.MODE_PLAYSHELF,
                randomNumber,
                aToken)
            m_thumb = plexbmc.gui.Media.getThumb(media, server_address)

            WINDOW.setProperty("Plexbmc.LatestMovie.%s.Path" % movieCount, m_url)
            WINDOW.setProperty("Plexbmc.LatestMovie.%s.Title" % movieCount, media.get('title', 'Unknown').encode('UTF-8'))
            WINDOW.setProperty("Plexbmc.LatestMovie.%s.Thumb" % movieCount, m_thumb + qToken)

            movieCount += 1

            printDebug("Building Recent window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
            printDebug("Building Recent window url: %s" % m_url)
            printDebug("Building Recent window thumb: %s" % m_thumb)
        elif media.get('type', None) == "season":
            printDebug("Found a recent season entry [%s]" % (media.get('parentTitle', 'Unknown').encode('UTF-8'), ))

            if plexbmc.settings('tvShelf') == "false":
                WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
                continue

            s_url = "ActivateWindow(VideoLibrary, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.gui.Utility.getLinkURL(
                'http://' + server_address,
                media,
                server_address),
                plexbmc.MODE_TVEPISODES,
                aToken)
            s_thumb = plexbmc.gui.Media.getThumb(media, server_address)

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

            printDebug("Building Recent window title: %s" % media.get('parentTitle', 'Unknown').encode('UTF-8'))
            printDebug("Building Recent window url: %s" % s_url)
            printDebug("Building Recent window thumb: %s" % s_thumb)
        elif media.get('type') == "album":
            if plexbmc.settings('musicShelf') == "false":
                WINDOW.clearProperty("Plexbmc.LatestAlbum.1.Path")
                continue
            printDebug("Found a recent album entry")

            s_url = "ActivateWindow(MusicFiles, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.gui.Utility.getLinkURL(
                'http://' + server_address,
                media,
                server_address),
                plexbmc.MODE_TRACKS,
                aToken)
            s_thumb = plexbmc.gui.Media.getThumb(media, server_address)

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

            printDebug("Building Recent window title: %s" % media.get('parentTitle', 'Unknown').encode('UTF-8'))
            printDebug("Building Recent window url: %s" % s_url)
            printDebug("Building Recent window thumb: %s" % s_thumb)

        elif media.get('type', None) == "episode":
            printDebug("Found an onDeck episode entry [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))

            if plexbmc.settings('tvShelf') == "false":
                WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
                continue

            s_url = "PlayMedia(plugin://plugin.video.plexbmc?url=%s&mode=%s%s)" % (plexbmc.gui.Utility.getLinkURL(
                'http://' + server_address,
                media,
                server_address),
                plexbmc.MODE_PLAYSHELF,
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

            printDebug("Building Recent window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
            printDebug("Building Recent window url: %s" % s_url)
            printDebug("Building Recent window thumb: %s" % s_thumb)

    clearShelf(movieCount, seasonCount, musicCount)


def clearShelf(movieCount=0, seasonCount=0, musicCount=0, photoCount=0):
    # Clear out old data
    WINDOW = xbmcgui.Window(10000)
    printDebug("Clearing unused properties")

    try:
        for i in range(movieCount, 50 + 1):
            WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Path" % (i))
            WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Title" % (i))
            WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Year" % (i))
            WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Rating" % (i))
            WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Duration" % (i))
            WINDOW.clearProperty("Plexbmc.LatestMovie.%s.Thumb" % (i))
            WINDOW.clearProperty("Plexbmc.LatestMovie.%s.uuid" % (i))
        printDebug("Done clearing movies")
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
        printDebug("Done clearing tv")
    except:
        pass

    try:
        for i in range(musicCount, 25 + 1):
            WINDOW.clearProperty("Plexbmc.LatestAlbum.%s.Path" % (i))
            WINDOW.clearProperty("Plexbmc.LatestAlbum.%s.Title" % (i))
            WINDOW.clearProperty("Plexbmc.LatestAlbum.%s.Artist" % (i))
            WINDOW.clearProperty("Plexbmc.LatestAlbum.%s.Thumb" % (i))
        printDebug("Done clearing music")
    except:
        pass

    try:
        for i in range(photoCount, 25 + 1):
            WINDOW.clearProperty("Plexbmc.LatestPhoto.%s.Path" % (i))
            WINDOW.clearProperty("Plexbmc.LatestPhoto.%s.Title" % (i))
            WINDOW.clearProperty("Plexbmc.LatestPhoto.%s.Thumb" % (i))
        printDebug("Done clearing photos")
    except:
        pass

    return


class Skin:
    @staticmethod
    def setProperty(listitem, name, info, template=None, **kwargs):
        if isinstance(info, str):
            listitem.setProperty(name, info)
            printDebug('setProperty(%s, %s)' %(name,info), False)
        elif isinstance(info, dict):
            if kwargs:
                info.update(kwargs)
            if info and template:
                listitem.setProperty(name, template.format(info))
                printDebug('setProperty(%s, %s)' % (name, template.format(info)), False)

    @staticmethod
    def popluateLibrarySections(container_id=None, static_content=None):
        # Gather some data and set the window properties
        printDebug("== ENTER: popluateLibrarySections() ==", False)

        # Servers
        server_list = plexbmc.servers.PlexServers.discoverAll()
        printDebug("Using list of " + str(len(server_list)) + " servers: " + str(server_list))

        # Sections
        sections = plexbmc.servers.Sections.getAllSections(server_list)
        printDebug("Total sections: " + str(len(sections)), False)

        mode_map = {
            'show': ("VideoLibrary", plexbmc.MODE_TVSHOWS),
            'movie': ("VideoLibrary", plexbmc.MODE_MOVIES),
            'artist': ("MusicFiles", plexbmc.MODE_ARTISTS),
            'photo': ("Pictures", plexbmc.MODE_PHOTOS)
        }

        setProperty = Skin.setProperty
        hide_shared = plexbmc.settings('hide_shared') and settings('myplex_user')
        listitems = []

        for section in sections:
            printDebug("=Enter popluateLibrarySections section=", False)
            printDebug(str(section), False)

            if hide_shared and section.get('owned') == '0':
                continue

            extraData = {'fanart_image': plexbmc.gui.Media.getFanart(section, section['address']), 'thumb': THUMB}

            # Determine what we are going to do process after a link is
            # selected by the user, based on the content we find
            window, mode = mode_map.get(section['type'], ("Videos", ""))

            path = section['path']
            aToken = plexbmc.servers.MyPlexServers.getAuthDetails(section)

            print 'secondary: %s' % settings('secondary')
            if settings('secondary'):
                mode = plexbmc.MODE_GETCONTENT
            else:
                path = path + '/all'

            s_url = 'http://%s%s&mode=%s%s' % (section['address'], path, mode, aToken)
            path = "plugin://plugin.video.plexbmc/?url={0}".format(s_url)
            base_url = 'plugin://plugin.video.plexbmc/?url=http://'
            command_template = "ActivateWindow(%s,return)"
            base_template = "{0[window]},{0[base_url]}{0[address]}{0[path]}{0[section]}"
            partial_template = command_template % base_template
            full_template = command_template % (base_template + "&mode={0[mode]}{0[token]}")

            # XXX: on deck tests!
            recent_url = section.get('address') + section.get("path") + "/recentlyAdded"
            recent_url = plexbmc.servers.PlexServers.normalizeURL(recent_url, server_list, section)
            ondeck_url = section.get('address') + section.get("path") + "/onDeck"
            ondeck_url = plexbmc.servers.PlexServers.normalizeURL(ondeck_url, server_list, section)

            info = {}
            info['label'] = section['title']
            info['label2'] = section['serverName']
            info['iconImage'] = None
            info['thumbnailImage'] = None
            info['path'] = path

            # Create listitem object from info dictionary
            listitem = xbmcgui.ListItem(**info)


            info['window'] = window
            info['base_url'] = base_url
            info['address'] = section['address']
            info['path'] = section['path']
            info['mode'] = mode
            info['token'] = aToken

            setProperty(listitem, 'uuid', section['sectionuuid'])
            setProperty(listitem, 'title', section['title'])
            setProperty(listitem, 'subtitle', section['serverName'])
            setProperty(listitem, 'type', section['type'])
            setProperty(listitem, 'mode', str(mode))
            setProperty(listitem, 'token', aToken)
            setProperty(listitem, 'window', window)
            setProperty(listitem, 'path', section['path'])
            #setProperty(listitem, 'partial', info, partial_template, section='')
            setProperty(listitem, 'partial_path', info, partial_template, section='')
            setProperty(listitem, 'search', info, full_template, section='/search?type=1')

            # Dunno if amber needs these paths, so I will create new ones for auto-pupulate
            setProperty(listitem, 'recent', info, full_template, section='/recentlyAdded')
            setProperty(listitem, 'viewed', info, full_template, section='/recentlyViewed')
            setProperty(listitem, 'ondeck', info, full_template, section='/onDeck')
            setProperty(listitem, 'released', info, full_template, section='/newest')
            # New Deck
            #listitem.setProperty('Plex', recent_url)
            listitem.setProperty('DeckRecentlyAdded', recent_url)
            listitem.setProperty('DeckOnDeck', ondeck_url)

            setProperty(listitem, 'all', info, full_template, section='/all')

            listitem.setArt(extraData['fanart_image'])
            #listitem.setIconImage(extraData['thumb'])
            #listitem.setThumbnailImage(extraData['thumb'])
            listitem.setIconImage(extraData['fanart_image'])
            listitem.setThumbnailImage(extraData['fanart_image'])

            if section['type'] == "artist":
                setProperty(listitem, 'artist', info, full_template, section='/albums')
                setProperty(listitem, 'search', info, full_template, section='/search?type=10')
            elif section['type'] == "photo":
                setProperty(listitem, 'year', info, full_template, section='/year')
            elif section['type'] == "show":
                setProperty(listitem, 'search', info, full_template, section='/search?type=4')
            #elif section['type'] == "movie":
            #    setProperty(listitem, 'search', info, full_template, section='/search?type=1')

            if section.get('owned') == '1':
                setProperty(listitem, 'shared', "false")
            else:
                setProperty(listitem, 'shared', "true")

            setProperty(listitem, 'node.target', window)
            #listitem.setProperty('node.target_url', path2)

            listitems.append((path, listitem, True))

        # Shared Sections
        if hide_shared:
            #path="plugin://plugin.video.plexbmc?content=sections&append=300"
            listitem = xbmcgui.ListItem(
                label="Shared Content",
                label2='Shared',
                iconImage=None,
                thumbnailImage=None,
                path="plugin://plugin.video.plexbmc/?url=/&mode=%s" % plexbmc.MODE_SHARED_ALL
            )
            setProperty(listitem, 'shared', "true")
            setProperty(listitem, 'type', "shared")
            setProperty(listitem, 'node.target', "VideoLibrary")
            listitems.append((info['path'], listitem, True))

        # Channels
        listitem = xbmcgui.ListItem(
            label=plexbmc.__localize__(30098),
            label2='channels',
            iconImage=None,
            thumbnailImage="special://skin/backgrounds/Channels.jpg",
            path="plugin://plugin.video.plexbmc/?mode=22&url=http://online%2fsystem%2fplugins%2fall",
        )
        setProperty(listitem, 'type', "channels")
        setProperty(listitem, 'node.target', "Videos")
        listitems.append((info['path'], listitem, True))

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

    if settings('myplex_user') != '' and hide_shared == 'true' and sharedCount != 0:
        WINDOW.setProperty("plexbmc.%d.title"    % (sectionCount) , "Shared Content")
        WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount) , "Shared")
        WINDOW.setProperty("plexbmc.%d.path"     % (sectionCount) , "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode="+str(MODE_SHARED_ALL)+",return)")
        WINDOW.setProperty("plexbmc.%d.type"     % (sectionCount) , "shared")
        WINDOW.setProperty("plexbmc.%d.shared"     % (sectionCount) , "true")
        sectionCount += 1

    elif sharedCount != 0:

        if shared_flag.get('movie'):
            WINDOW.setProperty("plexbmc.%d.title"    % (sectionCount) , "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount) , "Shared")
            WINDOW.setProperty("plexbmc.%d.path"     % (sectionCount) , "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode="+str(MODE_SHARED_MOVIES)+",return)")
            WINDOW.setProperty("plexbmc.%d.type"     % (sectionCount) , "shared")
            WINDOW.setProperty("plexbmc.%d.shared"     % (sectionCount) , "true")
            sectionCount += 1

        if shared_flag.get('show'):
            WINDOW.setProperty("plexbmc.%d.title"    % (sectionCount) , "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount) , "Shared")
            WINDOW.setProperty("plexbmc.%d.path"     % (sectionCount) , "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode="+str(MODE_SHARED_SHOWS)+",return)")
            WINDOW.setProperty("plexbmc.%d.type"     % (sectionCount) , "shared")
            WINDOW.setProperty("plexbmc.%d.shared"     % (sectionCount) , "true")
            sectionCount += 1

        if shared_flag.get('artist'):
            WINDOW.setProperty("plexbmc.%d.title"    % (sectionCount) , "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount) , "Shared")
            WINDOW.setProperty("plexbmc.%d.path"     % (sectionCount) , "ActivateWindow(MusicFiles,plugin://plugin.video.plexbmc/?url=/&mode="+str(MODE_SHARED_MUSIC)+",return)")
            WINDOW.setProperty("plexbmc.%d.type"     % (sectionCount) , "shared")
            WINDOW.setProperty("plexbmc.%d.shared"     % (sectionCount) , "true")
            sectionCount += 1

        if shared_flag.get('photo'):
            WINDOW.setProperty("plexbmc.%d.title"    % (sectionCount) , "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount) , "Shared")
            WINDOW.setProperty("plexbmc.%d.path"     % (sectionCount) , "ActivateWindow(Pictures,plugin://plugin.video.plexbmc/?url=/&mode="+str(MODE_SHARED_PHOTOS)+",return)")
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

        if settings('channelview'):
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

    if settings('myplex_user') != '':
        WINDOW.setProperty("plexbmc.queue" , "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=http://myplexqueue&mode=24,return)")
        WINDOW.setProperty("plexbmc.myplex",  "1" )

        #Now let's populate queue shelf items since we have MyPlex login
        if settings('homeshelf') != '3':
            printDebug("== ENTER: Queue Shelf ==", False)
            aToken = plexbmc.servers.MyPlexServers.getMyPlexToken()
            myplex_server = plexbmc.servers.MyPlexServers.getMyPlexURL('/pms/playlists/queue/all')
            root = plexbmc.etree.fromstring(myplex_server)
            server_address = plexbmc.servers.PlexServers.getMasterServer()['address']
            queue_count = 1

            for media in root:
                printDebug("Found a queue item entry: [%s]" % (media.get('title', '').encode('UTF-8') , ))
                m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&indirect=%s&t=%s" % (plexbmc.gui.Utility.getLinkURL('http://'+server_address, media, server_address), 18, 1, aToken)
                m_thumb = Skin.getShelfThumb(media, server_address, seasonThumb=0)+aToken

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

            Skin.clearQueueShelf(queue_count)

    else:
        WINDOW.clearProperty("plexbmc.myplex")

    #XXX: Skin.fullShelf(server_list)
    '''
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
            printDebug('container_id: %s' % str(container_id))
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
                    home_list.setStaticContent(listitem)
                    #testitems.append(listitem)
                # home_list.setStaticContent(items=testitems)
                #home_list.addItems(items=testitems)

                # home_list.addItems(testitems)
                # home_list.setVisible(True)
            except Exception:
                printDebug('Unable to getControl(%s)' % str(container_id))
            #xbmcplugin.addDirectoryItems(300, listitems)
            # xbmcplugin.endOfDirectory(handle=container_id)
        else:
            xbmcplugin.addDirectoryItems(plexbmc.main.PleXBMC.getHandle(), listitems)
            if static_content:
                xbmcplugin.addDirectoryItems(plexbmc.main.PleXBMC.getHandle(), static_content)
            xbmcplugin.endOfDirectory(handle=plexbmc.main.PleXBMC.getHandle())
            #xbmcplugin.endOfDirectory(pluginhandle, succeeded=True, updateListing=False, cacheToDisc=False)


    @staticmethod
    def createStaticListitems(static_xml_text, ids):
        setProperty = Skin.setProperty

        elem = plexbmc.utils.convertTextToXML(static_xml_text)
        if elem is None:
            return []

        for content_id in ids:
            # Find the content node for specified id
            content = elem.find("./content/[@id='%s']" % content_id)
            if content is None:
                return []

            # Now grab all the item nodes
            items = content.findall('item')
            if items is None:
                return []

            print content_id

        '''
        <item id="10" description="Settings">
            <visible>!Skin.HasSetting(QuitMenu_Show_Settings)</visible>
            <label>$LOCALIZE[5]</label>
            <thumb fallback="special://skin/backgrounds/Settings.jpg">$INFO[Skin.String(Settings.Background)]</thumb>
            <onclick>ActivateWindow(Settings)</onclick>
        </item>
            label=plexbmc.__localize__(30098),
            path="plugin://plugin.video.plexbmc/?mode=22&url=http://online%2fsystem%2fplugins%2fall",
        '''
        # XXX: TEST

        listitems = []
        listitem = xbmcgui.ListItem(
            label='$LOCALIZE[5]',
            label2=None,
            iconImage=None,
            thumbnailImage="special://skin/backgrounds/Channels.jpg",
            path=None,
        )
        setProperty(listitem, 'node.target', "Settings")
        #listitems.append((info['path'], listitem, True))
        listitems.append(('', listitem, True))

        return listitems


    @staticmethod
    def getShelfThumb(data, server, seasonThumb=False, width=400, height=400):
        '''
        Simply take a URL or path and determine how to format for images
        @ input: elementTree element, server name
        @ return formatted URL
        '''
        if seasonThumb:
            #thumb = data.get('grandparentThumb', '').split('?t')[0].encode('utf-8')
            thumb = data.get('grandparentThumb', '').encode('utf-8')
        else:
            #thumb = data.get('thumb', '').split('?t')[0].encode('utf-8')
            thumb = data.get('thumb', '').encode('utf-8')

        if not thumb:
            return THUMB

        parts = getURLParts(thumb)
        if parts.scheme in ["http", "https"]:
            return thumb

        elif not parts.scheme and not parts.netloc:
            if not plexbmc.settings("fullres_thumbs"):
                return updateURLPath(server, thumb)
            else:
                # FIXME:  should more than likely point to master server
                return plexbmc.gui.Utility.photoTranscode(server, 'http://localhost:32400' + thumb, width, height)
        else:
            return THUMB


def getURLParts(url):
    return urlparse.urlparse(url)


def fixURLParts(url, scheme=None):
    parts = getURLParts(url)

    if parts.scheme and parts.netloc and scheme is None:
        return url, parts
    elif scheme is None:
        # If scheme does not exist, guess it
        scheme = guessURLScheme(url)

    if scheme and (not parts.scheme or not parts.netloc):
        url = scheme + '://' + url
    else:
        parts = list(urlparse.urlsplit(url))
        parts[0] = scheme
        url = urlparse.urlunsplit(parts)

    return url, getURLParts(url)


def guessURLScheme(url):
    '''
    Take out best guess at figuring out the scheme since it was not provided
    '''
    parts = urlparse.urlparse(url)
    if parts.scheme and parts.netloc:
        return part.schema

    pattern = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
    match = re.search(pattern, url)

    if match.group('port') in ['443', '32443']:
        return 'https'
    elif match.group('host') in [plexbmc.MYPLEX_SERVER]:
        return 'https'
    elif match.group('port') in ['', '80', '8080', '32400']:
        return 'http'
    else:
        #XXX:  FIXME:  Gotta determine if its relative!
        return 'http'


def updateURLToken(url, token=None):
    if token is None:
        return url

    parts = urlparse.urlsplit(url)
    query = plexbmc.main.parseQueryString(parts.query)
    query.update({plexbmc.TOKEN: token})

    parts = list(parts)
    parts[3] = urllib.urlencode(query, doseq=True)
    return urlparse.urlunsplit(parts)


def updateURLPath(url, new_path):
    '''
    Change the path of an existing URL.  Keeps the scheme
    network address and token (if any) in place to avoid
    server lookups
    @ input: (str) url - current full url
    @ input: (str) new_path - new path (/path/to/whatever')
    '''
    url, parts = fixURLParts(url)
    parts = list(urlparse.urlsplit(url))

    new_path_parts = urlparse.urlsplit(new_path)
    # Relative urls sometime show up in scheme, so if they do we are set to just
    # copy the new_url, otherwise used the parsed path (which would not be
    # avaiable if the relative uls ended up in scheme field
    if new_path_parts.scheme and new_path_parts.scheme not in ['http', 'https']:
        parts[2] = new_path
    else:
        parts[2] = new_path_parts.path
    return urlparse.urlunsplit(parts)


def deckOnDeck(section_path):
    deck(section_path)


def deckRecentlyAdded(section_path):
    deck(section_path)


def deck(section_path):
    # pylint: disable=E1103
    # Instance of 'dict' has no 'xxx' member

    # Gather some data and set the window properties
    printDebug("== ENTER: deck (%s) ==" % section_path, False)

    #if plexbmc.settings('homeshelf') == '3' or ((plexbmc.settings(
    #        'movieShelf') == "false" and plexbmc.settings('tvShelf') == "false" and plexbmc.settings('musicShelf') == "false")):
    #    printDebug("Disabling all shelf items")
    #    return

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

    randomNumber = str(random.randint(1000000000, 9999999999))

    # XXX:
    # TAKE care of this in section that creates menu section items
    # IE: dont give the URL to recently added if it is unable to use
    #if not server_details['owned'] == '1':
    #    return

    content = plexbmc.servers.PlexServers.getURL(section_path)
    if not content:
        return
    tree = plexbmc.utils.convertTextToXML(content)
    if tree is None:
        printDebug("PLEXBMC -> RecentlyAdded items not found on: " + section_path, False)
        return

    # If we do not get an UUID, I believe the section is empty; or wrong section
    libraryuuid = tree.get("librarySectionUUID", '')

    ep_helper = {}  # helper season counter
    ra_item_count = 1

    listitems = []
    for media in tree:
    #for eachitem in tree:
        # if ra_item_count > 15:
            # break
        # if eachitem.get("type", "") == "episode":
            # # season identifier
            # key = int(eachitem.get("parentRatingKey"))
            # if key in ep_helper or (
                # (plexbmc.settings('hide_watched_recent_items') == 'true' and int( eachitem.get( "viewCount", 0)) > 0)):
                # pass
            # else:
                # recent_list[full_count] = (eachitem, section.get('address'), aToken, qToken, libraryuuid)
                # # use seasons as dict key so we can check
                # ep_helper[key] = key
                # full_count += 1
                # ra_item_count += 1
        # else:
            # recent_list[full_count] = (eachitem, section.get('address'), aToken, qToken, libraryuuid)
            # full_count += 1
            # ra_item_count += 1
    # full_count = 0

    # For each of the servers we have identified
    # for index in recent_list:
        # media = recent_list[index][0]
        # server_address = recent_list[index][1]
        # aToken = recent_list[index][2]
        # qToken = recent_list[index][3]
        # libuuid = recent_list[index][4]

        #s_url = "ActivateWindow(Videos, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.gui.Utility.getLinkURL(
        #    'http://' + server_address, media, server_address, season_shelf=True),
        #    plexbmc.MODE_TVEPISODES, aToken)
        #s_thumb = skins.Skin.getShelfThumb(media, server_address, seasonThumb=1) + aToken

        # path ============================================================================================================
        season = True if media.get('type', None) == 'episode' else False

        parts = getURLParts(section_path)
        query = plexbmc.main.parseQueryString(parts.query)
        token = query.get(plexbmc.TOKEN, None)
        parts = list(parts)
        parts[2] = ''
        parts[3] = ''
        parts[4] = ''
        parts[5] = ''
        server = urlparse.urlunparse(parts)

        # FIXME:  Lets be sure this wont break... dont forget about token!
        url = "plugin://plugin.video.plexbmc?url=%s&mode=%s" % (plexbmc.gui.Utility.getLinkURL(
            server, media, server, season),
            plexbmc.MODE_TVEPISODES)
        if token:
            url = updateURLToken(url, token)

        thumb = Skin.getShelfThumb(media, section_path, seasonThumb=season)  #+ aToken
        # =================================================================================================================

        # XXX
        # TODO:  Make ListItem contain ALL properties for server and section (json it) so we have it here
        #
        if media.get('type', None) == "movie":
            printDebug("Found a recent movie entry: [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))
            #if plexbmc.settings('movieShelf') == "false":
            #    WINDOW.clearProperty("Plexbmc.LatestMovie.1.Path")
            #    continue
            # XXX: FIXME:  check all plexbmc setting that are looking for booleans cause we dont return text anymore!
            #if plexbmc.settings('hide_watched_recent_items') == 'false' or media.get("viewCount", 0) == 0:
            #if not plexbmc.settings('hide_watched_recent_items') or media.get("viewCount", 0) == 0:

            #m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s" % (plexbmc.gui.Utility.getLinkURL(
            #    'http://' + server_address,
            #    media,
            #    server_address),
            #    plexbmc.MODE_PLAYSHELF,
            #    randomNumber,
            #    aToken)


            if media.get('duration') > 0:
               #movie_runtime = media.get('duration', '0')
                movie_runtime = str(int(float(media.get('duration')) / 1000 / 60))
            else:
                movie_runtime = ""
            if media.get('rating') > 0:
                movie_rating = str(round(float(media.get('rating')), 1))
            else:
                movie_rating = ''

            listitem = xbmcgui.ListItem(
                label=media.get('title', 'Unknown').encode('UTF-8'),
                label2=None,
                iconImage=None,
                thumbnailImage=thumb,
                path=url,
            )
            listitem.setProperty('uuid', libraryuuid.encode('UTF-8'))
            listitem.setProperty('Title', media.get( 'title', 'Unknown').encode('UTF-8'))
            listitem.setProperty('Year',  media.get('year', '').encode('UTF-8'))
            listitem.setProperty('Rating', movie_rating)
            listitem.setProperty('Duration', movie_runtime)
            listitem.setProperty('Plot', media.get('summary', '').encode('UTF-8'))

            m_genre = []
            for child in media:
                if child.tag == "Genre":
                    m_genre.append(child.get('tag'))
                else:
                    continue
            #WINDOW.setProperty("Plexbmc.LatestMovie.%s.Genre" % recentMovieCount, ", ".join(m_genre).encode('UTF-8'))
            listitem.setProperty('Genre', ", ".join(m_genre).encode('UTF-8'))

            #recentMovieCount += 1
            #printDebug("Building Recent window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
            #printDebug("Building Recent window url: %s" % m_url)
            #printDebug("Building Recent window thumb: %s" % m_thumb)

            listitem.setProperty('node.target', "VideoLibrary")
            listitems.append((url, listitem, True))

        elif media.get('type', None) == "episode":
            printDebug("Found an Recent episode entry [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))

            #if plexbmc.settings('tvShelf') == "false":
            #    WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
            #    continue

            #s_url = "ActivateWindow(Videos, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.gui.Utility.getLinkURL(
            #    'http://' + server_address, media, server_address, season_shelf=True),
            #    plexbmc.MODE_TVEPISODES, aToken)
            #s_thumb = skins.Skin.getShelfThumb(media, server_address, seasonThumb=1) + aToken

            #WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Path" % recentSeasonCount, s_url)
            #WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeTitle" % recentSeasonCount, media.get('title', '').encode('utf-8'))
            #WINDOW.setProperty( "Plexbmc.LatestEpisode.%s.EpisodeNumber" % recentSeasonCount, media.get( 'index', '').encode('utf-8'))
            #WINDOW.setProperty( "Plexbmc.LatestEpisode.%s.EpisodeSeason" % recentSeasonCount, media.get( 'parentIndex', '').encode('UTF-8') + '.' + media.get( 'index', 'Unknown').encode('UTF-8'))
            #WINDOW.setProperty( "Plexbmc.LatestEpisode.%s.EpisodeSeasonNumber" % recentSeasonCount, media.get( 'parentIndex', '').encode('UTF-8'))
            #WINDOW.setProperty( "Plexbmc.LatestEpisode.%s.ShowTitle" % recentSeasonCount, media.get( 'grandparentTitle', '').encode('UTF-8'))
            #WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Thumb" % recentSeasonCount, s_thumb)
            #WINDOW.setProperty("Plexbmc.LatestEpisode.%s.uuid" % recentSeasonCount, libuuid.encode('utf-8'))

            listitem = xbmcgui.ListItem(
                label=media.get('title', 'Unknown').encode('UTF-8'),
                label2=None,
                iconImage=None,
                thumbnailImage=thumb,
                path=url,
            )
            listitem.setProperty('uuid', libraryuuid.encode('UTF-8'))
            listitem.setProperty('EpisodeTitle', 'title')
            listitem.setProperty('EpisodeSeason', media.get( 'title', 'Unknown').encode('UTF-8'))
            listitem.setProperty('EpisodeNumber', media.get( 'title', 'index').encode('UTF-8'))
            listitem.setProperty('EpisodeSeasonNumber', media.get( 'parentIndex', 'Unknown').encode('UTF-8'))
            listitem.setProperty('ShowTitle', media.get( 'grandparentTitle', 'Unknown').encode('UTF-8'))

            listitem.setProperty('node.target', "Videos")
            listitems.append((url, listitem, True))


            #printDebug("Building RecentEpisode window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
            #printDebug("Building RecentEpisode window url: %s" % s_url)
            #printDebug("Building RecentEpisode window thumb: %s" % s_thumb)
            #recentSeasonCount += 1

        elif media.get('type', None) == "season":
            printDebug("Found a recent season entry [%s]" % (media.get('parentTitle', 'Unknown').encode('UTF-8'), ))

            #if plexbmc.settings('tvShelf') == "false":
            #    WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
            #    continue

            #s_url = "ActivateWindow(VideoLibrary, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.gui.Utility.getLinkURL(
            #    'http://' + server_address,
            #    media,
            #    server_address),
            #    plexbmc.MODE_TVEPISODES,
            #    aToken)

            #WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Path" % recentSeasonCount, s_url)
            #WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeTitle" % recentSeasonCount, '')
            #WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeSeason" % recentSeasonCount, media.get('title', '').encode('UTF-8'))
            #WINDOW.setProperty("Plexbmc.LatestEpisode.%s.ShowTitle" % recentSeasonCount, media.get( 'parentTitle', 'Unknown').encode('UTF-8'))
            #WINDOW.setProperty("Plexbmc.LatestEpisode.%s.Thumb" % recentSeasonCount, s_thumb)
            #WINDOW.setProperty( "Plexbmc.LatestEpisode.%s.uuid" % recentSeasonCount, media.get( 'librarySectionUUID', '').encode('UTF-8'))

            listitem = xbmcgui.ListItem(
                label=media.get('title', 'Unknown').encode('UTF-8'),
                label2=None,
                iconImage=None,
                thumbnailImage=thumb,
                path=url,
            )
            listitem.setProperty('uuid', libraryuuid.encode('UTF-8'))
            listitem.setProperty('EpisodeSeason', media.get( 'title', 'Unknown').encode('UTF-8'))
            listitem.setProperty('EpisodeTitle', '')
            listitem.setProperty('ShowTitle', media.get( 'parentTitle', 'Unknown').encode('UTF-8'))

            listitem.setProperty('node.target', "VideoLibrary")
            listitems.append((url, listitem, True))

            #recentSeasonCount += 1
            #printDebug("Building Recent window title: %s" % media.get('parentTitle', 'Unknown').encode('UTF-8'))
            #printDebug("Building Recent window url: %s" % s_url)
            #printDebug("Building Recent window thumb: %s" % s_thumb)


    xbmcplugin.addDirectoryItems(plexbmc.main.PleXBMC.getHandle(), listitems)
    xbmcplugin.endOfDirectory(handle=plexbmc.main.PleXBMC.getHandle())

    '''
        elif media.get('type') == "album":
            if plexbmc.settings('musicShelf') == "false":
                WINDOW.clearProperty("Plexbmc.LatestAlbum.1.Path")
                continue
            printDebug("Found a recent album entry")

            s_url = "ActivateWindow(MusicFiles, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.gui.Utility.getLinkURL(
                'http://' + server_address,
                media,
                server_address),
                plexbmc.MODE_TRACKS,
                aToken)
            s_thumb = skins.Skin.getShelfThumb(media, server_address, seasonThumb=0) + aToken

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

            printDebug("Building Recent window title: %s" % media.get('parentTitle', 'Unknown').encode('UTF-8'))
            printDebug("Building Recent window url: %s" % s_url)
            printDebug("Building Recent window thumb: %s" % s_thumb)

        elif media.get('type') == "photo":
            printDebug("Found a recent photo entry: [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))

            p_url = "ActivateWindow(Pictures, plugin://plugin.video.plexbmc/?url=http://%s%s&mode=%s%s,return" % (
                server_address, "/recentlyAdded", plexbmc.MODE_PHOTOS, aToken)
            p_thumb = skins.Skin.getShelfThumb(media, server_address, seasonThumb=0) + aToken

            WINDOW.setProperty("Plexbmc.LatestPhoto.%s.Path" % recentPhotoCount, p_url)
            WINDOW.setProperty("Plexbmc.LatestPhoto.%s.Title" % recentPhotoCount, media.get('title', 'Unknown').encode('UTF-8'))
            WINDOW.setProperty("Plexbmc.LatestPhoto.%s.Thumb" % recentPhotoCount, p_thumb)

            recentPhotoCount += 1

            printDebug("Building Recent photo window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
            printDebug("Building Recent photo window url: %s" % p_url)
            printDebug("Building Recent photo window thumb: %s" % p_thumb)
        '''

def jason_test():
    listitems = list()
    #self.section = 'Hey there'
    xbmcplugin.setContent(plexbmc.main.PleXBMC.getHandle(), 'movies')
    #self.parse_movies('recentmovies', 32005, listitems)
    path = "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=http://10.0.0.10:32400/library/sections/5,return)"
    path2 = "plugin://plugin.video.plexbmc/?url=http://10.0.0.10:32400/library/sections/5"

    print 'Entering jason_test'
    # XXX:
    #liz = xbmcgui.ListItem('JASON+: '+self.section)
    liz = xbmcgui.ListItem('JASON')
    liz.setInfo(type="Video", infoLabels={"Title": 'JASON WAS HERE'})
    liz.setPath(path)
    # liz.setIconImage('DefaultVideoCover.png')
    # liz.setArt('DefaultVideoCover.png')
    # liz.setThumbnailImage('DefaultVideoCover.png')
    # liz.setIconImage('DefaultVideoCover.png')
    #liz.setProperty("fanart_image", 'DefaultVideoCover.png')
    #liz.setProperty('ItemType', 'On Deck')
    # False??? should maybe be set back to Fasle since not a folder
    listitems.append((path, liz, True))
    xbmcplugin.addDirectoryItems(plexbmc.main.PleXBMC.getHandle(), listitems)
    xbmcplugin.endOfDirectory(handle=plexbmc.main.PleXBMC.getHandle())
    print 'Finish jason_test'  # So this is where we really start the plugin.


