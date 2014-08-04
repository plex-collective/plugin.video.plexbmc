import base64
import datetime
import requests
import httplib
import socket
import time
import urllib
import xbmc
import xbmcgui
import xbmcplugin

from plexbmc import settings, DEBUG, PLEXBMC_VERSION, PLEXBMC_PLATFORM, CACHE_DATA, printDebug
import plexbmc.cache as cache
import plexbmc
import plexbmc.gui
import plexbmc.main


class PlexServers:
    _streaming = plexbmc.__settings__.getSetting('streaming')
    _quality = None
    _capability = None
    _session_id = None
    _transcode = False
    _transcode_format = None

    @classmethod
    def setCapability(cls, value):
        cls._capability = value
    @classmethod
    def getCapability(cls):
        return cls._capability

    @classmethod
    def setQuality(cls, value):
        cls._quality = value
    @classmethod
    def getQuality(cls):
        return cls._quality

    @classmethod
    def setStreaming(cls, value):
        cls._streaming = value
    @classmethod
    def getStreaming(cls):
        return cls._streaming

    @classmethod
    def setTranscodeFormat(cls, value):
        cls._transcode_format = value
    @classmethod
    def getTranscodeFormat(cls):
        return cls._transcode_format

    @classmethod
    def setTranscode(cls, value):
        cls._transcode = value
    @classmethod
    def getTranscode(cls):
        return cls._transcode

    @classmethod
    def setSessionID(cls, value):
        cls._session_id = value
    @classmethod
    def getSessionID(cls):
        return cls._session_id

    @staticmethod
    def discoverAll():
        '''
        Take the users settings and add the required master servers
        to the server list.  These are the devices which will be queried
        for complete library listings.  There are 3 types:
            local server - from IP configuration
            bonjour server - from a bonjour lookup
            myplex server - from myplex configuration
        @input: None
        @return: deduplicate(das_servers)
        '''
        printDebug("== ENTER: discoverAllServers ==", False)

        das_servers = {}
        das_server_index = 0

        discovery = plexbmc.__settings__.getSetting('discovery')

        if discovery == "1":
            printDebug(
                "PleXBMC -> local GDM discovery setting enabled.", False)
            try:
                import plexgdm
                printDebug("Attempting GDM lookup on multicast")
                if DEBUG:
                    GDM_debug = 3
                else:
                    GDM_debug = 0

                gdm_cache_file = CACHE_DATA + "gdm.server.cache"
                gdm_cache_ok = False
                gdm_cache_ok, gdm_server_name = cache.check(gdm_cache_file)

                if not gdm_cache_ok:
                    gdm_client = plexgdm.plexgdm(GDM_debug)
                    gdm_client.discover()
                    gdm_server_name = gdm_client.getServerList()
                    cache.write(gdm_cache_file, gdm_server_name)

                if (gdm_cache_ok or gdm_client.discovery_complete) and gdm_server_name:
                    printDebug("GDM discovery completed")
                    for device in gdm_server_name:
                        das_servers[das_server_index] = device
                        das_server_index = das_server_index + 1
                else:
                    printDebug("GDM was not able to discover any servers")
            except:
                print "PleXBMC -> GDM Issue."

        # Set to Disabled
        else:
            das_host = plexbmc.__settings__.getSetting('ipaddress')
            das_port = plexbmc.__settings__.getSetting('port')

            if not das_host or das_host == "<none>":
                das_host = None
            elif not das_port:
                printDebug(
                    "PleXBMC -> No port defined.  Using default of " + plexbmc.DEFAULT_PORT, False)
                das_port = plexbmc.DEFAULT_PORT

            printDebug(
                "PleXBMC -> Settings hostname and port: %s : %s" % (das_host, das_port), False)

            if das_host is not None:
                local_server = PlexServers.getLocalServers(das_host, das_port)
                if local_server:
                    das_servers[das_server_index] = local_server
                    das_server_index = das_server_index + 1

        if plexbmc.__settings__.getSetting('myplex_user') != "":
            printDebug("PleXBMC -> Adding myplex as a server location", False)

            myplex_cache_file = CACHE_DATA + "myplex.server.cache"
            success, das_myplex = cache.check(myplex_cache_file)

            if not success:
                das_myplex = MyPlexServers.getServers()
                cache.write(myplex_cache_file, das_myplex)

            if das_myplex:
                printDebug("MyPlex discovery completed")
                for device in das_myplex:
                    das_servers[das_server_index] = device
                    das_server_index = das_server_index + 1

        # Remove Cloud Sync servers, since they cause problems
        # for das_server_index,das_server in das_plexbmc.servers.items():
        # Cloud sync "servers" don't have a version key in the dictionary
        #     if 'version' not in das_server:
        #         del das_servers[das_server_index]

        printDebug("PleXBMC -> serverList is " + str(das_servers), False)
        return PlexServers.deduplicate(das_servers)

    @staticmethod
    def getLocalServers(ip_address="localhost", port=32400):
        '''
        Connect to the defined local server (either direct or via bonjour discovery)
        and get a list of all known plexbmc.servers.
        @input: nothing
        @return: a list of servers (as Dict)
        '''
        printDebug("== ENTER: getLocalServers ==", False)

        url_path = "/"
        html = PlexServers.getURL(ip_address + ":" + port + url_path)

        if html is False:
            return []

        server = plexbmc.etree.fromstring(html)

        return {'serverName': server.attrib['friendlyName'].encode('utf-8'),
                'scheme': server.attrib['scheme'],
                'server': ip_address,
                'port': port,
                'discovery': 'local',
                'token': None,
                'uuid': server.attrib['machineIdentifier'],
                'owned': '1',
                'master': 1,
                'class': ''}

                #'updated': '1407084668',
                #'uuid': '34e28b63eb6ba30864e99f279458dff0201a4c62',
                #'serverName': 'Haswell',
                #'owned': '1',
                #'server': '10.0.0.10',
                #'port': '32400',
                #'version': '0.9.9.13.525-197d5ed',
                #'role': 'master',
                #'master': 1,
                #'content-type': 'plex/media-server',
                #'class': None,
                #'discovery': 'auto'}


    @staticmethod
    def normalizeURL(url, servers, section):
        '''
        Adds scheme and token if needed to url
        '''
        scheme = servers.get(section['uuid'], {}).get('scheme', 'http')
        scheme = scheme + '://'
        token = section.get('token', '')
        token = '' if not token else '?X-Plex-Token=' + token
        return scheme + url + token


    @staticmethod
    def getURL(url, suppress=True, url_type="GET", popup=0):
        printDebug("== ENTER: getURL ==", False)

        url = url if "://" in url else "http://" + url
        headers = MyPlexServers.getAuthDetails({'token': plexbmc.main.PleXBMC.getToken()}, False)

        printDebug("url = " + url)
        printDebug("headers = " + str(headers))

        try:
            if url_type == 'GET':
                response = requests.get(url, headers=headers)
            else:
                response = requests.post(url, headers=headers)

            if response.status_code == requests.codes.ok:
                content = response.content
                printDebug("====== XML returned =======")
                printDebug(content, False)
                printDebug("====== XML finished ======")
                return content

            elif response.status_code in [301, 302]:
                return response.headers.get('Location', '')

            elif response.status_code == 401:
                error = "Authentication error.  Check user/password."
                print "PleXBMC -> %s" % error
                if not suppress:
                    if not popup:
                        xbmc.executebuiltin("XBMC.Notification(Server Authentication Error,)")
                    else:
                        xbmcgui.Dialog().ok("PleXBMC", "Authentication Required or Incorrect")

            elif response.status_code == 401:
                error = "XML/web page does not exist."
                print "PleXBMC -> %s" % error
                if not suppress:
                    if not popup:
                        xbmc.executebuiltin("XBMC.Notification(Web/XML Page Does Not Exist,)")
                    else:
                        xbmcgui.Dialog().ok("PleXBMC", "Web/XML Page Does Not Exist")

            elif response.status_code >= 402:
                error = "HTTP response error: " + str(response.status_code) + " " + str(response.reason)
                print error
                if not suppress:
                    if not popup:
                        xbmc.executebuiltin("XBMC.Notification(URL error: " + str(response.reason) + ",)")
                    else:
                        xbmcgui.Dialog().ok("Error", error)

        except requests.ConnectionError as msg:
            error = "Connection Error.  A network problem has occured (DNS failure, refused connection, etc)\nError: %s" % msg
            print "PleXBMC %s" % error
            if not suppress:
                if not popup:
                    xbmc.executebuiltin("XBMC.Notification(\"PleXBMC\": Connection Error,)")
                else:
                    xbmcgui.Dialog().ok("PleXBMC", "Connecton Error")
        except requests.Timeout as msg:
            error = "Connection Timeout.\nError: %s" % msg
            print "PleXBMC %s" % error
            if not suppress:
                if not popup:
                    xbmc.executebuiltin("XBMC.Notification(\"PleXBMC\": Connection Timeout,)")
                else:
                    xbmcgui.Dialog().ok("PleXBMC", "Connecton Timeout")
        except requests.TooManyRedirects as msg:
            error = "Too Many Redirects\nError: %s" % msg
            print "PleXBMC %s" % error
            if not suppress:
                if not popup:
                    xbmc.executebuiltin("XBMC.Notification(\"PleXBMC\": Too Many Redirects,)")
                else:
                    xbmcgui.Dialog().ok("PleXBMC", "Too Many Redirects")
        except requests.HTTPError as msg:
            error = "Invalid HTTP response\nError: %s" % msg
            print "PleXBMC %s" % error
            if not suppress:
                if not popup:
                    xbmc.executebuiltin("XBMC.Notification(\"PleXBMC\": Invalid HTTP Response,)")
                else:
                    xbmcgui.Dialog().ok("PleXBMC", "Invalid HTTP Response")

        return ''


    @staticmethod
    def setMasterServer():
        printDebug("== ENTER: setmasterserver ==", False)

        servers = PlexServers.getMasterServer(True)
        printDebug(str(servers))

        current_master = plexbmc.__settings__.getSetting('masterServer')

        displayList = []
        for address in servers:
            found_server = address['name']
            if found_server == current_master:
                found_server = found_server + "*"
            displayList.append(found_server)

        audioScreen = xbmcgui.Dialog()
        result = audioScreen.select('Select master server', displayList)
        if result == -1:
            return False

        printDebug("Setting master server to: %s" % (servers[result]['name'],))
        plexbmc.__settings__.setSetting('masterServer', servers[result]['name'])
        return

    @staticmethod
    def getTranscodeSettings(override=False):
        printDebug("== ENTER: gettranscodesettings ==", False)

        PlexServers.setTranscode(plexbmc.__settings__.getSetting('transcode'))

        if override is True:
            printDebug("Transcode override.  Will play media with addon transcoding settings")
            PlexServers.setTranscode("true")

        if PlexServers.getTranscode() == "true":
            # If transcode is set, ignore the stream setting for file and smb:
            PlexServers.setStreaming("1")
            printDebug("We are set to Transcode, overriding stream selection")
            PlexServers.setTranscodeFormat("m3u8")

            PlexServers.setQuality(str(int(plexbmc.__settings__.getSetting('quality')) + 3))
            printDebug("Transcode format is " + PlexServers.getTranscodeFormat())
            printDebug("Transcode quality is " + PlexServers.getQuality())

            baseCapability = "http-live-streaming,http-mp4-streaming,http-streaming-video,http-streaming-video-1080p,http-mp4-video,http-mp4-video-1080p;videoDecoders=h264{profile:high&resolution:1080&level:51};"

            audio_output = plexbmc.__settings__.getSetting("audiotype")
            if audio_output == "0":
                audio = "mp3,aac{bitrate:160000}"
            elif audio_output == "1":
                audio = "ac3{channels:6}"
            elif audio_output == "2":
                audio = "dts{channels:6}"

            PlexServers.setCapability(
                "X-Plex-Client-Capabilities=" +
                urllib.quote_plus(
                    "protocols=" +
                    baseCapability +
                    "audioDecoders=" +
                    audio))
            printDebug("Plex Client Capability = " + PlexServers.getCapability())

            import uuid
            PlexServers.setSessionID((uuid.uuid4()))

    @staticmethod
    def getMasterServer(all=False):
        printDebug("== ENTER: getmasterserver ==", False)

        possibleServers = []
        current_master = plexbmc.__settings__.getSetting('masterServer')
        for serverData in PlexServers.discoverAll().values():
            printDebug(str(serverData))
            if serverData['master'] == 1:
                possibleServers.append({'address': serverData['server'] + ":" + serverData['port'],
                                        'discovery': serverData['discovery'],
                                        'name': serverData['serverName'],
                                        'token': serverData.get('token')})
        printDebug("Possible master servers are " + str(possibleServers))

        if all:
            return possibleServers

        if len(possibleServers) > 1:
            preferred = "local"
            for serverData in possibleServers:
                if serverData['name'] == current_master:
                    printDebug("Returning current master")
                    return serverData
                if preferred == "any":
                    printDebug("Returning 'any'")
                    return serverData
                else:
                    if serverData['discovery'] == preferred:
                        printDebug("Returning local")
                        return serverData
        elif len(possibleServers) == 0:
            return

        return possibleServers[0]

    @staticmethod
    def transcode(id, url, identifier=None):
        printDebug("== ENTER: transcode ==", False)

        server = plexbmc.gui.Utility.getServerFromURL(url)

        # Check for myplex user, which we need to alter to a master server
        if 'plexapp.com' in url:
            server = PlexServers.getMasterServer()

        printDebug("Using preferred transcoding server: " + server)
        printDebug("incoming URL is: %s" % url)

        transcode_request = "/video/:/transcode/segmented/start.m3u8"
        transcode_settings = {'3g': 0,
                              'offset': 0,
                              'quality': PlexServers.getQuality(),
                              'session': PlexServers.getSessionID(),
                              'identifier': identifier,
                              'httpCookie': "",
                              'userAgent': "",
                              'ratingKey': id,
                              'subtitleSize': plexbmc.__settings__.getSetting('subSize').split('.')[0],
                              'audioBoost': plexbmc.__settings__.getSetting('audioSize').split('.')[0],
                              'key': ""}

        if identifier:
            transcode_target = url.split('url=')[1]
            transcode_settings['webkit'] = 1
        else:
            transcode_settings['identifier'] = "com.plexapp.plugins.library"
            transcode_settings['key'] = urllib.quote_plus("http://%s/library/metadata/%s" % (server, id))
            transcode_target = urllib.quote_plus("http://127.0.0.1:32400" + "/" + "/".join(url.split('/')[3:]))
            printDebug("filestream URL is: %s" % transcode_target)

        transcode_request = "%s?url=%s" % (transcode_request, transcode_target)

        for argument, value in transcode_settings.items():
            transcode_request = "%s&%s=%s" % (
                transcode_request, argument, value)

        printDebug("new transcode request is: %s" % transcode_request)

        now = str(int(round(time.time(), 0)))

        msg = transcode_request + "@" + now
        printDebug("Message to hash is " + msg)

        # These are the DEV API keys - may need to change them on release
        publicKey = "KQMIY6GATPC63AIMC4R2"
        privateKey = base64.decodestring(
            "k3U6GLkZOoNIoSgjDshPErvqMIFdE0xMTx8kgsrhnC0=")

        import hmac
        import hashlib
        hash = hmac.new(privateKey, msg, digestmod=hashlib.sha256)

        printDebug("HMAC after hash is " + hash.hexdigest())

        # Encode the binary hash in base64 for transmission
        token = base64.b64encode(hash.digest())

        # Send as part of URL to avoid the case sensitive header issue.
        fullURL = "http://" + server + transcode_request + "&X-Plex-Access-Key=" + publicKey + "&X-Plex-Access-Time=" + \
            str(now) + "&X-Plex-Access-Code=" + urllib.quote_plus(token) + "&" + PlexServers.getCapability()

        printDebug("Transcoded media location URL " + fullURL)

        return fullURL

    @staticmethod
    def pluginTranscodeMonitor(sessionID, server):
        printDebug("== ENTER: pluginTranscodeMonitor ==", False)

        # Logic may appear backward, but this does allow for a failed start to be detected
        # First while loop waiting for start

        if plexbmc.__settings__.getSetting('monitoroff') == "true":
            return

        count = 0
        while not xbmc.Player().isPlaying():
            printDebug("Not playing yet...sleep for 2")
            count = count + 2
            if count >= 40:
                # Waited 20 seconds and still no movie playing - assume it
                # isn't going to..
                return
            else:
                time.sleep(2)

        while xbmc.Player().isPlaying():
            printDebug("Waiting for playback to finish")
            time.sleep(4)

        printDebug("Playback Stopped")
        printDebug("Stopping PMS transcode job with session: " + sessionID)
        stopURL = 'http://' + server + '/video/:/transcode/segmented/stop?session=' + sessionID

        # XXX: Unused variable 'html'
        html = PlexServers.getURL(stopURL)
        return

    @staticmethod
    def monitorPlayback(id, server):
        printDebug("== ENTER: monitorPlayback ==", False)

        if plexbmc.__settings__.getSetting('monitoroff') == "true":
            return

        if len(server.split(':')) == 1:
            server = server

        # XXX:  Unused variable 'monitorCount'
        monitorCount = 0
        progress = 0
        complete = 0
        # Whilst the file is playing back
        while xbmc.Player().isPlaying():
            # Get the current playback time

            currentTime = int(xbmc.Player().getTime())
            totalTime = int(xbmc.Player().getTotalTime())
            try:
                progress = int((float(currentTime) / float(totalTime)) * 100)
            except:
                progress = 0

            if currentTime < 30:
                printDebug("Less that 30 seconds, will not set resume")

            # If we are less than 95% completem, store resume time
            elif progress < 95:
                printDebug("Movies played time: %s secs of %s @ %s%%" %
                                   (currentTime, totalTime, progress))
                PlexServers.getURL("http://" +
                                   server +
                                   "/:/progress?key=" +
                                   id +
                                   "&identifier=com.plexapp.plugins.library&time=" +
                                   str(currentTime *
                                       1000), suppress=True)
                complete = 0

            # Otherwise, mark as watched
            else:
                if complete == 0:
                    printDebug("Movie marked as watched. Over 95% complete")
                    PlexServers.getURL(
                        "http://" +
                        server +
                        "/:/scrobble?key=" +
                        id +
                        "&identifier=com.plexapp.plugins.library",
                        suppress=True)
                    complete = 1

            xbmc.sleep(5000)

        # If we get this far, playback has stopped
        printDebug("Playback Stopped")

        if PlexServers.getSessionID() is not None:
            printDebug(
                "Stopping PMS transcode job with session " + PlexServers.getSessionID())
            stopURL = 'http://' + server + '/video/:/transcode/segmented/stop?session=' + PlexServers.getSessionID()

            # XXX:  Unused variable 'html'
            html = PlexServers.getURL(stopURL)

        return

    @staticmethod
    def deduplicate(server_list):
        '''
        Return list of all media sections configured
        within PleXBMC
        @input: None
        @Return: unique list of media servers
        '''
        printDebug("== ENTER: deduplicateServers ==", False)

        # Merge the servers so we get access to scheme, etc
        servers = {}
        for server in server_list.values():
            print server
            if not server['uuid'] in servers.keys():
                servers.setdefault(server['uuid'], {})
                servers[server['uuid']].update(server)
                servers[server['uuid']]['merged'] = False
            else:
                if server['discovery'] in ["auto", "local"]:
                    servers[server['uuid']].update(server)
                servers[server['uuid']]['merged'] = True
        printDebug("Unique server List: " + str(servers))
        return servers


