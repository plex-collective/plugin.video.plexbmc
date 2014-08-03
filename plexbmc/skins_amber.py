import random
import xbmc  # pylint: disable=F0401
import xbmcgui  # pylint: disable=F0401

from plexbmc import settings, THUMB, printDebug
import plexbmc
import plexbmc.gui
import plexbmc.servers
import plexbmc.main
import plexbmc.skins
from . import skins

def amberskin():
    # Gather some data and set the window properties
    printDebug("== ENTER: amberskin() ==", False)
    # Get the global host variable set in settings
    WINDOW = xbmcgui.Window(10000)

    sectionCount = 0
    serverCount = 0
    sharedCount = 0
    shared_flag = {}
    hide_shared = settings('hide_shared')

    server_list = plexbmc.servers.PlexServers.discoverAll()
    printDebug("Using list of " + str(len(server_list)) + " servers: " + str(server_list))

    # For each of the servers we have identified
    sections = plexbmc.gui.Sections.getAllSections(server_list)
    printDebug("Total sections: " + str(len(sections)), False)

    for section in sections:

        printDebug("=Enter amberskin section=", False)
        printDebug(str(section), False)
        printDebug("=/section=", False)

        extraData = {'fanart_image': plexbmc.gui.Media.getFanart(section, section['address']), 'thumb': THUMB}

        # Determine what we are going to do process after a link is selected by the user, based on the content we find
        path = section['path']

        if section['type'] == 'show':
            if hide_shared == "true" and section.get('owned') == '0':
                shared_flag['show'] = True
                sharedCount += 1
                continue
            window = "VideoLibrary"
            mode = plexbmc.MODE_TVSHOWS
        elif section['type'] == 'movie':
            if hide_shared == "true" and section.get('owned') == '0':
                shared_flag['movie'] = True
                sharedCount += 1
                continue
            window = "VideoLibrary"
            mode = plexbmc.MODE_MOVIES
        elif section['type'] == 'artist':
            if hide_shared == "true" and section.get('owned') == '0':
                shared_flag['artist'] = True
                sharedCount += 1
                continue
            window = "MusicFiles"
            mode = plexbmc.MODE_ARTISTS
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
            mode = plexbmc.MODE_PHOTOS

        aToken = plexbmc.servers.MyPlexServers.getAuthDetails(section)
        qToken = plexbmc.servers.MyPlexServers.getAuthDetails(section, prefix='?')

        if settings('secondary'):
            mode = plexbmc.MODE_GETCONTENT
        else:
            path = path + '/all'

        s_url = 'http://%s%s&mode=%s%s' % (section['address'], path, mode, aToken)

        # Build that listing..
        WINDOW.setProperty("plexbmc.%d.uuid" % (sectionCount), section['sectionuuid'])
        WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), section['title'])
        WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), section['serverName'])
        WINDOW.setProperty("plexbmc.%d.path" % (sectionCount),
                           "ActivateWindow(" + window + ",plugin://plugin.video.plexbmc/?url=" + s_url + ",return)")
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
        printDebug("PATH in use is: ActivateWindow(" + window + ",plugin://plugin.video.plexbmc/?url=" + s_url + ",return)")
        sectionCount += 1

    if settings('myplex_user') != '' and hide_shared == 'true' and sharedCount != 0:
        WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared Content")
        WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
        WINDOW.setProperty("plexbmc.%d.path" %
                           (sectionCount), "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode=" +
                           str(plexbmc.MODE_SHARED_ALL) +
                           ",return)")
        WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "shared")
        WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
        sectionCount += 1

    elif sharedCount != 0:

        if shared_flag.get('movie'):
            WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
            WINDOW.setProperty("plexbmc.%d.path" %
                               (sectionCount), "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode=" +
                               str(plexbmc.MODE_SHARED_MOVIES) +
                               ",return)")
            WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "shared")
            WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
            sectionCount += 1

        if shared_flag.get('show'):
            WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
            WINDOW.setProperty("plexbmc.%d.path" %
                               (sectionCount), "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode=" +
                               str(plexbmc.MODE_SHARED_SHOWS) +
                               ",return)")
            WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "shared")
            WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
            sectionCount += 1

        if shared_flag.get('artist'):
            WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
            WINDOW.setProperty("plexbmc.%d.path" %
                               (sectionCount), "ActivateWindow(MusicFiles,plugin://plugin.video.plexbmc/?url=/&mode=" +
                               str(plexbmc.MODE_SHARED_MUSIC) +
                               ",return)")
            WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "shared")
            WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
            sectionCount += 1

        if shared_flag.get('photo'):
            WINDOW.setProperty("plexbmc.%d.title" % (sectionCount), "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" % (sectionCount), "Shared")
            WINDOW.setProperty("plexbmc.%d.path" %
                               (sectionCount), "ActivateWindow(Pictures,plugin://plugin.video.plexbmc/?url=/&mode=" +
                               str(plexbmc.MODE_SHARED_PHOTOS) +
                               ",return)")
            WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "shared")
            WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
            sectionCount += 1

    else:
        pass

    # For each of the servers we have identified
    numOfServers = len(server_list)
    shelfChannel(server_list)

    for server in server_list.values():

        if server['class'] == "secondary":
            continue

        aToken = plexbmc.servers.MyPlexServers.getAuthDetails(server)
        #qToken=plexbmc.servers.MyPlexServers.getAuthDetails(server, prefix='?')

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

    if settings('myplex_user') != '':
        WINDOW.setProperty(
            "plexbmc.queue",
            "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=http://myplexqueue&mode=24,return)")
        WINDOW.setProperty("plexbmc.myplex", "1")

        # Now let's populate queue shelf items since we have MyPlex login
        if settings('homeshelf') != '3':
            printDebug("== ENTER: Queue Shelf ==", False)
            aToken = plexbmc.servers.MyPlexServers.getMyPlexToken()
            myplex_server = plexbmc.servers.MyPlexServers.getMyPlexURL('/pms/playlists/queue/all')
            root = plexbmc.etree.fromstring(myplex_server)
            server_address = plexbmc.servers.PlexServers.getMasterServer()['address']
            queue_count = 1

            for media in root:
                printDebug("Found a queue item entry: [%s]" % (media.get('title', '').encode('UTF-8'), ))
                m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&indirect=%s&t=%s" % (plexbmc.gui.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address),
                    18,
                    1,
                    aToken)
                m_thumb = plexbmc.skins.Skin.getShelfThumb(media, server_address, seasonThumb=0) + aToken

                try:
                    movie_runtime = str(int(float(media.get('duration')) / 1000 / 60))
                except:
                    movie_runtime = ""

                WINDOW.setProperty("Plexbmc.Queue.%s.Path" % queue_count, m_url)
                WINDOW.setProperty("Plexbmc.Queue.%s.Title" % queue_count, media.get('title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.Queue.%s.Year" %
                    queue_count,
                    media.get(
                        'originallyAvailableAt',
                        '').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.Queue.%s.Duration" % queue_count, movie_runtime)
                WINDOW.setProperty("Plexbmc.Queue.%s.Thumb" % queue_count, m_thumb)

                queue_count += 1

                printDebug("Building Queue item: %s" % media.get('title', 'Unknown').encode('UTF-8'))
                printDebug("Building Queue item url: %s" % m_url)
                printDebug("Building Queue item thumb: %s" % m_thumb)

            clearQueueShelf(queue_count)
    else:
        WINDOW.clearProperty("plexbmc.myplex")

    fullShelf(server_list)


def fullShelf(server_list={}):
    # pylint: disable=E1103
    # Instance of 'dict' has no 'xxx' member

    # Gather some data and set the window properties
    printDebug("== ENTER: fullShelf ==", False)

    if plexbmc.settings('homeshelf') == '3' or ((plexbmc.settings(
            'movieShelf') == "false" and plexbmc.settings('tvShelf') == "false" and plexbmc.settings('musicShelf') == "false")):
        printDebug("Disabling all shelf items")
        skins.clearShelf()
        clearOnDeckShelf()
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
        server_list = plexbmc.servers.PlexServers.discoverAll()

    if server_list == {}:
        xbmc.executebuiltin("XBMC.Notification(Unable to see any media servers,)")
        skins.clearShelf(0, 0, 0, 0)
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
            aToken = plexbmc.servers.MyPlexServers.getAuthDetails({'token': token})
            qToken = '?' + aToken

            sections = plexbmc.gui.Sections.getAllSections(server_list)

            # XXX: Unused variable 'ra_log_count'
            ra_log_count = 1

            if plexbmc.settings('homeshelf') == '0' or plexbmc.settings('homeshelf') == '2':
                '''
                    logfile = PLUGINPATH+"/_shelf_sections_.txt"
                    logfileh = open(logfile, "w")
                    logfileh.write(str(sections))
                    logfileh.close()
                    '''
                for section in sections:
                    recent_url = section.get('address') + section.get("path") + "/recentlyAdded"
                    #token = section.get('token', '')
                    tree = plexbmc.servers.PlexServers.getURL(recent_url)
                    tree = plexbmc.etree.fromstring(tree)
                    token = server_details.get('token', '')
                    '''
                        eetee = plexbmc.etree.ElementTree()
                        eetee._setroot(tree)
                        logfile = PLUGINPATH+"/RecentlyAdded"+ str(ra_log_count) + ".xml"
                        logfileh = open(logfile, "w")
                        eetee.write(logfileh)
                        logfileh.close()
                        ra_log_count += 1
                        '''
                    if tree is None:
                        printDebug("PLEXBMC -> RecentlyAdded items not found on: " + recent_url, False)
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
                                (plexbmc.settings('hide_watched_recent_items') == 'true' and int(
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
            if plexbmc.settings('homeshelf') == '1' or plexbmc.settings('homeshelf') == '2':
                for section in sections:
                    ondeck_url = section.get('address') + section.get("path") + "/onDeck"
                    #token = section.get('token', '')
                    tree = plexbmc.servers.PlexServers.getURL(ondeck_url)
                    tree = plexbmc.etree.fromstring(tree)
                    token = server_details.get('token', '')
                    '''
                        eetee = plexbmc.etree.ElementTree()
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
            printDebug("Found a recent movie entry: [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))
            if plexbmc.settings('movieShelf') == "false":
                WINDOW.clearProperty("Plexbmc.LatestMovie.1.Path")
                continue
            if plexbmc.settings('hide_watched_recent_items') == 'false' or media.get("viewCount", 0) == 0:
                m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s" % (plexbmc.gui.Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address),
                    plexbmc.MODE_PLAYSHELF,
                    randomNumber,
                    aToken)
                m_thumb = skins.Skin.getShelfThumb(media, server_address, seasonThumb=0) + aToken
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

                printDebug("Building Recent window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
                printDebug("Building Recent window url: %s" % m_url)
                printDebug("Building Recent window thumb: %s" % m_thumb)
            else:
                continue
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
            s_thumb = skins.Skin.getShelfThumb(media, server_address, seasonThumb=0) + aToken

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
        elif media.get('type', None) == "episode":
            printDebug("Found an Recent episode entry [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))

            if plexbmc.settings('tvShelf') == "false":
                WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
                continue

            s_url = "ActivateWindow(Videos, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.gui.Utility.getLinkURL(
                'http://' + server_address,
                media,
                server_address,
                season_shelf=True),
                plexbmc.MODE_TVEPISODES,
                aToken)
            s_thumb = skins.Skin.getShelfThumb(media, server_address, seasonThumb=1) + aToken

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

            printDebug("Building RecentEpisode window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
            printDebug("Building RecentEpisode window url: %s" % s_url)
            printDebug("Building RecentEpisode window thumb: %s" % s_thumb)

            recentSeasonCount += 1
    skins.clearShelf(recentMovieCount, recentSeasonCount, recentMusicCount, recentPhotoCount)

    # For each of the servers we have identified
    for index in sorted(ondeck_list):
        media = ondeck_list[index][0]
        server_address = ondeck_list[index][1]
        aToken = ondeck_list[index][2]
        qToken = ondeck_list[index][3]
        libuuid = ondeck_list[index][4]

        if media.get('type', None) == "movie":
            printDebug("Found a OnDeck movie entry: [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))
            if plexbmc.settings('movieShelf') == "false":
                WINDOW.clearProperty("Plexbmc.OnDeckMovie.1.Path")
                continue

            m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s" % (plexbmc.gui.Utility.getLinkURL(
                'http://' + server_address,
                media,
                server_address),
                plexbmc.MODE_PLAYSHELF,
                randomNumber,
                aToken)
            m_thumb = skins.Skin.getShelfThumb(media, server_address, seasonThumb=0) + aToken

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

            printDebug("Building OnDeck Movie window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
            printDebug("Building OnDeck Movie window url: %s" % m_url)
            printDebug("Building OnDeck Movie window thumb: %s" % m_thumb)

        elif media.get('type', None) == "season":
            printDebug("Found a OnDeck season entry [%s]" % (media.get('parentTitle', 'Unknown').encode('UTF-8'), ))
            if plexbmc.settings('tvShelf') == "false":
                WINDOW.clearProperty("Plexbmc.OnDeckEpisode.1.Path")
                continue

            s_url = "ActivateWindow(VideoLibrary, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (plexbmc.gui.Utility.getLinkURL(
                'http://' + server_address,
                media,
                server_address),
                plexbmc.MODE_TVEPISODES,
                aToken)
            s_thumb = skins.Skin.getShelfThumb(media, server_address, seasonThumb=0) + aToken

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

            printDebug("Building OnDeck window title: %s" % media.get('parentTitle', 'Unknown').encode('UTF-8'))
            printDebug("Building OnDeck window url: %s" % s_url)
            printDebug("Building OnDeck window thumb: %s" % s_thumb)
        elif media.get('type', None) == "episode":
            printDebug("Found an onDeck episode entry [%s]" % (media.get('title', 'Unknown').encode('UTF-8'), ))

            if plexbmc.settings('tvShelf') == "false":
                WINDOW.clearProperty("Plexbmc.OnDeckEpisode.1.Path")
                continue

            s_url = "PlayMedia(plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s)" % (plexbmc.gui.Utility.getLinkURL(
                'http://' + server_address,
                media,
                server_address),
                plexbmc.MODE_PLAYSHELF,
                randomNumber,
                aToken)
            # s_thumb="http://"+server_address+media.get('grandparentThumb','')
            s_thumb = skins.Skin.getShelfThumb(media, server_address, seasonThumb=1)

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

            printDebug("Building OnDeck window title: %s" % media.get('title', 'Unknown').encode('UTF-8'))
            printDebug("Building OnDeck window url: %s" % s_url)
            printDebug("Building OnDeck window thumb: %s" % s_thumb)

    clearOnDeckShelf(ondeckMovieCount, ondeckSeasonCount)

    if plexbmc.settings('channelShelf') == "true" or plexbmc.settings('homeshelf') != '3':
        shelfChannel(server_list)
    else:
        printDebug("Disabling channel shelf items")
        clearChannelShelf()

def clearOnDeckShelf(movieCount=0, seasonCount=0):
    # Clear out old data
    WINDOW = xbmcgui.Window(10000)
    printDebug("Clearing unused On Deck properties")

    try:
        for i in range(movieCount, 60 + 1):
            WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Path" % (i))
            WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Title" % (i))
            WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Thumb" % (i))
            WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Rating" % (i))
            WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Duration" % (i))
            WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.Year" % (i))
            WINDOW.clearProperty("Plexbmc.OnDeckMovie.%s.uuid" % (i))
        printDebug("Done clearing On Deck movies")
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
        printDebug("Done clearing On Deck tv")
    except:
        pass

    return

def shelfChannel(server_list=None):
    # pylint: disable=E1103
    # Instance of 'dict' has no 'xxx' member

    # Gather some data and set the window properties
    printDebug("== ENTER: shelfChannels() ==", False)

    if plexbmc.settings('channelShelf') == "false" or plexbmc.settings('homeshelf') == '3':
        printDebug("Disabling channel shelf")
        clearChannelShelf()
        return

    # Get the global host variable set in settings
    WINDOW = xbmcgui.Window(10000)

    channelCount = 1

    if server_list is None:
        server_list = plexbmc.servers.PlexServers.discoverAll()

    if server_list == {}:
        xbmc.executebuiltin("XBMC.Notification(Unable to see any media servers,)")
        clearChannelShelf()
        return

    for server_details in server_list.values():
        if server_details['class'] == "secondary":
            continue

        if not server_details['owned'] == '1':
            continue

        #global token
        token = server_details.get('token', '')
        aToken = plexbmc.servers.MyPlexServers.getAuthDetails({'token': token})

        # XXX: Unused variable 'qToken'
        qToken = plexbmc.servers.MyPlexServers.getAuthDetails({'token': token}, prefix='?')

        if plexbmc.settings('channelShelf') == "false" or plexbmc.settings('homeshelf') == '3':
            WINDOW.clearProperty("Plexbmc.LatestChannel.1.Path")
            return

        tree = plexbmc.gui.Utility.getXML(
            'http://' +
            server_details['server'] +
            ":" +
            server_details['port'] +
            '/channels/recentlyViewed')
        if tree is None:
            xbmc.executebuiltin("XBMC.Notification(Unable to contact server: " + server_details['serverName'] + ",)")
            clearChannelShelf(0)
            return

        # For each of the servers we have identified
        for media in tree:
            printDebug("Found a recent channel entry")
            suffix = media.get('key').split('/')[1]

            if suffix == "photos":
                mode = plexbmc.MODE_PHOTOS
                channel_window = "Pictures"
            elif suffix == "video":
                mode = plexbmc.MODE_PLEXPLUGINS
                channel_window = "VideoLibrary"
            elif suffix == "music":
                mode = plexbmc.MODE_MUSIC
                channel_window = "MusicFiles"
            else:
                mode = plexbmc.MODE_GETCONTENT
                channel_window = "VideoLibrary"

            c_url = "ActivateWindow(%s, plugin://plugin.video.plexbmc?url=%s&mode=%s%s)" % (channel_window,
                                                                                            plexbmc.gui.Utility.getLinkURL(
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

            printDebug("Building Recent window title: %s" % media.get('title', 'Unknown'))
            printDebug("Building Recent window url: %s" % c_url)
            printDebug("Building Recent window thumb: %s" % c_thumb)

    clearChannelShelf(channelCount)
    return

def clearChannelShelf(channelCount=0):
    WINDOW = xbmcgui.Window(10000)
    try:
        for i in range(channelCount, 30 + 1):
            WINDOW.clearProperty("Plexbmc.LatestChannel.%s.Path" % (i))
            WINDOW.clearProperty("Plexbmc.LatestChannel.%s.Title" % (i))
            WINDOW.clearProperty("Plexbmc.LatestChannel.%s.Thumb" % (i))
        printDebug("Done clearing channels")
    except:
        pass

    return

def clearQueueShelf(queueCount=0):
    WINDOW = xbmcgui.Window(10000)

    try:
        for i in range(queueCount, 15 + 1):
            WINDOW.clearProperty("Plexbmc.Queue.%s.Path" % (i))
            WINDOW.clearProperty("Plexbmc.Queue.%s.Title" % (i))
            WINDOW.clearProperty("Plexbmc.Queue.%s.Thumb" % (i))
        printDebug("Done clearing Queue shelf")
    except:
        pass

    return