class MyPlexServers:
    @staticmethod
    def getServers():
        '''
        Connect to the myplex service and get a list of all known
        plexbmc.servers.
        @input: nothing
        @return: a list of servers (as Dict)
        '''

        printDebug("== ENTER: getMyPlexServers ==", False)

        tempServers = []
        url_path = "/pms/servers"
        all_servers = MyPlexServers.getMyPlexURL(url_path)

        if all_servers is False:
            return {}

        servers = plexbmc.etree.fromstring(all_servers)
        count = 0
        for server in servers:
            #data = dict(server.items())

            if server.get('owned', None) == "1":
                owned = '1'
                if count == 0:
                    master = 1
                    count = - 1
                accessToken = MyPlexServers.getMyPlexToken()
            else:
                owned = '0'
                master = 0
                accessToken = server.get('accessToken')

            tempServers.append({'serverName': server.get('name').encode('utf-8'),
                                'scheme': server.get('scheme'),
                                'server': server.get('address'),
                                'port': server.get('port'),
                                'discovery': 'myplex',
                                'token': accessToken,
                                'uuid': server.get('machineIdentifier'),
                                'owned': owned,
                                'master': master,
                                'class': ""})

        return tempServers

    @staticmethod
    def getAuthDetails(details, url_format=True, prefix="&"):
        '''
        Takes the token and creates the required arguments to allow
        authentication.  This is really just a formatting tools
        @input: token as dict, style of output [opt] and prefix style [opt]
        @return: header string or header dict
        '''
        token = details.get('token', None)

        if url_format:
            if token:
                return prefix + "X-Plex-Token=" + str(token)
            else:
                return ""
        else:
            if token:
                return {'X-Plex-Token': token}
            else:
                return {}

    @staticmethod
    def getMyPlexURL(url_path, renew=False, suppress=True):
        '''
        Connect to the my.plexapp.com service and get an XML pages
        A separate function is required as interfacing into myplex
        is slightly different than getting a standard URL
        @input: url to get, whether we need a new token, whether to display on screen err
        @return: an xml page as string or false
        '''
        printDebug("== ENTER: getMyPlexURL ==", False)
        #printDebug("url = " + plexbmc.MYPLEX_SERVER + url_path)
        printDebug("url = " + plexbmc.MYPLEX_SERVER + url_path + "?X-Plex-Token=" + MyPlexServers.getMyPlexToken(renew))

        try:
            conn = httplib.HTTPSConnection(plexbmc.MYPLEX_SERVER, timeout=5)
            conn.request("GET", url_path + "?X-Plex-Token=" + MyPlexServers.getMyPlexToken(renew))
            data = conn.getresponse()
            if (int(data.status) == 401) and not renew:
                try:
                    conn.close()
                except:
                    pass
                return MyPlexServers.getMyPlexURL(url_path, True)

            if int(data.status) >= 400:
                error = "HTTP response error: " + str(data.status) + " " + str(data.reason)
                if suppress is False:
                    xbmcgui.Dialog().ok("Error", error)
                print error
                try:
                    conn.close()
                except:
                    pass
                return False
            # FIXME: 'type' is not defined
            #        and it also seems a HEAD request is never sent from here
            #        so lets just comment it out for now
            #elif int(data.status) == 301 and type == "HEAD":
            #    try:
            #        conn.close()
            #    except:
            #        pass
            #    return str(data.status) + "@" + data.getheader('Location')
            else:
                link = data.read()
                printDebug("====== XML returned =======")
                printDebug(link, False)
                printDebug("====== XML finished ======")
        except socket.gaierror:
            error = 'Unable to lookup host: ' + plexbmc.MYPLEX_SERVER + "\nCheck host name is correct"
            if suppress is False:
                xbmcgui.Dialog().ok("Error", error)
            print error
            return False
        except socket.error as msg:
            error = "Unable to connect to " + plexbmc.MYPLEX_SERVER + "\nReason: " + str(msg)
            if suppress is False:
                xbmcgui.Dialog().ok("Error", error)
            print error
            return False
        else:
            try:
                conn.close()
            except:
                pass

        if link:
            return link
        else:
            return False

    @staticmethod
    def getMyPlexToken(renew=False):
        '''
        Get the myplex token.  If the user ID stored with the token
        does not match the current userid, then get new token.  This stops old token
        being used if plex ID is changed. If token is unavailable, then get a new one
        @input: whether to get new token
        @return: myplex token
        '''
        printDebug("== ENTER: getMyPlexToken ==", False)

        try:
            user, token = (plexbmc.__settings__.getSetting('myplex_token')).split('|')
        except:
            token = None

        if (token is None) or (renew) or (user != plexbmc.__settings__.getSetting('myplex_user')):
            token = MyPlexServers.getNewMyPlexToken()

        printDebug(
            "Using token: " + str(token) + "[Renew: " + str(renew) + "]")
        return token

    @staticmethod
    def getNewMyPlexToken(suppress=True, title="Error"):
        '''
        Get a new myplex token from myplex API
        @input: nothing
        @return: myplex token
        '''
        printDebug("== ENTER: getNewMyPlexToken ==", False)

        printDebug("Getting New token")
        myplex_username = plexbmc.__settings__.getSetting('myplex_user')
        myplex_password = plexbmc.__settings__.getSetting('myplex_pass')

        if not myplex_username or not myplex_password:
            printDebug("No myplex details in config..")
            return ""

        base64string = base64.encodestring(
            '%s:%s' % (myplex_username, myplex_password)).replace('\n', '')
        txdata = ""
        token = False

        myplex_headers = {'X-Plex-Platform': "XBMC",
                          'X-Plex-Platform-Version': "12.00/Frodo",
                          'X-Plex-Provides': "player",
                          'X-Plex-Product': "PleXBMC",
                          'X-Plex-Version': PLEXBMC_VERSION,
                          'X-Plex-Device': PLEXBMC_PLATFORM,
                          'X-Plex-Client-Identifier': "PleXBMC",
                          'Authorization': "Basic %s" % base64string}

        try:
            conn = httplib.HTTPSConnection(plexbmc.MYPLEX_SERVER)
            conn.request("POST", "/users/sign_in.xml", txdata, myplex_headers)
            data = conn.getresponse()

            if int(data.status) == 201:
                link = data.read()
                printDebug("====== XML returned =======")

                try:
                    token = plexbmc.etree.fromstring(link).findtext(
                        'authentication-token')
                    plexbmc.__settings__.setSetting('myplex_token', myplex_username + "|" + token)
                except:
                    printDebug(link)

                printDebug("====== XML finished ======")
            else:
                error = "HTTP response error: " + str(data.status) + " " + str(data.reason)
                if suppress is False:
                    xbmcgui.Dialog().ok(title, error)
                print error
                return ""
        except socket.gaierror:
            error = 'Unable to lookup host: MyPlex' + "\nCheck host name is correct"
            if suppress is False:
                xbmcgui.Dialog().ok(title, error)
            print error
            return ""
        except socket.error as msg:
            error = "Unable to connect to MyPlex" + "\nReason: " + str(msg)
            if suppress is False:
                xbmcgui.Dialog().ok(title, error)
            print error
            return ""

        return token

    @staticmethod
    def getAuthTokenFromURL(url):
        if "X-Plex-Token=" in url:
            return url.split('X-Plex-Token=')[1]
        else:
            return ""


class Media:
    @staticmethod
    def setAudioSubtitles(stream):
        '''
        Take the collected audio/sub stream data and apply to the media
        If we do not have any subs then we switch them off
        '''
        printDebug("== ENTER: setAudioSubtitles ==", False)

        # If we have decided not to collect any sub data then do not set subs
        if stream['contents'] == "type":
            printDebug("No audio or subtitle streams to process.")

            # If we have decided to force off all subs, then turn them off now
            # and return
            if settings('streamControl') == plexbmc.SUB_AUDIO_NEVER_SHOW:
                xbmc.Player().showSubtitles(False)
                printDebug("All subs disabled")

            return True

        # Set the AUDIO component
        if settings('streamControl') == plexbmc.SUB_AUDIO_PLEX_CONTROL:
            printDebug("Attempting to set Audio Stream")

            audio = stream['audio']

            if stream['audioCount'] == 1:
                printDebug(
                    "Only one audio stream present - will leave as default")

            elif audio:
                printDebug("Attempting to use selected language setting: %s" % audio.get(
                    'language', audio.get('languageCode', 'Unknown')).encode('utf8'))
                printDebug(
                    "Found preferred language at index " + str(stream['audioOffset']))
                try:
                    xbmc.Player().setAudioStream(stream['audioOffset'])
                    printDebug("Audio set")
                except:
                    printDebug(
                        "Error setting audio, will use embedded default stream")

        # Set the SUBTITLE component
        if plexbmc.settings('streamControl') == plexbmc.SUB_AUDIO_PLEX_CONTROL:
            printDebug("Attempting to set preferred subtitle Stream", True)
            subtitle = stream['subtitle']
            if subtitle:
                printDebug("Found preferred subtitle stream")
                try:
                    xbmc.Player().showSubtitles(False)
                    if subtitle.get('key'):
                        xbmc.Player().setSubtitles(
                            subtitle['key'] + plexbmc.servers.MyPlexServers.getAuthDetails({'token': plexbmc.main.PleXBMC.getToken()}, prefix="?"))
                    else:
                        printDebug(
                            "Enabling embedded subtitles at index %s" % stream['subOffset'])
                        xbmc.Player().setSubtitleStream(
                            int(stream['subOffset']))

                    xbmc.Player().showSubtitles(True)
                    return True
                except:
                    printDebug("Error setting subtitle")

            else:
                printDebug("No preferred subtitles to set")
                xbmc.Player().showSubtitles(False)

        return False

    @staticmethod
    def getAudioSubtitlesMedia(server, tree, full=False):
        '''
        Cycle through the Parts sections to find all "selected" audio and subtitle streams
        If a stream is marked as selected=1 then we will record it in the dict
        Any that are not, are ignored as we do not need to set them
        We also record the media locations for playback decision later on
        '''
        printDebug("== ENTER: getAudioSubtitlesMedia ==", False)
        printDebug("Gather media stream info")

        parts = []
        partsCount = 0
        subtitle = {}
        subCount = 0
        audio = {}
        audioCount = 0
        media = {}
        subOffset = -1
        audioOffset = -1
        selectedSubOffset = -1
        selectedAudioOffset = -1
        full_data = {}
        contents = "type"
        media_type = "unknown"
        extra = {}

        timings = tree.find('Video')
        if timings is not None:
            media_type = "video"
        else:
            timings = tree.find('Track')
            if timings:
                media_type = "music"
            else:
                timings = tree.find('Photo')
                if timings:
                    media_type = "picture"
                else:
                    printDebug("No Video data found")
                    return {}

        media['viewOffset'] = timings.get('viewOffset', 0)
        media['duration'] = timings.get('duration', 12 * 60 * 60)

        if full:
            if media_type == "video":
                full_data = {'plot': timings.get('summary', '').encode('utf-8'),
                             'title': timings.get('title', 'Unknown').encode('utf-8'),
                             'sorttitle': timings.get('titleSort', timings.get('title', 'Unknown')).encode('utf-8'),
                             'rating': float(timings.get('rating', 0)),
                             'studio': timings.get('studio', '').encode('utf-8'),
                             'mpaa': timings.get('contentRating', '').encode('utf-8'),
                             'year': int(timings.get('year', 0)),
                             'tagline': timings.get('tagline', ''),
                             'thumbnailImage': plexbmc.gui.Media.getThumb(timings, server)}

                if timings.get('type') == "episode":
                    full_data['episode'] = int(timings.get('index', 0))
                    full_data['aired'] = timings.get(
                        'originallyAvailableAt', '')
                    full_data['tvshowtitle'] = timings.get(
                        'grandparentTitle', tree.get('grandparentTitle', '')).encode('utf-8')
                    full_data['season'] = int(
                        timings.get('parentIndex', tree.get('parentIndex', 0)))

            elif media_type == "music":

                full_data = {
                    'TrackNumber': int(
                        timings.get(
                            'index',
                            0)),
                    'title': str(
                        timings.get(
                            'index',
                            0)).zfill(2) +
                    ". " +
                    timings.get(
                        'title',
                        'Unknown').encode('utf-8'),
                    'rating': float(
                            timings.get(
                                'rating',
                                0)),
                    'album': timings.get(
                        'parentTitle',
                        tree.get(
                            'parentTitle',
                            '')).encode('utf-8'),
                    'artist': timings.get(
                        'grandparentTitle',
                        tree.get(
                            'grandparentTitle',
                            '')).encode('utf-8'),
                    'duration': int(
                        timings.get(
                            'duration',
                            0)) /
                    1000,
                    'thumbnailImage': plexbmc.gui.Media.getThumb(timings, server)}

                extra['album'] = timings.get('parentKey')
                extra['index'] = timings.get('index')

        details = timings.findall('Media')

        media_details_list = []
        for media_details in details:

            resolution = ""
            try:
                if media_details.get('videoResolution') == "sd":
                    resolution = "SD"
                elif int(media_details.get('videoResolution', 0)) >= 1080:
                    resolution = "HD 1080"
                elif int(media_details.get('videoResolution', 0)) >= 720:
                    resolution = "HD 720"
                elif int(media_details.get('videoResolution', 0)) < 720:
                    resolution = "SD"
            except:
                pass

            media_details_temp = {'bitrate': round(float(media_details.get('bitrate', 0)) / 1000, 1),
                                  'videoResolution': resolution,
                                  'container': media_details.get('container', 'unknown')}

            options = media_details.findall('Part')

            # Get the media locations (file and web) for later on
            for stuff in options:

                try:
                    bits = stuff.get('key'), stuff.get('file')
                    parts.append(bits)
                    media_details_list.append(media_details_temp)
                    partsCount += 1
                except:
                    pass

        # if we are deciding internally or forcing an external subs file, then
        # collect the data
        if media_type == "video" and settings('streamControl') == plexbmc.SUB_AUDIO_PLEX_CONTROL:

            contents = "all"
            tags = tree.getiterator('Stream')

            for bits in tags:
                stream = dict(bits.items())

                # Audio Streams
                if stream['streamType'] == '2':
                    audioCount += 1
                    audioOffset += 1
                    if stream.get('selected') == "1":
                        printDebug(
                            "Found preferred audio id: " + str(stream['id']))
                        audio = stream
                        selectedAudioOffset = audioOffset

                # Subtitle Streams
                elif stream['streamType'] == '3':

                    if subOffset == -1:
                        subOffset = int(stream.get('index', -1))
                    elif stream.get('index', -1) > 0 and stream.get('index', -1) < subOffset:
                        subOffset = int(stream.get('index', -1))

                    if stream.get('selected') == "1":
                        printDebug(
                            "Found preferred subtitles id : " + str(stream['id']))
                        subCount += 1
                        subtitle = stream
                        if stream.get('key'):
                            subtitle['key'] = 'http://' + server + stream['key']
                        else:
                            selectedSubOffset = int(
                                stream.get('index')) - subOffset

        else:
            printDebug("Stream selection is set OFF")

        streamData = {'contents': contents,  # What type of data we are holding
                      'audio': audio,  # Audio data held in a dict
                      'audioCount': audioCount,  # Number of audio streams
                      # Subtitle data (embedded) held as a dict
                      'subtitle': subtitle,
                      'subCount': subCount,  # Number of subtitle streams
                      'parts': parts,  # The differet media locations
                      'partsCount': partsCount,  # Number of media locations
                      'media': media,  # Resume/duration data for media
                      # Bitrate, resolution and container for each part
                      'details': media_details_list,
                      # Stream index for selected subs
                      'subOffset': selectedSubOffset,
                      # STream index for select audio
                      'audioOffset': selectedAudioOffset,
                      # Full metadata extract if requested
                      'full_data': full_data,
                      'type': media_type,  # Type of metadata
                      'extra': extra}  # Extra data

        printDebug(str(streamData))
        return streamData

    @staticmethod
    def playPlaylist(server, data):
        printDebug("== ENTER: playPlaylist ==", False)
        printDebug("Creating new playlist")
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        playlist.clear()

        tree = plexbmc.gui.Utility.getXML(
            server + data['extra'].get('album') + "/children")
        if tree is None:
            return

        TrackTags = tree.findall('Track')
        for track in TrackTags:
            printDebug("Adding playlist item")
            url, item = plexbmc.gui.GUI.trackTag(server, tree, track, listing=False)
            liz = xbmcgui.ListItem(item.get('title', 'Unknown'), iconImage=data['full_data'].get(
                'thumbnailImage', ''), thumbnailImage=data['full_data'].get('thumbnailImage', ''))
            liz.setInfo(type='music', infoLabels=item)
            playlist.add(url, liz)

        index = int(data['extra'].get('index', 0)) - 1
        printDebug("Playlist complete.  Starting playback from track %s [playlist index %s] " % (
            data['extra'].get('index', 0), index))
        xbmc.Player().playselected(index)

        return

    @staticmethod
    def playLibraryMedia(vids, override=0, force=None, full_data=False, shelf=False):
        printDebug("== ENTER: playLibraryMedia ==", False)

        if override == 1:
            override = True
            full_data = True
        else:
            override = False

        PlexServers.getTranscodeSettings(override)
        server = plexbmc.gui.Utility.getServerFromURL(vids)
        id_ = vids.split('?')[0].split('&')[0].split('/')[-1]

        tree = plexbmc.gui.Utility.getXML(vids)
        if not tree:
            return

        if force:
            full_data = True

        streams = Media.getAudioSubtitlesMedia(server, tree, full_data)

        if force and streams['type'] == "music":
            Media.playPlaylist(server, streams)
            return

        url = Media.selectMedia(streams, server)

        if url is None:
            return

        protocol = url.split(':', 1)[0]

        if protocol == "file":
            printDebug("We are playing a local file")
            playurl = url.split(':', 1)[1]
        elif protocol == "http":
            printDebug("We are playing a stream")
            if PlexServers.getTranscode() == "true":
                printDebug("We will be transcoding the stream")
                playurl = PlexServers.transcode(id_, url) + MyPlexServers.getAuthDetails({'token': plexbmc.main.PleXBMC.getToken()})
            else:
                playurl = url + MyPlexServers.getAuthDetails(
                    {'token': plexbmc.main.PleXBMC.getToken()}, prefix="?")
        else:
            playurl = url

        resume = int(int(streams['media']['viewOffset']) / 1000)
        duration = int(int(streams['media']['duration']) / 1000)

        if not resume == 0 and shelf:
            printDebug("Shelf playback: display resume dialog")
            displayTime = str(datetime.timedelta(seconds=resume))
            display_list = [
                "Resume from " + displayTime, "Start from beginning"]
            resumeScreen = xbmcgui.Dialog()
            result = resumeScreen.select('Resume', display_list)
            if result == -1:
                return False

            if result == 1:
                resume = 0

        printDebug("Resume has been set to " + str(resume))

        item = xbmcgui.ListItem(path=playurl)

        if streams['full_data']:
            item.setInfo(type=streams['type'], infoLabels=streams['full_data'])
            item.setThumbnailImage(
                streams['full_data'].get('thumbnailImage', ''))
            item.setIconImage(streams['full_data'].get('thumbnailImage', ''))

        if force:

            if int(force) > 0:
                resume = int(int(force) / 1000)
            else:
                resume = force

        if force or shelf:
            if resume:
                printDebug("Playback from resume point")
                item.setProperty('ResumeTime', str(resume))
                item.setProperty('TotalTime', str(duration))

        if streams['type'] == "picture":
            import json
            request = json.dumps({"id": 1,
                                  "jsonrpc": "2.0",
                                  "method": "Player.Open",
                                  "params": {"item": {"file": playurl}}})
            # XXX: Unused variable 'html'
            html = xbmc.executeJSONRPC(request)
            return
        else:
            # XXX: Unused variable 'start'
            start = xbmcplugin.setResolvedUrl(plexbmc.main.PleXBMC.getHandle(), True, item)

        # record the playing file and server in the home window
        # so that plexbmc helper can find out what is playing
        WINDOW = xbmcgui.Window(10000)
        WINDOW.setProperty('plexbmc.nowplaying.server', server)
        WINDOW.setProperty('plexbmc.nowplaying.id', id_)

        # Set a loop to wait for positive confirmation of playback
        count = 0
        while not xbmc.Player().isPlaying():
            printDebug("Not playing yet...sleep for 2")
            count = count + 2
            if count >= 20:
                return
            else:
                time.sleep(2)

        if not (PlexServers.getTranscode() == "true"):
            Media.setAudioSubtitles(streams)

        if streams['type'] == "video":
            PlexServers.monitorPlayback(id_, server)

        return

    @staticmethod
    def selectMedia(data, server):
        printDebug("== ENTER: selectMedia ==", False)
        # if we have two or more files for the same movie, then present a
        # screen
        result = 0
        dvdplayback = False

        count = data['partsCount']
        options = data['parts']
        details = data['details']

        if count > 1:
            dialogOptions = []
            dvdIndex = []
            indexCount = 0
            for items in options:

                if items[1]:
                    name = items[1].split('/')[-1]
                    #name="%s %s %sMbps" % (items[1].split('/')[-1], details[indexCount]['videoResolution'], details[indexCount]['bitrate'])
                else:
                    name = "%s %s %sMbps" % (items[0].split(
                        '.')[-1], details[indexCount]['videoResolution'], details[indexCount]['bitrate'])

                if settings('forcedvd'):
                    if '.ifo' in name.lower():
                        printDebug("Found IFO DVD file in " + name)
                        name = "DVD Image"
                        dvdIndex.append(indexCount)

                dialogOptions.append(name)
                indexCount += 1

            printDebug(
                "Create selection dialog box - we have a decision to make!")
            startTime = xbmcgui.Dialog()
            result = startTime.select('Select media to play', dialogOptions)
            if result == -1:
                return None

            if result in dvdIndex:
                printDebug("DVD Media selected")
                dvdplayback = True
        else:
            if settings('forcedvd'):
                if '.ifo' in options[result]:
                    dvdplayback = True

        newurl = plexbmc.gui.Media.mediaType({'key': options[result][0], 'file': options[result][1]}, server, dvdplayback)

        printDebug("We have selected media at " + newurl)
        return newurl

class Sections:
    @staticmethod
    def getServerSections(ip_address, port, name, uuid):
        printDebug("== ENTER: getServerSections ==", False)

        cache_file = "%s%s.sections.cache" % (CACHE_DATA, uuid)
        success, temp_list = cache.check(cache_file)

        if not success:
            html = plexbmc.servers.PlexServers.getURL(
                'http://%s:%s/library/sections' % (ip_address, port))

            if html is False:
                return {}

            sections = plexbmc.etree.fromstring(html)
            temp_list = []
            for section in sections:
                path = section.get('key')
                if not path[0] == "/":
                    path = '/library/sections/%s' % path

                temp_list.append({'title': section.get('title', 'Unknown').encode('utf-8'),
                                  'address': ip_address + ":" + port,
                                  'serverName': name,
                                  'uuid': uuid,
                                  'sectionuuid': section.get('uuid', ''),
                                  'path': path,
                                  'token': section.get('accessToken', None),
                                  'location': "local",
                                  'art': section.get('art', None),
                                  'local': '1',
                                  'type': section.get('type', ''),
                                  'owned': '1'})
            cache.write(cache_file, temp_list)
        return temp_list

    @staticmethod
    def getMyplexSections():
        printDebug("== ENTER: getMyplexSections ==", False)

        cache_file = "%smyplex.sections.cache" % (CACHE_DATA)
        success, temp_list = cache.check(cache_file)

        if not success:
            html = plexbmc.servers.MyPlexServers.getMyPlexURL('/pms/system/library/sections')

            if html is False:
                return {}

            tree = plexbmc.etree.fromstring(html).getiterator("Directory")
            temp_list = []
            for sections in tree:
                temp_list.append({'title': sections.get('title', 'Unknown').encode('utf-8'),
                                  'address': sections.get('host', 'Unknown') + ":" + sections.get('port'),
                                  'serverName': sections.get('serverName', 'Unknown').encode('utf-8'),
                                  'uuid': sections.get('machineIdentifier', 'Unknown'),
                                  'sectionuuid': sections.get('uuid', '').encode('utf-8'),
                                  'path': sections.get('path'),
                                  'token': sections.get('accessToken', None),
                                  'location': "myplex",
                                  'art': sections.get('art'),
                                  'local': sections.get('local'),
                                  'type': sections.get('type', 'Unknown'),
                                  'owned': sections.get('owned', '0')})
            cache.write(cache_file, temp_list)
        return temp_list

    @staticmethod
    def getAllSections(server_list=None):
        '''
        from server_list, get a list of all the available sections
        and deduplicate the sections list
        @input: None
        @return: section_list
        '''
        printDebug("== ENTER: getAllSections ==", False)

        if server_list is None:
            server_list = plexbmc.servers.PlexServers.discoverAll()
        printDebug("Using servers list: " + str(server_list))

        section_list = []
        myplex_section_list = []
        myplex_complete = False
        local_complete = False

        for server in server_list.itervalues():
            if server['discovery'] == "local" or server['discovery'] == "auto":
                section_details = Sections.getServerSections(server['server'], server['port'], server['serverName'], server['uuid'])
                section_list += section_details
                local_complete = True

            elif server['discovery'] == "myplex":
                if not myplex_complete:
                    section_details = Sections.getMyplexSections()
                    myplex_section_list += section_details
                    myplex_complete = True
        '''
        logfile = PLUGINPATH + "/_section_list.txt"
        with open(logfile, 'wb') as f:
            f.write(str(section_list))

        logfile = PLUGINPATH + "/_myplex_section_list.txt"
        with open(logfile, 'wb') as f:
            f.write(str(myplex_section_list))
        '''
        # Remove any myplex sections that are locally available
        if myplex_complete and local_complete:
            printDebug("Deduplicating myplex sections list")
            for each_server in server_list.values():
                printDebug("Checking server [%s]" % each_server)
                if each_server['discovery'] == 'myplex':
                    printDebug("Skipping as a myplex server")
                    continue
                myplex_section_list = [x for x in myplex_section_list if not x['uuid'] == each_server['uuid']]

        section_list += myplex_section_list
        '''
        logfile = PLUGINPATH + "/_final_section_list.txt"
        with open(logfile, 'wb') as f:
            f.write(str(section_list))
        '''
        return section_list

