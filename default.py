'''
    @document   : default.py
    @package    : PleXBMC add-on
    @author     : Hippojay (aka Dave Hawes-Johnson)
    @copyright  : 2011-2012, Hippojay
    @version    : 3.0 (frodo)

    @license    : Gnu General Public License - see LICENSE.TXT
    @description: pleXBMC XBMC add-on

    This file is part of the XBMC PleXBMC Plugin.

    PleXBMC Plugin is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    PleXBMC Plugin is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PleXBMC Plugin.  If not, see <http://www.gnu.org/licenses/>.

'''
#######################################################################################
# autopep8 configuration
# ----------------------
# Standard:   -a -a --max-line-length 132  --ignore=E309,E301,E303
# lib2to3:    -a -a --max-line-length 132  --select=W690
# Deprecated: --aggressive --select=W6
#
# E301 - Put a blank line between a class docstring and its first method declaration
# E303 - Remove blank lines between a function declaration and its docstring
# E309 - Put a blank line between a class declaration and its first method declaration
#######################################################################################

import base64
import datetime
import httplib
import inspect
import os
import random
import re
import socket
import sys
import time
import urllib
import xbmc  # pylint: disable=F0401
import xbmcaddon  # pylint: disable=F0401
import xbmcgui  # pylint: disable=F0401
import xbmcplugin  # pylint: disable=F0401
import xbmcvfs  # pylint: disable=F0401
try:
    import cPickle as pickle
except ImportError:
    import pickle

__addon__ = xbmcaddon.Addon()
__plugin__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__icon__ = __addon__.getAddonInfo('icon')
__cachedir__ = __addon__.getAddonInfo('profile')
__settings__ = xbmcaddon.Addon(id='plugin.video.plexbmc')
__localize__ = __addon__.getLocalizedString
#__cwd__ = __settings__.getAddonInfo('path')
__cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')

BASE_RESOURCE_PATH = xbmc.translatePath(
    os.path.join(__cwd__, 'resources', 'lib'))
PLUGINPATH = xbmc.translatePath(os.path.join(__cwd__))
sys.path.append(BASE_RESOURCE_PATH)
CACHEDATA = __cachedir__
PLEXBMC_VERSION = __version__

print "===== PLEXBMC START ====="
print "PleXBMC -> Running Python: " + str(sys.version_info)
print "PleXBMC -> Running PleXBMC: " + str(PLEXBMC_VERSION)
print "PleXBMC -> FullRes Thumbs are se to: " + __settings__.getSetting("fullres_thumbs")
print "PleXBMC -> CWD is set to: " + __cwd__

# Get the setting from the appropriate file.
DEFAULT_PORT = "32400"
MYPLEX_SERVER = "my.plexapp.com"
_MODE_GETCONTENT = 0
_MODE_TVSHOWS = 1
_MODE_MOVIES = 2
_MODE_ARTISTS = 3
_MODE_TVSEASONS = 4
_MODE_PLAYLIBRARY = 5
_MODE_TVEPISODES = 6
_MODE_PLEXPLUGINS = 7
_MODE_PROCESSXML = 8
_MODE_CHANNELSEARCH = 9
_MODE_CHANNELPREFS = 10
_MODE_PLAYSHELF = 11
_MODE_BASICPLAY = 12
_MODE_SHARED_MOVIES = 13
_MODE_ALBUMS = 14
_MODE_TRACKS = 15
_MODE_PHOTOS = 16
_MODE_MUSIC = 17
_MODE_VIDEOPLUGINPLAY = 18
_MODE_PLEXONLINE = 19
_MODE_CHANNELINSTALL = 20
_MODE_CHANNELVIEW = 21
_MODE_DISPLAYSERVERS = 22
_MODE_PLAYLIBRARY_TRANSCODE = 23
_MODE_MYPLEXQUEUE = 24
_MODE_SHARED_SHOWS = 25
_MODE_SHARED_MUSIC = 26
_MODE_SHARED_PHOTOS = 27
_MODE_DELETE_REFRESH = 28
_MODE_SHARED_ALL = 29

_SUB_AUDIO_XBMC_CONTROL = "0"
_SUB_AUDIO_PLEX_CONTROL = "1"
_SUB_AUDIO_NEVER_SHOW = "2"

# XXX: Get rid of these globals!!!
_PARAM_TOKEN = ""

# Check debug first...
#g_debug = __settings__.getSetting('debug')
#g_debug_dev = __settings__.getSetting('debug_dev')
# XXX;
g_debug = 'true'
g_debug_dev = 'true'

# elementtree imports. If debugging on, use python elementtree, as c implementation
# is horrible for debugging.

if g_debug == "true":
    print("PleXBMC -> Running with built-in ElemenTree (debug).")
    import xml.etree.ElementTree as etree
else:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
        print("PleXBMC -> Running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # normal cElementTree install
            import cElementTree as etree
            print("PleXBMC -> Running with built-in cElementTree")
        except ImportError:
            try:
                # normal ElementTree install
                import xml.etree.ElementTree as etree
                print("PleXBMC -> Running with built-in ElementTree")
            except ImportError:
                print(
                    "PleXBMC -> Failed to import ElementTree from any known place")


def printDebug(msg, functionname=True):
    if g_debug == "true":
        if functionname is False:
            print str(msg)
        else:
            print "PleXBMC -> " + inspect.stack()[1][3] + ": " + str(msg)


def printDev(msg, functionname=True):
    if g_debug_dev == "true":
        if functionname is False:
            print str(msg)
        else:
            print "PleXBMC -> " + inspect.stack()[1][3] + ": " + str(msg)


def getPlatform():
    if xbmc.getCondVisibility('system.platform.osx'):
        return "OSX"
    elif xbmc.getCondVisibility('system.platform.atv2'):
        return "ATV2"
    elif xbmc.getCondVisibility('system.platform.ios'):
        return "iOS"
    elif xbmc.getCondVisibility('system.platform.windows'):
        return "Windows"
    elif xbmc.getCondVisibility('system.platform.linux'):
        return "Linux/RPi"
    elif xbmc.getCondVisibility('system.platform.android'):
        return "Linux/Android"

    return "Unknown"

PLEXBMC_PLATFORM = getPlatform()
print "PleXBMC -> Platform: " + str(PLEXBMC_PLATFORM)


def wake_on_lan():
    # Next Check the WOL status - lets give the servers as much time as
    # possible to come up
    g_wolon = __settings__.getSetting('wolon')
    if g_wolon == "true":
        from WOL import wake_on_lan
        printDebug("PleXBMC -> Wake On LAN: " + g_wolon, False)
        for i in range(1, 12):
            wakeserver = __settings__.getSetting('wol' + str(i))
            if not wakeserver == "":
                try:
                    printDebug(
                        "PleXBMC -> Waking server " + str(i) + " with MAC: " + wakeserver, False)
                    wake_on_lan(wakeserver)
                except ValueError:
                    printDebug(
                        "PleXBMC -> Incorrect MAC address format for server " + str(i), False)
                except:
                    printDebug("PleXBMC -> Unknown wake on lan error", False)

g_stream = __settings__.getSetting('streaming')
g_secondary = __settings__.getSetting('secondary')
g_streamControl = __settings__.getSetting('streamControl')
g_channelview = __settings__.getSetting('channelview')
g_flatten = __settings__.getSetting('flatten')
printDebug("PleXBMC -> Flatten is: " + g_flatten, False)
g_forcedvd = __settings__.getSetting('forcedvd')

if g_debug == "true":
    print "PleXBMC -> Settings streaming: " + g_stream
    print "PleXBMC -> Setting filter menus: " + g_secondary
    print "PleXBMC -> Setting debug to " + g_debug
    if g_streamControl == _SUB_AUDIO_XBMC_CONTROL:
        print "PleXBMC -> Setting stream Control to : XBMC CONTROL (%s)" % g_streamControl
    elif g_streamControl == _SUB_AUDIO_PLEX_CONTROL:
        print "PleXBMC -> Setting stream Control to : PLEX CONTROL (%s)" % g_streamControl
    elif g_streamControl == _SUB_AUDIO_NEVER_SHOW:
        print "PleXBMC -> Setting stream Control to : NEVER SHOW (%s)" % g_streamControl

    print "PleXBMC -> Force DVD playback: " + g_forcedvd
else:
    print "PleXBMC -> Debug is turned off.  Running silent"


def nas_override():
    # NAS Override
    global g_nasoverride
    global g_nasoverrideip
    global g_nasroot
    g_nasoverride = __settings__.getSetting('nasoverride')
    printDebug("PleXBMC -> SMB IP Override: " + g_nasoverride, False)
    if g_nasoverride == "true":
        g_nasoverrideip = __settings__.getSetting('nasoverrideip')
        if g_nasoverrideip == "":
            printDebug("PleXBMC -> No NAS IP Specified.  Ignoring setting")
        else:
            printDebug("PleXBMC -> NAS IP: " + g_nasoverrideip, False)

        g_nasroot = __settings__.getSetting('nasroot')

# Get look and feel
if __settings__.getSetting("contextreplace") == "true":
    g_contextReplace = True
else:
    g_contextReplace = False

g_skipcontext = __settings__.getSetting("skipcontextmenus")
g_skipmetadata = __settings__.getSetting("skipmetadata")
g_skipmediaflags = __settings__.getSetting("skipflags")
g_skipimages = __settings__.getSetting("skipimages")

# g_loc = PLUGINPATH   * Does not work right, why? *
g_loc = "special://home/addons/plugin.video.plexbmc"
g_thumb = "special://home/addons/plugin.video.plexbmc/resources/thumb.png"


# Create the standard header structure and load with a User Agent to
# ensure we get back a response.
g_txheaders = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)',
}

# Set up holding variable for session ID
global g_sessionID
g_sessionID = None


class Cache:
    @staticmethod
    def read(cachefile):
        if __settings__.getSetting("cache") == "false":
            return (False, None)

        printDebug("CACHE [%s]: attempting to read" % cachefile)
        cache = xbmcvfs.File(cachefile)
        cachedata = cache.read()
        cache.close()
        if cachedata:
            printDebug("CACHE [%s]: read: [%s]" % (cachefile, cachedata))
            cacheobject = pickle.loads(cachedata)
            return (True, cacheobject)

        printDebug("CACHE [%s]: empty" % cachefile)
        return (False, None)

    @staticmethod
    def write(cachefile, object):
        if __settings__.getSetting("cache") == "false":
            return True

        printDebug("CACHE [%s]: Writing file" % cachefile)
        cache = xbmcvfs.File(cachefile, 'w')
        cache.write(pickle.dumps(object))
        cache.close()
        return True

    @staticmethod
    def check(cachefile, life=3600):
        if __settings__.getSetting("cache") == "false":
            return (False, None)

        if xbmcvfs.exists(cachefile):
            printDebug("CACHE [%s]: exists" % cachefile)
            now = int(round(time.time(), 0))
            created = int(xbmcvfs.Stat(cachefile).st_ctime())
            modified = int(xbmcvfs.Stat(cachefile).st_mtime())
            accessed = int(xbmcvfs.Stat(cachefile).st_atime())
            printDebug("CACHE [%s]: mod[%s] now[%s] diff[%s]" % (cachefile, modified, now, now - modified))
            printDebug("CACHE [%s]: ctd[%s] mod[%s] acc[%s]" % (cachefile, created, modified, accessed))

            if (modified < 0) or (now - modified) > life:
                printDebug("CACHE [%s]: too old, delete" % cachefile)
                success = xbmcvfs.delete(cachefile)
                if success:
                    printDebug("CACHE [%s]: deleted" % cachefile)
                else:
                    printDebug("CACHE [%s]: not deleted" % cachefile)
            else:
                printDebug("CACHE [%s]: current" % cachefile)

                return Cache.read(cachefile)
        else:
            printDebug("CACHE [%s]: does not exist" % cachefile)

        return (False, None)

    @staticmethod
    def delete():
        printDebug("== ENTER: deleteCache ==", False)
        # cache_header=".cache.directory"
        cache_suffix = "cache"
        dirs, files = xbmcvfs.listdir(CACHEDATA)

        printDebug("List of file: [%s]" % files)
        printDebug("List of dirs: [%s]" % dirs)

        for i in files:
            if cache_suffix not in i:
                continue

            success = xbmcvfs.delete(CACHEDATA + i)
            if success:
                printDebug("SUCCESSFUL: removed %s" % i)
            else:
                printDebug("UNSUCESSFUL: did not remove %s" % i)


class PlexServers:
    @staticmethod
    def discoverAll():
        '''
        Take the users settings and add the required master servers
        to the server list.  These are the devices which will be queried
        for complete library listings.  There are 3 types:
            local server - from IP configuration
            bonjour server - from a bonjour lookup
            myplex server - from myplex configuration
        Alters the global g_serverDict value
        @input: None
        @return: None
        '''
        printDebug("== ENTER: discoverAllServers ==", False)

        das_servers = {}
        das_server_index = 0

        g_discovery = __settings__.getSetting('discovery')

        if g_discovery == "1":
            printDebug(
                "PleXBMC -> local GDM discovery setting enabled.", False)
            try:
                import plexgdm
                printDebug("Attempting GDM lookup on multicast")
                if g_debug == "true":
                    GDM_debug = 3
                else:
                    GDM_debug = 0

                gdm_cache_file = CACHEDATA + "gdm.server.cache"
                gdm_cache_ok = False
                gdm_cache_ok, gdm_server_name = Cache.check(gdm_cache_file)

                if not gdm_cache_ok:
                    gdm_client = plexgdm.plexgdm(GDM_debug)
                    gdm_client.discover()
                    gdm_server_name = gdm_client.getServerList()
                    Cache.write(gdm_cache_file, gdm_server_name)

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
            das_host = __settings__.getSetting('ipaddress')
            das_port = __settings__.getSetting('port')

            if not das_host or das_host == "<none>":
                das_host = None
            elif not das_port:
                printDebug(
                    "PleXBMC -> No port defined.  Using default of " + DEFAULT_PORT, False)
                das_port = DEFAULT_PORT

            printDebug(
                "PleXBMC -> Settings hostname and port: %s : %s" % (das_host, das_port), False)

            if das_host is not None:
                local_server = PlexServers.getLocalServers(das_host, das_port)
                if local_server:
                    das_servers[das_server_index] = local_server
                    das_server_index = das_server_index + 1

        if __settings__.getSetting('myplex_user') != "":
            printDebug("PleXBMC -> Adding myplex as a server location", False)

            myplex_cache_file = CACHEDATA + "myplex.server.cache"
            success, das_myplex = Cache.check(myplex_cache_file)

            if not success:
                das_myplex = MyPlexServers.getServers()
                Cache.write(myplex_cache_file, das_myplex)

            if das_myplex:
                printDebug("MyPlex discovery completed")
                for device in das_myplex:

                    das_servers[das_server_index] = device
                    das_server_index = das_server_index + 1

        # Remove Cloud Sync servers, since they cause problems
        # for das_server_index,das_server in das_servers.items():
        # Cloud sync "servers" don't have a version key in the dictionary
        #     if 'version' not in das_server:
        #         del das_servers[das_server_index]

        printDebug("PleXBMC -> serverList is " + str(das_servers), False)
        return Sections.deduplicate(das_servers)

    @staticmethod
    def getLocalServers(ip_address="localhost", port=32400):
        '''
        Connect to the defined local server (either direct or via bonjour discovery)
        and get a list of all known servers.
        @input: nothing
        @return: a list of servers (as Dict)
        '''
        printDebug("== ENTER: getLocalServers ==", False)

        url_path = "/"
        html = PlexServers.getURL(ip_address + ":" + port + url_path)

        if html is False:
            return []

        server = etree.fromstring(html)

        return {'serverName': server.attrib['friendlyName'].encode('utf-8'),
                'server': ip_address,
                'port': port,
                'discovery': 'local',
                'token': None,
                'uuid': server.attrib['machineIdentifier'],
                'owned': '1',
                'master': 1,
                'class': ''}

    @staticmethod
    def getURL(url, suppress=True, type="GET", popup=0):
        printDebug("== ENTER: getURL ==", False)
        try:
            if url[0:4] == "http":
                serversplit = 2
                urlsplit = 3
            else:
                serversplit = 0
                urlsplit = 1

            server = url.split('/')[serversplit]
            urlPath = "/" + "/".join(url.split('/')[urlsplit:])

            authHeader = MyPlexServers.getAuthDetails(
                {'token': _PARAM_TOKEN}, False)

            printDebug("url = " + url)
            printDebug("header = " + str(authHeader))
            conn = httplib.HTTPConnection(server, timeout=8)
            conn.request(type, urlPath, headers=authHeader)
            data = conn.getresponse()

            if int(data.status) == 200:
                link = data.read()
                printDebug("====== XML returned =======")
                printDebug(link, False)
                printDebug("====== XML finished ======")
                try:
                    conn.close()
                except:
                    pass
                return link

            elif (int(data.status) == 301) or (int(data.status) == 302):
                try:
                    conn.close()
                except:
                    pass
                return data.getheader('Location')

            elif int(data.status) == 401:
                error = "Authentication error on server [%s].  Check user/password." % server
                print "PleXBMC -> %s" % error
                if suppress is False:
                    if popup == 0:
                        xbmc.executebuiltin(
                            "XBMC.Notification(Server authentication error,)")
                    else:
                        xbmcgui.Dialog().ok(
                            "PleXBMC", "Authentication require or incorrect")

            elif int(data.status) == 404:
                error = "Server [%s] XML/web page does not exist." % server
                print "PleXBMC -> %s" % error
                if suppress is False:
                    if popup == 0:
                        xbmc.executebuiltin(
                            "XBMC.Notification(Server web/XML page error,)")
                    else:
                        xbmcgui.Dialog().ok(
                            "PleXBMC", "Server error, data does not exist")

            elif int(data.status) >= 400:
                error = "HTTP response error: " + \
                    str(data.status) + " " + str(data.reason)
                print error
                if suppress is False:
                    if popup == 0:
                        xbmc.executebuiltin(
                            "XBMC.Notification(URL error: " + str(data.reason) + ",)")
                    else:
                        xbmcgui.Dialog().ok("Error", server)

            else:
                link = data.read()
                printDebug("====== XML returned =======")
                printDebug(link, False)
                printDebug("====== XML finished ======")
                try:
                    conn.close()
                except:
                    pass
                return link

        except socket.gaierror:
            error = "Unable to locate host [%s]\nCheck host name is correct" % server
            print "PleXBMC %s" % error
            if suppress is False:
                if popup == 0:
                    xbmc.executebuiltin(
                        "XBMC.Notification(\"PleXBMC\": Server name incorrect,)")
                else:
                    xbmcgui.Dialog().ok(
                        "PleXBMC", "Server [%s] not found" % server)

        except socket.error as msg:
            error = "Server[%s] is offline, or not responding\nReason: %s" % (
                server, str(msg))
            print "PleXBMC -> %s" % error
            if suppress is False:
                if popup == 0:
                    xbmc.executebuiltin(
                        "XBMC.Notification(\"PleXBMC\": Server offline or not responding,)")
                else:
                    xbmcgui.Dialog().ok(
                        "PleXBMC", "Server is offline or not responding")

        try:
            conn.close()
        except:
            pass

        return False

    @staticmethod
    def setMasterServer():
        printDebug("== ENTER: setmasterserver ==", False)

        servers = PlexServers.getMasterServer(True)
        printDebug(str(servers))

        current_master = __settings__.getSetting('masterServer')

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
        __settings__.setSetting('masterServer', servers[result]['name'])
        return

    @staticmethod
    def getTranscodeSettings(override=False):
        printDebug("== ENTER: gettranscodesettings ==", False)

        global g_transcode
        g_transcode = __settings__.getSetting('transcode')

        if override is True:
            printDebug(
                "Transcode override.  Will play media with addon transcoding settings")
            g_transcode = "true"

        if g_transcode == "true":
            # If transcode is set, ignore the stream setting for file and smb:
            global g_stream
            g_stream = "1"
            printDebug("We are set to Transcode, overriding stream selection")
            global g_transcodefmt
            g_transcodefmt = "m3u8"

            global g_quality
            g_quality = str(int(__settings__.getSetting('quality')) + 3)
            printDebug("Transcode format is " + g_transcodefmt)
            printDebug("Transcode quality is " + g_quality)

            baseCapability = "http-live-streaming,http-mp4-streaming,http-streaming-video,http-streaming-video-1080p,http-mp4-video,http-mp4-video-1080p;videoDecoders=h264{profile:high&resolution:1080&level:51};"

            g_audioOutput = __settings__.getSetting("audiotype")
            if g_audioOutput == "0":
                audio = "mp3,aac{bitrate:160000}"
            elif g_audioOutput == "1":
                audio = "ac3{channels:6}"
            elif g_audioOutput == "2":
                audio = "dts{channels:6}"

            global capability
            capability = "X-Plex-Client-Capabilities=" + \
                urllib.quote_plus(
                    "protocols=" + baseCapability + "audioDecoders=" + audio)
            printDebug("Plex Client Capability = " + capability)

            import uuid
            global g_sessionID
            g_sessionID = str(uuid.uuid4())

    @staticmethod
    def getMasterServer(all=False):
        printDebug("== ENTER: getmasterserver ==", False)

        possibleServers = []
        current_master = __settings__.getSetting('masterServer')
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

        server = Utility.getServerFromURL(url)

        # Check for myplex user, which we need to alter to a master server
        if 'plexapp.com' in url:
            server = PlexServers.getMasterServer()

        printDebug("Using preferred transcoding server: " + server)
        printDebug("incoming URL is: %s" % url)

        transcode_request = "/video/:/transcode/segmented/start.m3u8"
        transcode_settings = {'3g': 0,
                              'offset': 0,
                              'quality': g_quality,
                              'session': g_sessionID,
                              'identifier': identifier,
                              'httpCookie': "",
                              'userAgent': "",
                              'ratingKey': id,
                              'subtitleSize': __settings__.getSetting('subSize').split('.')[0],
                              'audioBoost': __settings__.getSetting('audioSize').split('.')[0],
                              'key': ""}

        if identifier:
            transcode_target = url.split('url=')[1]
            transcode_settings['webkit'] = 1
        else:
            transcode_settings['identifier'] = "com.plexapp.plugins.library"
            transcode_settings['key'] = urllib.quote_plus(
                "http://%s/library/metadata/%s" % (server, id))
            transcode_target = urllib.quote_plus(
                "http://127.0.0.1:32400" + "/" + "/".join(url.split('/')[3:]))
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
        fullURL = "http://" + server + transcode_request + "&X-Plex-Access-Key=" + publicKey + \
            "&X-Plex-Access-Time=" + \
            str(now) + "&X-Plex-Access-Code=" + \
            urllib.quote_plus(token) + "&" + capability

        printDebug("Transcoded media location URL " + fullURL)

        return fullURL

    @staticmethod
    def pluginTranscodeMonitor(sessionID, server):
        printDebug("== ENTER: pluginTranscodeMonitor ==", False)

        # Logic may appear backward, but this does allow for a failed start to be detected
        # First while loop waiting for start

        if __settings__.getSetting('monitoroff') == "true":
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
        stopURL = 'http://' + server + \
            '/video/:/transcode/segmented/stop?session=' + sessionID

        # XXX: Unused variable 'html'
        html = PlexServers.getURL(stopURL)
        return


class MyPlexServers:

    '''
    '''
    @staticmethod
    def getServers():
        '''
        Connect to the myplex service and get a list of all known
        servers.
        @input: nothing
        @return: a list of servers (as Dict)
        '''

        printDebug("== ENTER: getMyPlexServers ==", False)

        tempServers = []
        url_path = "/pms/servers"
        all_servers = MyPlexServers.getMyPlexURL(url_path)

        if all_servers is False:
            return {}

        servers = etree.fromstring(all_servers)
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
        A seperate function is required as interfacing into myplex
        is slightly different than getting a standard URL
        @input: url to get, whether we need a new token, whether to display on screen err
        @return: an xml page as string or false
        '''
        printDebug("== ENTER: getMyPlexURL ==", False)
        printDebug("url = " + MYPLEX_SERVER + url_path)

        try:
            conn = httplib.HTTPSConnection(MYPLEX_SERVER, timeout=5)
            conn.request(
                "GET", url_path + "?X-Plex-Token=" + MyPlexServers.getMyPlexToken(renew))
            data = conn.getresponse()
            if (int(data.status) == 401) and not (renew):
                try:
                    conn.close()
                except:
                    pass
                return MyPlexServers.getMyPlexURL(url_path, True)

            if int(data.status) >= 400:
                error = "HTTP response error: " + \
                    str(data.status) + " " + str(data.reason)
                if suppress is False:
                    xbmcgui.Dialog().ok("Error", error)
                print error
                try:
                    conn.close()
                except:
                    pass
                return False
            elif int(data.status) == 301 and type == "HEAD":
                try:
                    conn.close()
                except:
                    pass
                return str(data.status) + "@" + data.getheader('Location')
            else:
                link = data.read()
                printDebug("====== XML returned =======")
                printDebug(link, False)
                printDebug("====== XML finished ======")
        except socket.gaierror:
            error = 'Unable to lookup host: ' + \
                MYPLEX_SERVER + "\nCheck host name is correct"
            if suppress is False:
                xbmcgui.Dialog().ok("Error", error)
            print error
            return False
        except socket.error as msg:
            error = "Unable to connect to " + \
                MYPLEX_SERVER + "\nReason: " + str(msg)
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
            user, token = (__settings__.getSetting('myplex_token')).split('|')
        except:
            token = None

        if (token is None) or (renew) or (user != __settings__.getSetting('myplex_user')):
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
        myplex_username = __settings__.getSetting('myplex_user')
        myplex_password = __settings__.getSetting('myplex_pass')

        if (myplex_username or myplex_password) == "":
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
            conn = httplib.HTTPSConnection(MYPLEX_SERVER)
            conn.request("POST", "/users/sign_in.xml", txdata, myplex_headers)
            data = conn.getresponse()

            if int(data.status) == 201:
                link = data.read()
                printDebug("====== XML returned =======")

                try:
                    token = etree.fromstring(link).findtext(
                        'authentication-token')
                    __settings__.setSetting(
                        'myplex_token', myplex_username + "|" + token)
                except:
                    printDebug(link)

                printDebug("====== XML finished ======")
            else:
                error = "HTTP response error: " + \
                    str(data.status) + " " + str(data.reason)
                if suppress is False:
                    xbmcgui.Dialog().ok(title, error)
                print error
                return ""
        except socket.gaierror:
            error = 'Unable to lookup host: MyPlex' + \
                "\nCheck host name is correct"
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


class Sections:

    '''
    '''
    @staticmethod
    def deduplicate(server_list):
        '''
        Return list of all media sections configured
        within PleXBMC
        @input: None
        @Return: unique list of media servers
        '''
        printDebug("== ENTER: deduplicateServers ==", False)

        if len(server_list) <= 1:
            return server_list

        temp_list = server_list.values()
        oneCount = 0
        for onedevice in temp_list:
            twoCount = 0
            for twodevice in temp_list:
                #printDebug( "["+str(oneCount)+":"+str(twoCount)+"] Checking " + onedevice['uuid'] + " and " + twodevice['uuid'])
                if oneCount == twoCount:
                    #printDebug( "skip" )
                    twoCount += 1
                    continue
                if onedevice['uuid'] == twodevice['uuid']:
                    #printDebug ( "match" )
                    if onedevice['discovery'] == "auto" or onedevice['discovery'] == "local":
                        temp_list.pop(twoCount)
                    else:
                        temp_list.pop(oneCount)
                # else:
                #    printDebug( "no match" )
                twoCount += 1
            oneCount += 1
        count = 0
        unique_list = {}
        for i in temp_list:
            unique_list[count] = i
            count = count + 1
        printDebug("Unique server List: " + str(unique_list))
        return unique_list

    @staticmethod
    def getServerSections(ip_address, port, name, uuid):
        printDebug("== ENTER: getServerSections ==", False)

        cache_file = "%s%s.sections.cache" % (CACHEDATA, uuid)
        success, temp_list = Cache.check(cache_file)

        if not success:
            html = PlexServers.getURL(
                'http://%s:%s/library/sections' % (ip_address, port))

            if html is False:
                return {}

            sections = etree.fromstring(html)
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
            Cache.write(cache_file, temp_list)
        return temp_list

    @staticmethod
    def getMyplexSections():
        printDebug("== ENTER: getMyplexSections ==", False)

        cache_file = "%smyplex.sections.cache" % (CACHEDATA)
        success, temp_list = Cache.check(cache_file)

        if not success:
            html = MyPlexServers.getMyPlexURL('/pms/system/library/sections')

            if html is False:
                return {}

            tree = etree.fromstring(html).getiterator("Directory")
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
            Cache.write(cache_file, temp_list)
        return temp_list

    @staticmethod
    def getAllSections(server_list=None):
        '''
        from server_list, get a list of all the available sections
        and deduplicate the sections list
        @input: None
        @return: None (alters the global value g_sectionList)
        '''
        printDebug("== ENTER: getAllSections ==", False)

        if server_list is None:
            server_list = PlexServers.discoverAll()
        printDebug("Using servers list: " + str(server_list))

        section_list = []
        myplex_section_list = []
        myplex_complete = False
        local_complete = False

        for server in server_list.itervalues():
            if server['discovery'] == "local" or server['discovery'] == "auto":
                section_details = Sections.getServerSections(
                    server['server'], server['port'], server['serverName'], server['uuid'])
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
                myplex_section_list = [
                    x for x in myplex_section_list if not x['uuid'] == each_server['uuid']]

        section_list += myplex_section_list
        '''
        logfile = PLUGINPATH + "/_final_section_list.txt"
        with open(logfile, 'wb') as f:
            f.write(str(section_list))
        '''
        return section_list

    @staticmethod
    def displaySections(filter=None, shared=False):
        printDebug("== ENTER: displaySections() ==", False)
        xbmcplugin.setContent(pluginhandle, 'files')

        ds_servers = PlexServers.discoverAll()
        numOfServers = len(ds_servers)
        printDebug(
            "Using list of " + str(numOfServers) + " servers: " + str(ds_servers))

        for section in Sections.getAllSections(ds_servers):

            if shared and section.get('owned') == '1':
                continue

            details = {'title': section.get('title', 'Unknown')}

            if len(ds_servers) > 1:
                details['title'] = section.get(
                    'serverName') + ": " + details['title']

            extraData = {'fanart_image': Media.getFanart(section, section.get('address')),
                         'type': "Video",
                         'thumb': g_thumb,
                         'token': section.get('token', None)}

            # Determine what we are going to do process after a link is
            # selected by the user, based on the content we find

            path = section['path']

            if section.get('type') == 'show':
                mode = _MODE_TVSHOWS
                if (filter is not None) and (filter != "tvshows"):
                    continue

            elif section.get('type') == 'movie':
                mode = _MODE_MOVIES
                if (filter is not None) and (filter != "movies"):
                    continue

            elif section.get('type') == 'artist':
                mode = _MODE_ARTISTS
                if (filter is not None) and (filter != "music"):
                    continue

            elif section.get('type') == 'photo':
                mode = _MODE_PHOTOS
                if (filter is not None) and (filter != "photos"):
                    continue
            else:
                printDebug(
                    "Ignoring section " + details['title'] + " of type " + section.get('type') + " as unable to process")
                continue

            if g_secondary == "true":
                mode = _MODE_GETCONTENT
            else:
                path = path + '/all'

            extraData['mode'] = mode
            s_url = 'http://%s%s' % (section['address'], path)

            if g_skipcontext == "false":
                context = []
                refreshURL = "http://" + \
                    section.get('address') + section.get('path') + "/refresh"
                libraryRefresh = "RunScript(plugin.video.plexbmc, update ," + \
                    refreshURL + ")"
                context.append(('Refresh library section', libraryRefresh, ))
            else:
                context = None

            # Build that listing..
            GUI.addGUIItem(s_url, details, extraData, context)

        if shared:
            xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)
            return

        # For each of the servers we have identified
        allservers = ds_servers
        numOfServers = len(allservers)

        if __settings__.getSetting('myplex_user') != '':
            GUI.addGUIItem('http://myplexqueue', {'title': 'myplex Queue'}, {
                           'thumb': g_thumb, 'type': 'Video', 'mode': _MODE_MYPLEXQUEUE})

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
                         'thumb': g_thumb,
                         'token': server.get('token', None)}

            extraData['mode'] = _MODE_CHANNELVIEW
            u = "http://" + server['server'] + ":" + \
                server['port'] + "/system/plugins/all"
            GUI.addGUIItem(u, details, extraData)

            # Create plexonline link
            details['title'] = prefix + "Plex Online"
            extraData['type'] = "file"
            extraData['thumb'] = g_thumb
            extraData['mode'] = _MODE_PLEXONLINE

            u = "http://" + server['server'] + ":" + \
                server['port'] + "/system/plexonline"
            GUI.addGUIItem(u, details, extraData)

        if __settings__.getSetting("cache") == "true":
            details = {'title': "Refresh Data"}
            extraData = {}
            extraData['type'] = "file"

            extraData['mode'] = _MODE_DELETE_REFRESH

            u = "http://nothing"
            GUI.addGUIItem(u, details, extraData)

        # All XML entries have been parsed and we are ready to allow the user
        # to browse around.  So end the screen listing.
        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=False)


class OtherModes:

    '''
    '''
    @staticmethod
    def displayServers(url):
        printDebug("== ENTER: displayServers ==", False)
        type = url.split('/')[2]
        printDebug("Displaying entries for " + type)
        server_list = PlexServers.discoverAll()
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

            if type == "video":
                extraData['mode'] = _MODE_PLEXPLUGINS
                s_url = 'http://%s:%s/video' % (
                    mediaserver.get('server', ''), mediaserver.get('port'))
                if number_of_servers == 1:
                    url.PlexPlugins(
                        s_url + MyPlexServers.getAuthDetails(extraData, prefix="?"))
                    return

            elif type == "online":
                extraData['mode'] = _MODE_PLEXONLINE
                s_url = 'http://%s:%s/system/plexonline' % (
                    mediaserver.get('server', ''), mediaserver.get('port'))
                if number_of_servers == 1:
                    url.plexOnline(
                        s_url + MyPlexServers.getAuthDetails(extraData, prefix="?"))
                    return

            elif type == "music":
                extraData['mode'] = _MODE_MUSIC
                s_url = 'http://%s:%s/music' % (
                    mediaserver.get('server', ''), mediaserver.get('port'))
                if number_of_servers == 1:
                    GUI.music(
                        s_url + MyPlexServers.getAuthDetails(extraData, prefix="?"))
                    return

            elif type == "photo":
                extraData['mode'] = _MODE_PHOTOS
                s_url = 'http://%s:%s/photos' % (
                    mediaserver.get('server', ''), mediaserver.get('port'))
                if number_of_servers == 1:
                    GUI.photo(
                        s_url + MyPlexServers.getAuthDetails(extraData, prefix="?"))
                    return

            GUI.addGUIItem(s_url, details, extraData)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

    @staticmethod
    def myPlexQueue():
        printDebug("== ENTER: myplexqueue ==", False)

        if __settings__.getSetting('myplex_user') == '':
            xbmc.executebuiltin("XBMC.Notification(myplex not configured,)")
            return

        html = MyPlexServers.getMyPlexURL('/pms/playlists/queue/all')
        tree = etree.fromstring(html)

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
                extraData['mode'] = _MODE_PHOTOS
            elif suffix == "video":
                extraData['mode'] = _MODE_PLEXPLUGINS
            elif suffix == "music":
                extraData['mode'] = _MODE_MUSIC
            else:
                extraData['mode'] = _MODE_GETCONTENT

            GUI.addGUIItem(p_url, details, extraData)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

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
                    installed = PlexServers.getURL(url + "/install")
                    tree = etree.fromstring(installed)

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

        action = PlexServers.getURL(u)
        tree = etree.fromstring(action)

        msg = tree.get('message')
        printDebug(msg)
        xbmcgui.Dialog().ok("Plex Online", msg)
        xbmc.executebuiltin("Container.Refresh")
        return

    @staticmethod
    def plexOnline(url):
        printDebug("== ENTER: plexOnline ==")

        xbmcplugin.setContent(pluginhandle, 'addons')
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

            extraData['mode'] = _MODE_CHANNELINSTALL

            if extraData['installed'] == 1:
                details['title'] = details['title'] + " (installed)"

            elif extraData['installed'] == 2:
                extraData['mode'] = _MODE_PLEXONLINE

            u = Utility.getLinkURL(url, plugin, server)

            extraData['parameters'] = {'name': details['title']}

            GUI.addGUIItem(u, details, extraData)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

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
        PlexServers.getURL(setString)
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
        xbmcplugin.setContent(pluginhandle, 'addons')

        tree = Utility.getXML(url, tree)
        if tree is None:
            return

        myplex_url = False
        server = Utility.getServerFromURL(url)
        if (tree.get('identifier') != "com.plexapp.plugins.myplex") and ("node.plexapp.com" in url):
            myplex_url = True
            printDebug(
                "This is a myplex URL, attempting to locate master server")
            server = PlexServers.getMasterServer()['address']

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
                    extraData['mode'] = _MODE_CHANNELSEARCH
                    extraData['parameters'] = {
                        'prompt': plugin.get('prompt', "Enter Search Term").encode('utf-8')}
                else:
                    extraData['mode'] = _MODE_PLEXPLUGINS

                GUI.addGUIItem(p_url, details, extraData)

            elif plugin.tag == "Video":
                extraData['mode'] = _MODE_VIDEOPLUGINPLAY

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
                extraData['mode'] = _MODE_CHANNELPREFS
                extraData['parameters'] = {'id': plugin.get('id')}
                GUI.addGUIItem(url, details, extraData)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

    @staticmethod
    def processDirectory(url, tree=None):
        printDebug("== ENTER: processDirectory ==", False)
        printDebug("Processing secondary menus")
        xbmcplugin.setContent(pluginhandle, "")

        server = Utility.getServerFromURL(url)
        GUI.setWindowHeading(tree)
        for directory in tree:
            details = {
                'title': directory.get('title', 'Unknown').encode('utf-8')}
            extraData = {'thumb': Media.getThumb(tree, server),
                         'fanart_image': Media.getFanart(tree, server)}

            # if extraData['thumb'] == '':
            #    extraData['thumb']=extraData['fanart_image']

            extraData['mode'] = _MODE_GETCONTENT
            u = '%s' % (Utility.getLinkURL(url, directory, server))

            GUI.addGUIItem(u, details, extraData)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

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

    '''
    '''
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
                       (__settings__.getSetting('contentNone'), ))
            if content_map[__settings__.getSetting('contentNone')] <= content_map[acceptable_level]:
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
        xbmcplugin.setContent(pluginhandle, 'movies')
        server = Utility.getServerFromURL(url)
        tree = url.getXML(url, tree)
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
                extraData['mode'] = _MODE_PROCESSXML
                GUI.addGUIItem(p_url, details, extraData)

            elif plugin.tag == "Track":
                GUI.trackTag(server, tree, plugin)

            elif tree.get('viewGroup') == "movie":
                GUI.Movies(url, tree)
                return

            elif tree.get('viewGroup') == "episode":
                GUI.TVEpisodes(url, tree)
                return
        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

    @staticmethod
    def getXML(url, media=None):
        printDebug("== ENTER: getXML ==", False)
        if media is None:
            tree = PlexServers.getURL(url)

            if tree is False:
                print "PleXBMC -> Server [%s] offline, not responding or no data was receieved" % Utility.getServerFromURL(url)
                return None
            media = etree.fromstring(tree)

        if media.get('message'):
            xbmcgui.Dialog().ok(
                media.get('header', 'Message'), media.get('message', ''))
            return None

        # setWindowHeading(media)
        return media

    @staticmethod
    def get_params(paramlist):
        printDebug("== ENTER: get_params ==", False)
        printDebug("Parameter string/list: " + str(paramlist))

        param = {}
        try:
            # Make sure parmlist is a list, not a string
            paramlist if isinstance(paramlist, list) else [paramlist]

            for paramstring in paramlist:
                if len(paramstring) >= 2:
                    params = paramstring

                    if params[0] == "?":
                        cleanedparams = params[1:]
                    else:
                        cleanedparams = params

                    if (params[len(params) - 1] == '/'):
                        params = params[0:len(params) - 2]

                    pairsofparams = cleanedparams.split('&')
                    for i in range(len(pairsofparams)):
                        splitparams = {}
                        splitparams = pairsofparams[i].split('=')
                        if (len(splitparams)) == 2:
                            param[splitparams[0]] = splitparams[1]
                        elif (len(splitparams)) == 3:
                            param[splitparams[0]] = splitparams[
                                1] + "=" + splitparams[2]
                print "PleXBMC -> Detected parameters: " + str(param)
        except:
            printDebug("Parameter parsing failed: " + str(paramlist))
        return param

    @staticmethod
    def remove_html_tags(data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)


class Commands:

    '''
    '''
    @staticmethod
    def alterAudio(url):
        '''
        Display a list of available audio streams and allow a user to select one.
        The currently selected stream will be annotated with a *
        '''
        printDebug("== ENTER: alterAudio ==", False)

        html = PlexServers.getURL(url)
        tree = etree.fromstring(html)

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

        authtoken = MyPlexServers.getAuthTokenFromURL(url)
        audio_select_URL = "http://%s/library/parts/%s?audioStreamID=%s" % (Utility.getServerFromURL(
            url), part_id, audio_list[result]) + MyPlexServers.getAuthDetails({'token': authtoken})
        printDebug("User has selected stream %s" % audio_list[result])
        printDebug("Setting via URL: %s" % audio_select_URL)

        # XXX: Unused variable 'outcome'
        outcome = PlexServers.getURL(audio_select_URL, type="PUT")
        return True

    @staticmethod
    def alterSubs(url):
        '''
        Display a list of available Subtitle streams and allow a user to select one.
        The currently selected stream will be annotated with a *
        '''
        printDebug("== ENTER: alterSubs ==", False)
        html = PlexServers.getURL(url)

        tree = etree.fromstring(html)

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

        authtoken = MyPlexServers.getAuthTokenFromURL(url)
        sub_select_URL = "http://%s/library/parts/%s?subtitleStreamID=%s" % (Utility.getServerFromURL(
            url), part_id, sub_list[result]) + MyPlexServers.getAuthDetails({'token': authtoken})

        printDebug("User has selected stream %s" % sub_list[result])
        printDebug("Setting via URL: %s" % sub_select_URL)

        # XXX: Unused variable 'outcome'
        outcome = PlexServers.getURL(sub_select_URL, type="PUT")
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
            installed = PlexServers.getURL(url, type="DELETE")
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
        html = PlexServers.getURL(url)

        xbmc.executebuiltin("Container.Refresh")
        return

    @staticmethod
    def libraryRefresh(url):
        printDebug("== ENTER: libraryRefresh ==", False)

        # XXX:  Unused variable 'html'
        html = PlexServers.getURL(url)

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
            server = PlexServers.getMasterServer()['address']

        # If we find the url lookup service, then we probably have a standard
        # plugin, but possibly with resolution choices
        if '/services/url/lookup' in vids:
            printDebug("URL Lookup service")
            html = PlexServers.getURL(vids, suppress=False)
            if not html:
                return
            tree = etree.fromstring(html)

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
            html = PlexServers.getURL(vids, suppress=False)
            if not html:
                return
            tree = etree.fromstring(html)

            for bits in tree.getiterator('Part'):
                Commands.videoPluginPlay(Utility.getLinkURL(vids, bits, server))
                break

            return

        # if we have a plex URL, then this is a transcoding URL
        if 'plex://' in vids:
            printDebug("found webkit video, pass to transcoder")
            PlexServers.getTranscodeSettings(True)
            if not (prefix):
                prefix = "system"
            vids = PlexServers.transcode(0, vids, prefix)

            # Workaround for XBMC HLS request limit of 1024 byts
            if len(vids) > 1000:
                printDebug(
                    "XBMC HSL limit detected, will pre-fetch m3u8 playlist")

                playlist = PlexServers.getURL(vids)

                if not playlist or not "#EXTM3U" in playlist:

                    printDebug(
                        "Unable to get valid m3u8 playlist from transcoder")
                    return

                server = Utility.getServerFromURL(vids)
                session = playlist.split()[-1]
                vids = "http://" + server + \
                    "/video/:/transcode/segmented/" + session + "?t=1"

        printDebug("URL to Play: " + vids)
        printDebug("Prefix is: " + str(prefix))

        # If this is an Apple movie trailer, add User Agent to allow access
        if 'trailers.apple.com' in vids:
            url = vids + \
                "|User-Agent=QuickTime/7.6.5 (qtver=7.6.5;os=Windows NT 5.1Service Pack 3)"
        elif server in vids:
            url = vids + MyPlexServers.getAuthDetails({'token': _PARAM_TOKEN})
        else:
            url = vids

        printDebug("Final URL is : " + url)

        item = xbmcgui.ListItem(path=url)

        # XXX:  Unused variable 'start'
        start = xbmcplugin.setResolvedUrl(pluginhandle, True, item)

        if 'transcode' in url:
            try:
                PlexServers.pluginTranscodeMonitor(g_sessionID, server)
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
                playurl = url + \
                    MyPlexServers.getAuthDetails({'token': _PARAM_TOKEN})
            else:
                playurl = url + \
                    MyPlexServers.getAuthDetails(
                        {'token': _PARAM_TOKEN}, prefix="?")
        else:
            playurl = url

        item = xbmcgui.ListItem(path=playurl)
        return xbmcplugin.setResolvedUrl(pluginhandle, True, item)

    @staticmethod
    def monitorPlayback(id, server):
        printDebug("== ENTER: monitorPlayback ==", False)

        if __settings__.getSetting('monitoroff') == "true":
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
                PlexServers.getURL("http://" + server + "/:/progress?key=" + id +
                                   "&identifier=com.plexapp.plugins.library&time=" + str(currentTime * 1000), suppress=True)
                complete = 0

            # Otherwise, mark as watched
            else:
                if complete == 0:
                    printDebug("Movie marked as watched. Over 95% complete")
                    PlexServers.getURL("http://" + server + "/:/scrobble?key=" +
                                       id + "&identifier=com.plexapp.plugins.library", suppress=True)
                    complete = 1

            xbmc.sleep(5000)

        # If we get this far, playback has stopped
        printDebug("Playback Stopped")

        if g_sessionID is not None:
            printDebug(
                "Stopping PMS transcode job with session " + g_sessionID)
            stopURL = 'http://' + server + \
                '/video/:/transcode/segmented/stop?session=' + g_sessionID

            # XXX:  Unused variable 'html'
            html = PlexServers.getURL(stopURL)

        return

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
            if g_streamControl == _SUB_AUDIO_NEVER_SHOW:
                xbmc.Player().showSubtitles(False)
                printDebug("All subs disabled")

            return True

        # Set the AUDIO component
        if g_streamControl == _SUB_AUDIO_PLEX_CONTROL:
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
        if g_streamControl == _SUB_AUDIO_PLEX_CONTROL:
            printDebug("Attempting to set preferred subtitle Stream", True)
            subtitle = stream['subtitle']
            if subtitle:
                printDebug("Found preferred subtitle stream")
                try:
                    xbmc.Player().showSubtitles(False)
                    if subtitle.get('key'):
                        xbmc.Player().setSubtitles(subtitle[
                            'key'] + MyPlexServers.getAuthDetails({'token': _PARAM_TOKEN}, prefix="?"))
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
    def playLibraryMedia(vids, override=0, force=None, full_data=False, shelf=False):
        printDebug("== ENTER: playLibraryMedia ==", False)

        if override == 1:
            override = True
            full_data = True
        else:
            override = False

        PlexServers.getTranscodeSettings(override)
        server = Utility.getServerFromURL(vids)
        id = vids.split('?')[0].split('&')[0].split('/')[-1]

        tree = Utility.getXML(vids)
        if not tree:
            return

        if force:
            full_data = True

        streams = Media.getAudioSubtitlesMedia(server, tree, full_data)

        if force and streams['type'] == "music":
            vids.playPlaylist(server, streams)
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
            if g_transcode == "true":
                printDebug("We will be transcoding the stream")
                playurl = PlexServers.transcode(
                    id, url) + MyPlexServers.getAuthDetails({'token': _PARAM_TOKEN})

            else:
                playurl = url + \
                    MyPlexServers.getAuthDetails(
                        {'token': _PARAM_TOKEN}, prefix="?")
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
            start = xbmcplugin.setResolvedUrl(pluginhandle, True, item)

        # record the playing file and server in the home window
        # so that plexbmc helper can find out what is playing
        WINDOW = xbmcgui.Window(10000)
        WINDOW.setProperty('plexbmc.nowplaying.server', server)
        WINDOW.setProperty('plexbmc.nowplaying.id', id)

        # Set a loop to wait for positive confirmation of playback
        count = 0
        while not xbmc.Player().isPlaying():
            printDebug("Not playing yet...sleep for 2")
            count = count + 2
            if count >= 20:
                return
            else:
                time.sleep(2)

        if not (g_transcode == "true"):
            Commands.setAudioSubtitles(streams)

        if streams['type'] == "video":
            Commands.monitorPlayback(id, server)

        return

    @staticmethod
    def playPlaylist(server, data):
        printDebug("== ENTER: playPlaylist ==", False)
        printDebug("Creating new playlist")
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        playlist.clear()

        tree = Utility.getXML(
            server + data['extra'].get('album') + "/children")
        if tree is None:
            return

        TrackTags = tree.findall('Track')
        for track in TrackTags:
            printDebug("Adding playlist item")
            url, item = GUI.trackTag(server, tree, track, listing=False)
            liz = xbmcgui.ListItem(item.get('title', 'Unknown'), iconImage=data['full_data'].get(
                'thumbnailImage', ''), thumbnailImage=data['full_data'].get('thumbnailImage', ''))
            liz.setInfo(type='music', infoLabels=item)
            playlist.add(url, liz)

        index = int(data['extra'].get('index', 0)) - 1
        printDebug("Playlist complete.  Starting playback from track %s [playlist index %s] " % (
            data['extra'].get('index', 0), index))
        xbmc.Player().playselected(index)

        return


class Media:

    '''
    '''
    @staticmethod
    def mediaType(partData, server, dvdplayback=False):
        printDebug("== ENTER: mediaType ==", False)
        stream = partData['key']
        file = partData['file']

        global g_stream

        if (file is None) or (g_stream == "1"):
            printDebug("Selecting stream")
            return "http://" + server + stream

        # First determine what sort of 'file' file is

        if file[0:2] == "\\\\":
            printDebug("Looks like a UNC")
            type = "UNC"
        elif file[0:1] == "/" or file[0:1] == "\\":
            printDebug("looks like a unix file")
            type = "nixfile"
        elif file[1:3] == ":\\" or file[1:2] == ":/":
            printDebug("looks like a windows file")
            type = "winfile"
        else:
            printDebug("uknown file type")
            printDebug(str(file))
            type = "notsure"

        # 0 is auto select.  basically check for local file first, then stream
        # if not found
        if g_stream == "0":
            # check if the file can be found locally
            if type == "nixfile" or type == "winfile":
                try:
                    printDebug("Checking for local file")
                    exists = open(file, 'r')
                    printDebug("Local file found, will use this")
                    exists.close()
                    return "file:" + file
                except:
                    pass

            printDebug("No local file")
            if dvdplayback:
                printDebug("Forcing SMB for DVD playback")
                g_stream = "2"
            else:
                return "http://" + server + stream

        # 2 is use SMB
        elif g_stream == "2" or g_stream == "3":
            if g_stream == "2":
                protocol = "smb"
            else:
                protocol = "afp"

            printDebug("Selecting smb/unc")
            if type == "UNC":
                filelocation = protocol + ":" + file.replace("\\", "/")
            else:
                # Might be OSX type, in which case, remove Volumes and replace
                # with server
                server = server.split(':')[0]
                loginstring = ""

                if g_nasoverride == "true":
                    if not g_nasoverrideip == "":
                        server = g_nasoverrideip
                        printDebug("Overriding server with: " + server)

                    nasuser = __settings__.getSetting('nasuserid')
                    if not nasuser == "":
                        loginstring = __settings__.getSetting(
                            'nasuserid') + ":" + __settings__.getSetting('naspass') + "@"
                        printDebug(
                            "Adding AFP/SMB login info for user " + nasuser)

                if file.find('Volumes') > 0:
                    filelocation = protocol + ":/" + \
                        file.replace("Volumes", loginstring + server)
                else:
                    if type == "winfile":
                        filelocation = protocol + "://" + \
                            loginstring + server + "/" + file[3:]
                    else:
                        # else assume its a file local to server available over
                        # smb/samba (now we have linux PMS).  Add server name
                        # to file path.
                        filelocation = protocol + "://" + \
                            loginstring + server + file

            if g_nasoverride == "true" and g_nasroot != "":
                # Re-root the file path
                printDebug(
                    "Altering path " + filelocation + " so root is: " + g_nasroot)
                if '/' + g_nasroot + '/' in filelocation:
                    components = filelocation.split('/')
                    index = components.index(g_nasroot)

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
                             'thumbnailImage': server.getThumb(timings, server)}

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
                    'thumbnailImage': server.getThumb(
                        timings,
                        server)}

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
        if media_type == "video" and g_streamControl == _SUB_AUDIO_PLEX_CONTROL:

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
                            subtitle['key'] = 'http://' + \
                                server + stream['key']
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

                if g_forcedvd == "true":
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
            if g_forcedvd == "true":
                if '.ifo' in options[result]:
                    dvdplayback = True

        newurl = Media.mediaType(
            {'key': options[result][0], 'file': options[result][1]}, server, dvdplayback)

        printDebug("We have selected media at " + newurl)
        return newurl

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
        if g_skipimages == "true":
            return ''

        fanart = data.get('art', '').encode('utf-8')

        if fanart == '':
            return ''

        elif fanart[0:4] == "http":
            return fanart

        elif fanart[0] == '/':
            if __settings__.getSetting("fullres_fanart") != "false":
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
        if g_skipimages == "true":
            return ''

        thumbnail = data.get('thumb', '').split('?t')[0].encode('utf-8')

        if thumbnail == '':
            return g_thumb

        elif thumbnail[0:4] == "http":
            return thumbnail

        elif thumbnail[0] == '/':
            if __settings__.getSetting("fullres_thumbs") != "false":
                return 'http://' + server + thumbnail

            else:
                return Utility.photoTranscode(server, 'http://localhost:32400' + thumbnail, width, height)

        else:
            return g_thumb

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

        html = PlexServers.getURL(url, suppress=False, popup=1)

        if html is False:
            return

        tree = etree.fromstring(html)

        GUI.setWindowHeading(tree)

        if lastbit == "folder":
            Utility.processXML(url, tree)
            return

        view_group = tree.get('viewGroup', None)

        if view_group == "movie":
            printDebug("This is movie XML, passing to Movies")
            if not (lastbit.startswith('recently') or lastbit.startswith('newest') or lastbit.startswith('onDeck')):
                xbmcplugin.addSortMethod(
                    pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
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

    '''
    '''
    @staticmethod
    def addGUIItem(url, details, extraData, context=None, folder=True):
        item_title = details.get('title', 'Unknown')

        printDebug("== ENTER: addGUIItem ==", False)
        printDebug("Adding Dir for [%s]" % item_title)
        printDebug("Passed details: " + str(details))
        printDebug("Passed extraData: " + str(extraData))

        if item_title == '':
            return

        if (extraData.get('token', None) is None) and _PARAM_TOKEN:
            extraData['token'] = _PARAM_TOKEN

        aToken = MyPlexServers.getAuthDetails(extraData)
        qToken = MyPlexServers.getAuthDetails(extraData, prefix='?')

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

                if g_skipmediaflags == "false":
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

            liz.addContextMenuItems(context, g_contextReplace)

        return xbmcplugin.addDirectoryItem(handle=pluginhandle, url=u, listitem=liz, isFolder=folder)

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
        xbmcplugin.setContent(pluginhandle, 'movies')

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

            url.movieTag(url, server, tree, movie, randomNumber)

        printDebug("Skin override is: %s" %
                   __settings__.getSetting('skinoverride'))
        view_id = Skin.enforceSkinView('movie')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(pluginhandle)

    @staticmethod
    def buildContextMenu(url, itemData):
        context = []
        server = Utility.getServerFromURL(url)
        refreshURL = url.replace("/all", "/refresh")
        plugin_url = "RunScript(plugin.video.plexbmc, "
        ID = itemData.get('ratingKey', '0')

        # Initiate Library refresh
        libraryRefresh = plugin_url + "update, " + \
            refreshURL.split(
                '?')[0] + MyPlexServers.getAuthDetails(itemData, prefix="?") + ")"
        context.append(('Rescan library section', libraryRefresh, ))

        # Mark media unwatched
        unwatchURL = "http://" + server + "/:/unscrobble?key=" + ID + \
            "&identifier=com.plexapp.plugins.library" + \
            MyPlexServers.getAuthDetails(itemData)
        unwatched = plugin_url + "watch, " + unwatchURL + ")"
        context.append(('Mark as Unwatched', unwatched, ))

        # Mark media watched
        watchURL = "http://" + server + "/:/scrobble?key=" + ID + \
            "&identifier=com.plexapp.plugins.library" + \
            MyPlexServers.getAuthDetails(itemData)
        watched = plugin_url + "watch, " + watchURL + ")"
        context.append(('Mark as Watched', watched, ))

        # Delete media from Library
        deleteURL = "http://" + server + "/library/metadata/" + \
            ID + MyPlexServers.getAuthDetails(itemData, prefix="?")
        removed = plugin_url + "delete, " + deleteURL + ")"
        context.append(('Delete media', removed, ))

        # Display plugin setting menu
        settingDisplay = plugin_url + "setting)"
        context.append(('PleXBMC settings', settingDisplay, ))

        # Reload media section
        listingRefresh = plugin_url + "refresh)"
        context.append(('Reload Section', listingRefresh, ))

        # alter audio
        alterAudioURL = "http://" + server + "/library/metadata/" + \
            ID + MyPlexServers.getAuthDetails(itemData, prefix="?")
        alterAudio = plugin_url + "audio, " + alterAudioURL + ")"
        context.append(('Select Audio', alterAudio, ))

        # alter subs
        alterSubsURL = "http://" + server + "/library/metadata/" + \
            ID + MyPlexServers.getAuthDetails(itemData, prefix="?")
        alterSubs = plugin_url + "subs, " + alterSubsURL + ")"
        context.append(('Select Subtitle', alterSubs, ))

        printDebug("Using context menus " + str(context))
        return context

    @staticmethod
    def TVShows(url, tree=None):
        printDebug("== ENTER: TVShows() ==", False)
        xbmcplugin.setContent(pluginhandle, 'tvshows')

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
                         'token': _PARAM_TOKEN,
                         'key': show.get('key', ''),
                         'ratingKey': str(show.get('ratingKey', 0))}

            # banner art
            if show.get('banner', None) is not None:
                extraData['banner'] = 'http://' + server + show.get('banner')
            else:
                extraData['banner'] = g_thumb

            # Set up overlays for watched and unwatched episodes
            if extraData['WatchedEpisodes'] == 0:
                details['playcount'] = 0
            elif extraData['UnWatchedEpisodes'] == 0:
                details['playcount'] = 1
            else:
                extraData['partialTV'] = 1

            # Create URL based on whether we are going to flatten the season
            # view
            if g_flatten == "2":
                printDebug("Flattening all shows")
                extraData['mode'] = _MODE_TVEPISODES
                u = 'http://%s%s' % (server,
                                     extraData['key'].replace("children", "allLeaves"))
            else:
                extraData['mode'] = _MODE_TVSEASONS
                u = 'http://%s%s' % (server, extraData['key'])

            if g_skipcontext == "false":
                context = GUI.buildContextMenu(url, extraData)
            else:
                context = None

            GUI.addGUIItem(u, details, extraData, context)

        printDebug("Skin override is: %s" %
                   __settings__.getSetting('skinoverride'))
        view_id = Skin.enforceSkinView('tv')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

    @staticmethod
    def TVSeasons(url):
        printDebug("== ENTER: season() ==", False)
        xbmcplugin.setContent(pluginhandle, 'seasons')

        # Get URL, XML and parse
        server = Utility.getServerFromURL(url)
        tree = Utility.getXML(url)
        if tree is None:
            return

        willFlatten = False
        if g_flatten == "1":
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
                url.TVEpisodes(url)
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
                         'token': _PARAM_TOKEN,
                         'key': season.get('key', ''),
                         'ratingKey': str(season.get('ratingKey', 0)),
                         'mode': _MODE_TVEPISODES}

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

            if g_skipcontext == "false":
                context = GUI.buildContextMenu(url, season)
            else:
                context = None

            # Build the screen directory listing
            GUI.addGUIItem(url, details, extraData, context)

        printDebug("Skin override is: %s" %
                   __settings__.getSetting('skinoverride'))
        view_id = Skin.enforceSkinView('season')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

    @staticmethod
    def TVEpisodes(url, tree=None):
        printDebug("== ENTER: TVEpisodes() ==", False)
        xbmcplugin.setContent(pluginhandle, 'episodes')

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

        if g_skipimages == "false":
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
                elif child.tag == "Genre" and g_skipmetadata == "false":
                    tempgenre.append(child.get('tag'))
                elif child.tag == "Writer" and g_skipmetadata == "false":
                    tempwriter.append(child.get('tag'))
                elif child.tag == "Director" and g_skipmetadata == "false":
                    tempdir.append(child.get('tag'))
                elif child.tag == "Role" and g_skipmetadata == "false":
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
                         'token': _PARAM_TOKEN,
                         'key': episode.get('key', ''),
                         'ratingKey': str(episode.get('ratingKey', 0)),
                         'duration': duration,
                         'resume': int(int(view_offset) / 1000)}

            if extraData['fanart_image'] == "" and g_skipimages == "false":
                extraData['fanart_image'] = sectionart

            if season_thumb:
                extraData['season_thumb'] = "http://" + server + season_thumb

            # get ALL SEASONS thumb
            if not season_thumb and episode.get('parentThumb', ""):
                extraData['season_thumb'] = "http://" + \
                    server + episode.get('parentThumb', "")

            if banner:
                extraData['banner'] = "http://" + server + banner

            # Determine what tupe of watched flag [overlay] to use
            if int(episode.get('viewCount', 0)) > 0:
                details['playcount'] = 1
            else:
                details['playcount'] = 0

            # Extended Metadata
            if g_skipmetadata == "false":
                details['cast'] = tempcast
                details['director'] = " / ".join(tempdir)
                details['writer'] = " / ".join(tempwriter)
                details['genre'] = " / ".join(tempgenre)

            # Add extra media flag data
            if g_skipmediaflags == "false":
                extraData.update(Media.getMediaData(mediaarguments))

            # Build any specific context menu entries
            if g_skipcontext == "false":
                context = GUI.buildContextMenu(url, extraData)
            else:
                context = None

            extraData['mode'] = _MODE_PLAYLIBRARY
            # http:// <server> <path> &mode=<mode> &t=<rnd>
            separator = "?"
            if "?" in extraData['key']:
                separator = "&"
            u = "http://%s%s%st=%s" % (server,
                                       extraData['key'], separator, randomNumber)

            GUI.addGUIItem(u, details, extraData, context, folder=False)

        printDebug("Skin override is: %s" %
                   __settings__.getSetting('skinoverride'))
        view_id = Skin.enforceSkinView('episode')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

    @staticmethod
    def artist(url, tree=None):
        '''
        Process artist XML and display data
        @input: url of XML page, or existing tree of XML page
        @return: nothing
        '''
        printDebug("== ENTER: artist ==", False)
        xbmcplugin.setContent(pluginhandle, 'artists')

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
                         'mode': _MODE_ALBUMS,
                         'plot': artist.get('summary', '')}

            url = 'http://%s%s' % (server, extraData['key'])
            GUI.addGUIItem(url, details, extraData)

        printDebug("Skin override is: %s" %
                   __settings__.getSetting('skinoverride'))
        view_id = Skin.enforceSkinView('music')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

    @staticmethod
    def albums(url, tree=None):
        printDebug("== ENTER: albums ==", False)
        xbmcplugin.setContent(pluginhandle, 'albums')

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
                         'mode': _MODE_TRACKS,
                         'plot': album.get('summary', '')}

            if extraData['fanart_image'] == "":
                extraData['fanart_image'] = sectionart

            url = 'http://%s%s' % (server, extraData['key'])

            GUI.addGUIItem(url, details, extraData)

        printDebug("Skin override is: %s" %
                   __settings__.getSetting('skinoverride'))
        view_id = Skin.enforceSkinView('music')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

    @staticmethod
    def tracks(url, tree=None):
        printDebug("== ENTER: tracks ==", False)
        xbmcplugin.setContent(pluginhandle, 'songs')

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

            url.trackTag(server, tree, track)

        printDebug("Skin override is: %s" %
                   __settings__.getSetting('skinoverride'))
        view_id = Skin.enforceSkinView('music')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

    @staticmethod
    def trackTag(server, tree, track, listing=True):
        printDebug("== ENTER: trackTAG ==", False)
        xbmcplugin.setContent(pluginhandle, 'songs')

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

        extraData['mode'] = _MODE_BASICPLAY
        u = "%s" % (url)

        if listing:
            GUI.addGUIItem(u, details, extraData, folder=False)
        else:
            return (url, details)

    @staticmethod
    def photo(url, tree=None):
        printDebug("== ENTER: photos ==", False)
        server = url.split('/')[2]

        xbmcplugin.setContent(pluginhandle, 'photo')

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
                extraData['mode'] = _MODE_PHOTOS
                GUI.addGUIItem(u, details, extraData)

            elif picture.tag == "Photo":
                if tree.get('viewGroup', '') == "photo":
                    for photo in picture:
                        if photo.tag == "Media":
                            for images in photo:
                                if images.tag == "Part":
                                    extraData['key'] = "http://" + \
                                        server + images.get('key', '')
                                    details['size'] = int(
                                        images.get('size', 0))
                                    u = extraData['key']

                GUI.addGUIItem(u, details, extraData, folder=False)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

    @staticmethod
    def music(url, tree=None):
        printDebug("== ENTER: music ==", False)
        xbmcplugin.setContent(pluginhandle, 'artists')

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
                xbmcplugin.setContent(pluginhandle, 'songs')

                details['title'] = grapes.get(
                    'track', grapes.get('title', 'Unknown')).encode('utf-8')
                details['duration'] = int(
                    int(grapes.get('totalTime', 0)) / 1000)

                extraData['mode'] = _MODE_BASICPLAY
                GUI.addGUIItem(u, details, extraData, folder=False)
            else:
                if grapes.tag == "Artist":
                    printDebug("Artist Tag")
                    xbmcplugin.setContent(pluginhandle, 'artists')
                    details['title'] = grapes.get(
                        'artist', 'Unknown').encode('utf-8')
                elif grapes.tag == "Album":
                    printDebug("Album Tag")
                    xbmcplugin.setContent(pluginhandle, 'albums')
                    details['title'] = grapes.get(
                        'album', 'Unknown').encode('utf-8')
                elif grapes.tag == "Genre":
                    details['title'] = grapes.get(
                        'genre', 'Unknown').encode('utf-8')
                else:
                    printDebug("Generic Tag: " + grapes.tag)
                    details['title'] = grapes.get(
                        'title', 'Unknown').encode('utf-8')

                extraData['mode'] = _MODE_MUSIC
                GUI.addGUIItem(u, details, extraData)

        printDebug("Skin override is: %s" %
                   __settings__.getSetting('skinoverride'))
        view_id = Skin.enforceSkinView('music')
        if view_id:
            xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)

        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

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
            elif child.tag == "Genre" and g_skipmetadata == "false":
                tempgenre.append(child.get('tag'))
            elif child.tag == "Writer" and g_skipmetadata == "false":
                tempwriter.append(child.get('tag'))
            elif child.tag == "Director" and g_skipmetadata == "false":
                tempdir.append(child.get('tag'))
            elif child.tag == "Role" and g_skipmetadata == "false":
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
                     'token': _PARAM_TOKEN,
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
        if g_skipmetadata == "false":
            details['cast'] = tempcast
            details['director'] = " / ".join(tempdir)
            details['writer'] = " / ".join(tempwriter)
            details['genre'] = " / ".join(tempgenre)

        # Add extra media flag data
        if g_skipmediaflags == "false":
            extraData.update(Media.getMediaData(mediaarguments))

        # Build any specific context menu entries
        if g_skipcontext == "false":
            context = GUI.buildContextMenu(url, extraData)
        else:
            context = None
        # http:// <server> <path> &mode=<mode> &t=<rnd>
        extraData['mode'] = _MODE_PLAYLIBRARY
        separator = "?"
        if "?" in extraData['key']:
            separator = "&"
        u = "http://%s%s%st=%s" % (server,
                                   extraData['key'], separator, randomNumber)

        GUI.addGUIItem(u, details, extraData, context, folder=False)
        return


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
        printDebug("== ENTER: enforceSkinView ==", False)

        if __settings__.getSetting('skinoverride') == "false":
            return None

        skinname = __settings__.getSetting('skinname')

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
            viewname = __settings__.getSetting('mo_view_%s' % skinname)

        elif mode == "tv":
            printDebug("Looking for tv skin settings")
            viewname = __settings__.getSetting('tv_view_%s' % skinname)

        elif mode == "music":
            printDebug("Looking for music skin settings")
            viewname = __settings__.getSetting('mu_view_%s' % skinname)

        elif mode == "episode":
            printDebug("Looking for music skin settings")
            viewname = __settings__.getSetting('ep_view_%s' % skinname)

        elif mode == "season":
            printDebug("Looking for music skin settings")
            viewname = __settings__.getSetting('se_view_%s' % skinname)

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

    @staticmethod
    def skin(server_list=None, type=None):
        # Gather some data and set the window properties
        printDebug("== ENTER: skin() ==", False)
        # Get the global host variable set in settings
        WINDOW = xbmcgui.Window(10000)

        sectionCount = 0
        serverCount = 0

        # XXX: Unused variable 'sharedCount'
        sharedCount = 0
        shared_flag = {}
        hide_shared = __settings__.getSetting('hide_shared')

        if server_list is None:
            server_list = PlexServers.discoverAll()

        # For each of the servers we have identified
        for section in Sections.getAllSections(server_list):

            extraData = {'fanart_image': Media.getFanart(section, section['address']),
                         'thumb': Media.getFanart(section, section['address'], False)}

            # Determine what we are going to do process after a link is
            # selected by the user, based on the content we find

            path = section['path']

            if section['type'] == 'show':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['show'] = True
                    continue
                window = "VideoLibrary"
                mode = _MODE_TVSHOWS
            if section['type'] == 'movie':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['movie'] = True
                    continue
                window = "VideoLibrary"
                mode = _MODE_MOVIES
            if section['type'] == 'artist':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['artist'] = True
                    continue
                window = "MusicFiles"
                mode = _MODE_ARTISTS
            if section['type'] == 'photo':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['photo'] = True
                    continue
                window = "Pictures"
                mode = _MODE_PHOTOS

            aToken = MyPlexServers.getAuthDetails(section)
            qToken = MyPlexServers.getAuthDetails(section, prefix='?')

            if g_secondary == "true":
                mode = _MODE_GETCONTENT
            else:
                path = path + '/all'

            s_url = 'http://%s%s&mode=%s%s' % (
                section['address'], path, mode, aToken)

            # Build that listing..
            WINDOW.setProperty("plexbmc.%d.title" %
                               (sectionCount), section['title'])
            WINDOW.setProperty("plexbmc.%d.subtitle" %
                               (sectionCount), section['serverName'])
            WINDOW.setProperty("plexbmc.%d.path" % (
                sectionCount), "ActivateWindow(" + window + ",plugin://plugin.video.plexbmc/?url=" + s_url + ",return)")
            WINDOW.setProperty(
                "plexbmc.%d.art" % (sectionCount), extraData['fanart_image'] + qToken)
            WINDOW.setProperty("plexbmc.%d.type" %
                               (sectionCount), section['type'])
            WINDOW.setProperty("plexbmc.%d.icon" %
                               (sectionCount), extraData['thumb'] + qToken)
            WINDOW.setProperty("plexbmc.%d.thumb" %
                               (sectionCount), extraData['thumb'] + qToken)
            WINDOW.setProperty("plexbmc.%d.partialpath" % (sectionCount), "ActivateWindow(" + window +
                               ",plugin://plugin.video.plexbmc/?url=http://" + section['address'] + section['path'])
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

            printDebug(
                "Building window properties index [" + str(sectionCount) + "] which is [" + section['title'] + "]")
            printDebug("PATH in use is: ActivateWindow(" + window +
                       ",plugin://plugin.video.plexbmc/?url=" + s_url + ",return)")
            sectionCount += 1

        if type == "nocat":
            WINDOW.setProperty("plexbmc.%d.title" %
                               (sectionCount), "Shared...")
            WINDOW.setProperty("plexbmc.%d.subtitle" %
                               (sectionCount), "Shared")
            WINDOW.setProperty(
                "plexbmc.%d.path" %
                (sectionCount),
                "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode=" +
                str(_MODE_SHARED_ALL) +
                ",return)")
            WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "movie")
            WINDOW.setProperty("plexbmc.%d.shared" % (sectionCount), "true")
            sectionCount += 1

        else:

            if shared_flag.get('movie'):
                WINDOW.setProperty("plexbmc.%d.title" %
                                   (sectionCount), "Shared...")
                WINDOW.setProperty("plexbmc.%d.subtitle" %
                                   (sectionCount), "Shared")
                WINDOW.setProperty(
                    "plexbmc.%d.path" %
                    (sectionCount),
                    "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode=" +
                    str(_MODE_SHARED_MOVIES) +
                    ",return)")
                WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "movie")
                WINDOW.setProperty(
                    "plexbmc.%d.shared" % (sectionCount), "true")
                sectionCount += 1

            if shared_flag.get('show'):
                WINDOW.setProperty("plexbmc.%d.title" %
                                   (sectionCount), "Shared...")
                WINDOW.setProperty("plexbmc.%d.subtitle" %
                                   (sectionCount), "Shared")
                WINDOW.setProperty(
                    "plexbmc.%d.path" %
                    (sectionCount),
                    "ActivateWindow(VideoLibrary,plugin://plugin.video.plexbmc/?url=/&mode=" +
                    str(_MODE_SHARED_SHOWS) +
                    ",return)")
                WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "show")
                WINDOW.setProperty(
                    "plexbmc.%d.shared" % (sectionCount), "true")
                sectionCount += 1

            if shared_flag.get('artist'):
                WINDOW.setProperty("plexbmc.%d.title" %
                                   (sectionCount), "Shared...")
                WINDOW.setProperty("plexbmc.%d.subtitle" %
                                   (sectionCount), "Shared")
                WINDOW.setProperty(
                    "plexbmc.%d.path" %
                    (sectionCount),
                    "ActivateWindow(MusicFiles,plugin://plugin.video.plexbmc/?url=/&mode=" +
                    str(_MODE_SHARED_MUSIC) +
                    ",return)")
                WINDOW.setProperty(
                    "plexbmc.%d.type" % (sectionCount), "artist")
                WINDOW.setProperty(
                    "plexbmc.%d.shared" % (sectionCount), "true")
                sectionCount += 1

            if shared_flag.get('photo'):
                WINDOW.setProperty("plexbmc.%d.title" %
                                   (sectionCount), "Shared...")
                WINDOW.setProperty("plexbmc.%d.subtitle" %
                                   (sectionCount), "Shared")
                WINDOW.setProperty(
                    "plexbmc.%d.path" %
                    (sectionCount),
                    "ActivateWindow(Pictures,plugin://plugin.video.plexbmc/?url=/&mode=" +
                    str(_MODE_SHARED_PHOTOS) +
                    ",return)")
                WINDOW.setProperty("plexbmc.%d.type" % (sectionCount), "photo")
                WINDOW.setProperty(
                    "plexbmc.%d.shared" % (sectionCount), "true")
                sectionCount += 1

        # For each of the servers we have identified
        numOfServers = len(server_list)

        for server in server_list.values():

            if server['class'] == "secondary":
                continue

            aToken = MyPlexServers.getAuthDetails(server)
            qToken = MyPlexServers.getAuthDetails(server, prefix='?')

            if g_channelview == "true":
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
                WINDOW.setProperty("plexbmc.%d.server.video" % (
                    serverCount), "http://" + server['server'] + ":" + server['port'] + "/video&mode=7" + aToken)
                WINDOW.setProperty("plexbmc.%d.server.music" % (
                    serverCount), "http://" + server['server'] + ":" + server['port'] + "/music&mode=17" + aToken)
                WINDOW.setProperty("plexbmc.%d.server.photo" % (
                    serverCount), "http://" + server['server'] + ":" + server['port'] + "/photos&mode=16" + aToken)

            WINDOW.setProperty("plexbmc.%d.server.online" % (serverCount), "http://" + server[
                               'server'] + ":" + server['port'] + "/system/plexonline&mode=19" + aToken)

            WINDOW.setProperty("plexbmc.%d.server" %
                               (serverCount), server['serverName'])
            printDebug("Name mapping is :" + server['serverName'])

            serverCount += 1

        # Clear out old data
        try:
            printDebug("Clearing properties from [" + str(
                sectionCount) + "] to [" + WINDOW.getProperty("plexbmc.sectionCount") + "]")

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

        printDebug(
            "Total number of skin sections is [" + str(sectionCount) + "]")
        printDebug("Total number of servers is [" + str(numOfServers) + "]")
        WINDOW.setProperty("plexbmc.sectionCount", str(sectionCount))
        WINDOW.setProperty("plexbmc.numServers", str(numOfServers))
        if __settings__.getSetting('myplex_user') != '':
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
        printDebug("== ENTER: amberskin() ==", False)
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
        hide_shared = __settings__.getSetting('hide_shared')

        server_list = PlexServers.discoverAll()
        printDebug(
            "Using list of " + str(len(server_list)) + " servers: " + str(server_list))

        # For each of the servers we have identified
        sections = Sections.getAllSections(server_list)
        printDebug("Total sections: " + str(len(sections)), False)

        listitems = list()

        for section in sections:
            printDebug("=Enter amberskin section=", False)
            printDebug(str(section), False)
            printDebug("=/section=", False)

            # XXX: Unused variable 'extraData'
            extraData = {'fanart_image': Media.getFanart(
                section, section['address']), 'thumb': g_thumb}

            # Determine what we are going to do process after a link is
            # selected by the user, based on the content we find
            path = section['path']

            if section['type'] == 'show':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['show'] = True
                    sharedCount += 1
                    continue
                window = "VideoLibrary"
                mode = _MODE_TVSHOWS
            elif section['type'] == 'movie':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['movie'] = True
                    sharedCount += 1
                    continue
                window = "VideoLibrary"
                mode = _MODE_MOVIES
            elif section['type'] == 'artist':
                if hide_shared == "true" and section.get('owned') == '0':
                    shared_flag['artist'] = True
                    sharedCount += 1
                    continue
                window = "MusicFiles"
                mode = _MODE_ARTISTS
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
                mode = _MODE_PHOTOS

            aToken = MyPlexServers.getAuthDetails(section)

            # XXX: Unused variable 'qToken'
            qToken = MyPlexServers.getAuthDetails(section, prefix='?')

            print 'g_secondary: %s' % g_secondary
            if g_secondary == "true":
                mode = _MODE_GETCONTENT
            else:
                path = path + '/all'

            # mode not working with directl server connect
            s_url = 'http://%s%s&mode=%s%s' % (
                section['address'], path, mode, aToken)

            #xbmcplugin.setContent(pluginhandle, 'movies')
            print 'Entering jason_test'
            # XXX:
            path = "plugin://plugin.video.plexbmc/?url={0}".format(s_url)
            partial_path = "plugin://plugin.video.plexbmc/?url=http://{0}{1}".format(
                section['address'], section['path'])

            path2 = "ActivateWindow({0},plugin://plugin.video.plexbmc/?url={1},return)".format(
                window, s_url)
            path3 = "ActivateWindow(" + window + \
                ",plugin://plugin.video.plexbmc/?url=" + s_url + ",return)"

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
            listitem.setProperty('partial', "ActivateWindow(" + window +
                                 ",plugin://plugin.video.plexbmc/?url=http://" + section['address'] + section['path'])
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
            WINDOW.clearProperty("plexbmc.%d.uuid"    % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.title"    % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.subtitle" % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.url"      % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.path"     % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.window"   % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.art"      % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.type"     % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.icon"     % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.thumb"    % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.recent"    % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.all"    % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.search"    % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.viewed"    % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.ondeck" % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.released" % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.shared"     % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.album"     % ( i ) )
            WINDOW.clearProperty("plexbmc.%d.year"     % ( i ) )

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
        info['label'] = __localize__(30098)
        info['label2'] = 'channels'
        info['iconImage'] = None
        info['thumbnailImage'] = "special://skin/backgrounds/Channels.jpg"
        #info['path'] = "plugin://plugin.video.plexbmc/?mode=22&amp;url=http://online%2fsystem%2fplugins%2fall"
        info[
            'path'] = "plugin://plugin.video.plexbmc/?mode=22&url=http://online%2fsystem%2fplugins%2fall"
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
                printDebug('Unable to getControl(%s)' % str(container_id))
            #xbmcplugin.addDirectoryItems(300, listitems)
            # xbmcplugin.endOfDirectory(handle=container_id)
        else:
            xbmcplugin.addDirectoryItems(pluginhandle, listitems)
            xbmcplugin.endOfDirectory(handle=pluginhandle)
            #xbmcplugin.endOfDirectory(pluginhandle, succeeded=True, updateListing=False, cacheToDisc=False)

    @staticmethod
    def fullShelf(server_list={}):
        # pylint: disable=E1103
        # Instance of 'dict' has no 'xxx' member

        # Gather some data and set the window properties
        printDebug("== ENTER: fullShelf ==", False)

        if __settings__.getSetting('homeshelf') == '3' or ((__settings__.getSetting('movieShelf') == "false" and __settings__.getSetting(
                'tvShelf') == "false" and __settings__.getSetting('musicShelf') == "false")):
            printDebug("Disabling all shelf items")
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
            server_list = PlexServers.discoverAll()

        if server_list == {}:
            xbmc.executebuiltin(
                "XBMC.Notification(Unable to see any media servers,)")
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

                global _PARAM_TOKEN
                _PARAM_TOKEN = server_details.get('token', '')
                aToken = MyPlexServers.getAuthDetails({'token': _PARAM_TOKEN})
                qToken = '?' + aToken

                sections = Sections.getAllSections(server_list)

                # XXX: Unused variable 'ra_log_count'
                ra_log_count = 1

                if __settings__.getSetting('homeshelf') == '0' or __settings__.getSetting('homeshelf') == '2':
                    '''
                    logfile = PLUGINPATH+"/_shelf_sections_.txt"
                    logfileh = open(logfile, "w")
                    logfileh.write(str(sections))
                    logfileh.close()
                    '''
                    for section in sections:
                        recent_url = section.get(
                            'address') + section.get("path") + "/recentlyAdded"
                        _PARAM_TOKEN = section.get('token', '')
                        tree = PlexServers.getURL(recent_url)
                        tree = etree.fromstring(tree)
                        _PARAM_TOKEN = server_details.get('token', '')
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
                            printDebug(
                                "PLEXBMC -> RecentlyAdded items not found on: " + recent_url, False)
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
                                    (__settings__.getSetting('hide_watched_recent_items') == 'true' and int(
                                        eachitem.get(
                                            "viewCount",
                                            0)) > 0)):
                                    pass
                                else:
                                    recent_list[full_count] = (
                                        eachitem, section.get('address'), aToken, qToken, libraryuuid)
                                    # use seasons as dict key so we can check
                                    ep_helper[key] = key
                                    full_count += 1
                                    ra_item_count += 1
                            else:
                                recent_list[full_count] = (
                                    eachitem, section.get('address'), aToken, qToken, libraryuuid)
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
                if __settings__.getSetting('homeshelf') == '1' or __settings__.getSetting('homeshelf') == '2':
                    for section in sections:
                        ondeck_url = section.get(
                            'address') + section.get("path") + "/onDeck"
                        _PARAM_TOKEN = section.get('token', '')
                        tree = PlexServers.getURL(ondeck_url)
                        tree = etree.fromstring(tree)
                        _PARAM_TOKEN = server_details.get('token', '')
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
                            print (
                                "PLEXBMC -> OnDeck items not found on: " + ondeck_url, False)
                            continue
                        deck_item_count = 1
                        libraryuuid = tree.attrib["librarySectionUUID"]
                        for eachitem in tree:
                            if deck_item_count > 15:
                                break
                            deck_item_count += 1
                            #libraryuuid = tree.attrib["librarySectionUUID"]
                            ondeck_list[full_count] = (
                                eachitem, section.get('address'), aToken, qToken, libraryuuid)
                            full_count += 1
        # For each of the servers we have identified
        for index in recent_list:
            media = recent_list[index][0]
            server_address = recent_list[index][1]
            aToken = recent_list[index][2]
            qToken = recent_list[index][3]
            libuuid = recent_list[index][4]

            if media.get('type', None) == "movie":
                printDebug("Found a recent movie entry: [%s]" % (
                    media.get('title', 'Unknown').encode('UTF-8'), ))
                if __settings__.getSetting('movieShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestMovie.1.Path")
                    continue
                if __settings__.getSetting('hide_watched_recent_items') == 'false' or media.get("viewCount", 0) == 0:
                    m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s" % (Utility.getLinkURL(
                        'http://' + server_address, media, server_address), _MODE_PLAYSHELF, randomNumber, aToken)
                    m_thumb = server_list.getShelfThumb(
                        media, server_address, seasonThumb=0) + aToken
                    if media.get('duration') > 0:
                        #movie_runtime = media.get('duration', '0')
                        movie_runtime = str(
                            int(float(media.get('duration')) / 1000 / 60))
                    else:
                        movie_runtime = ""
                    if media.get('rating') > 0:
                        movie_rating = str(
                            round(float(media.get('rating')), 1))
                    else:
                        movie_rating = ''

                    WINDOW.setProperty(
                        "Plexbmc.LatestMovie.%s.Path" % recentMovieCount, m_url)
                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.Title" % recentMovieCount, media.get(
                        'title', 'Unknown').encode('UTF-8'))
                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.Year" % recentMovieCount, media.get(
                        'year', '').encode('UTF-8'))
                    WINDOW.setProperty(
                        "Plexbmc.LatestMovie.%s.Rating" % recentMovieCount, movie_rating)
                    WINDOW.setProperty(
                        "Plexbmc.LatestMovie.%s.Duration" % recentMovieCount, movie_runtime)
                    WINDOW.setProperty(
                        "Plexbmc.LatestMovie.%s.Thumb" % recentMovieCount, m_thumb)
                    WINDOW.setProperty(
                        "Plexbmc.LatestMovie.%s.uuid" % recentMovieCount, libuuid.encode('UTF-8'))
                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.Plot" % recentMovieCount, media.get(
                        'summary', '').encode('UTF-8'))

                    m_genre = []

                    for child in media:
                        if child.tag == "Genre":
                            m_genre.append(child.get('tag'))
                        else:
                            continue

                    WINDOW.setProperty("Plexbmc.LatestMovie.%s.Genre" % recentMovieCount, ", ".join(
                        m_genre).encode('UTF-8'))

                    recentMovieCount += 1

                    printDebug("Building Recent window title: %s" %
                               media.get('title', 'Unknown').encode('UTF-8'))
                    printDebug("Building Recent window url: %s" % m_url)
                    printDebug("Building Recent window thumb: %s" % m_thumb)
                else:
                    continue
            elif media.get('type', None) == "season":
                printDebug("Found a recent season entry [%s]" % (
                    media.get('parentTitle', 'Unknown').encode('UTF-8'), ))

                if __settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
                    continue

                s_url = "ActivateWindow(VideoLibrary, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (
                    Utility.getLinkURL('http://' + server_address, media, server_address), _MODE_TVEPISODES, aToken)
                s_thumb = server_list.getShelfThumb(
                    media, server_address, seasonThumb=0) + aToken

                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.Path" % recentSeasonCount, s_url)
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.EpisodeTitle" % recentSeasonCount, '')
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeSeason" %
                                   recentSeasonCount, media.get('title', '').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.ShowTitle" % recentSeasonCount, media.get(
                    'parentTitle', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.Thumb" % recentSeasonCount, s_thumb)
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.uuid" % recentSeasonCount, media.get(
                    'librarySectionUUID', '').encode('UTF-8'))

                recentSeasonCount += 1

                printDebug("Building Recent window title: %s" %
                           media.get('parentTitle', 'Unknown').encode('UTF-8'))
                printDebug("Building Recent window url: %s" % s_url)
                printDebug("Building Recent window thumb: %s" % s_thumb)

            elif media.get('type') == "album":
                if __settings__.getSetting('musicShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestAlbum.1.Path")
                    continue
                printDebug("Found a recent album entry")

                s_url = "ActivateWindow(MusicFiles, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (
                    Utility.getLinkURL('http://' + server_address, media, server_address), _MODE_TRACKS, aToken)
                s_thumb = server_list.getShelfThumb(
                    media, server_address, seasonThumb=0) + aToken

                WINDOW.setProperty(
                    "Plexbmc.LatestAlbum.%s.Path" % recentMusicCount, s_url)
                WINDOW.setProperty("Plexbmc.LatestAlbum.%s.Title" % recentMusicCount, media.get(
                    'title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestAlbum.%s.Artist" % recentMusicCount, media.get(
                    'parentTitle', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestAlbum.%s.Thumb" % recentMusicCount, s_thumb)

                recentMusicCount += 1

                printDebug("Building Recent window title: %s" %
                           media.get('parentTitle', 'Unknown').encode('UTF-8'))
                printDebug("Building Recent window url: %s" % s_url)
                printDebug("Building Recent window thumb: %s" % s_thumb)

            elif media.get('type') == "photo":
                printDebug("Found a recent photo entry: [%s]" % (
                    media.get('title', 'Unknown').encode('UTF-8'), ))

                p_url = "ActivateWindow(Pictures, plugin://plugin.video.plexbmc/?url=http://%s%s&mode=%s%s,return" % (
                    server_address, "/recentlyAdded", _MODE_PHOTOS, aToken)
                p_thumb = server_list.getShelfThumb(
                    media, server_address, seasonThumb=0) + aToken

                WINDOW.setProperty(
                    "Plexbmc.LatestPhoto.%s.Path" % recentPhotoCount, p_url)
                WINDOW.setProperty("Plexbmc.LatestPhoto.%s.Title" % recentPhotoCount, media.get(
                    'title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestPhoto.%s.Thumb" % recentPhotoCount, p_thumb)

                recentPhotoCount += 1

                printDebug("Building Recent photo window title: %s" %
                           media.get('title', 'Unknown').encode('UTF-8'))
                printDebug("Building Recent photo window url: %s" % p_url)
                printDebug("Building Recent photo window thumb: %s" % p_thumb)
            elif media.get('type', None) == "episode":
                printDebug("Found an Recent episode entry [%s]" % (
                    media.get('title', 'Unknown').encode('UTF-8'), ))

                if __settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
                    continue

                s_url = "ActivateWindow(Videos, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (Utility.getLinkURL(
                    'http://' + server_address,
                    media,
                    server_address,
                    season_shelf=True),
                    _MODE_TVEPISODES,
                    aToken)
                s_thumb = server_list.getShelfThumb(
                    media, server_address, seasonThumb=1) + aToken

                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.Path" % recentSeasonCount, s_url)
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeTitle" %
                                   recentSeasonCount, media.get('title', '').encode('utf-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeNumber" %
                                   recentSeasonCount, media.get('index', '').encode('utf-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeSeason" % recentSeasonCount, media.get(
                    'parentIndex', '').encode('UTF-8') + '.' + media.get('index', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeSeasonNumber" %
                                   recentSeasonCount, media.get('parentIndex', '').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.ShowTitle" % recentSeasonCount, media.get(
                    'grandparentTitle', '').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.Thumb" % recentSeasonCount, s_thumb)
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.uuid" % recentSeasonCount, libuuid.encode('utf-8'))

                printDebug("Building RecentEpisode window title: %s" %
                           media.get('title', 'Unknown').encode('UTF-8'))
                printDebug("Building RecentEpisode window url: %s" % s_url)
                printDebug("Building RecentEpisode window thumb: %s" % s_thumb)

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
                printDebug("Found a OnDeck movie entry: [%s]" % (
                    media.get('title', 'Unknown').encode('UTF-8'), ))
                if __settings__.getSetting('movieShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.OnDeckMovie.1.Path")
                    continue

                m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s" % (Utility.getLinkURL(
                    'http://' + server_address, media, server_address), _MODE_PLAYSHELF, randomNumber, aToken)
                m_thumb = server_list.getShelfThumb(
                    media, server_address, seasonThumb=0) + aToken

                if media.get('duration') > 0:
                    #movie_runtime = media.get('duration', '0')
                    movie_runtime = str(
                        int(float(media.get('duration')) / 1000 / 60))
                else:
                    movie_runtime = ""

                if media.get('rating') > 0:
                    m_rating = str(round(float(media.get('rating')), 1))
                else:
                    m_rating = ''

                WINDOW.setProperty(
                    "Plexbmc.OnDeckMovie.%s.Path" % ondeckMovieCount, m_url)
                WINDOW.setProperty("Plexbmc.OnDeckMovie.%s.Title" % ondeckMovieCount, media.get(
                    'title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.OnDeckMovie.%s.Year" % ondeckMovieCount, media.get(
                    'year', '').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.OnDeckMovie.%s.Rating" % ondeckMovieCount, m_rating)
                WINDOW.setProperty(
                    "Plexbmc.OnDeckMovie.%s.Duration" % ondeckMovieCount, movie_runtime)
                WINDOW.setProperty(
                    "Plexbmc.OnDeckMovie.%s.Thumb" % ondeckMovieCount, m_thumb)
                WINDOW.setProperty(
                    "Plexbmc.OnDeckMovie.%s.uuid" % ondeckMovieCount, libuuid.encode('UTF-8'))

                ondeckMovieCount += 1

                printDebug("Building OnDeck Movie window title: %s" %
                           media.get('title', 'Unknown').encode('UTF-8'))
                printDebug("Building OnDeck Movie window url: %s" % m_url)
                printDebug("Building OnDeck Movie window thumb: %s" % m_thumb)

            elif media.get('type', None) == "season":
                printDebug("Found a OnDeck season entry [%s]" % (
                    media.get('parentTitle', 'Unknown').encode('UTF-8'), ))
                if __settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.OnDeckEpisode.1.Path")
                    continue

                s_url = "ActivateWindow(VideoLibrary, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (
                    Utility.getLinkURL('http://' + server_address, media, server_address), _MODE_TVEPISODES, aToken)
                s_thumb = server_list.getShelfThumb(
                    media, server_address, seasonThumb=0) + aToken

                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.Path" % ondeckSeasonCount, s_url)
                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.EpisodeTitle" % ondeckSeasonCount, '')
                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.EpisodeSeason" %
                                   ondeckSeasonCount, media.get('title', '').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.ShowTitle" % ondeckSeasonCount, media.get(
                    'parentTitle', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.Thumb" % ondeckSeasonCount, s_thumb)

                ondeckSeasonCount += 1

                printDebug("Building OnDeck window title: %s" %
                           media.get('parentTitle', 'Unknown').encode('UTF-8'))
                printDebug("Building OnDeck window url: %s" % s_url)
                printDebug("Building OnDeck window thumb: %s" % s_thumb)
            elif media.get('type', None) == "episode":
                printDebug("Found an onDeck episode entry [%s]" % (
                    media.get('title', 'Unknown').encode('UTF-8'), ))

                if __settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.OnDeckEpisode.1.Path")
                    continue

                s_url = "PlayMedia(plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s)" % (Utility.getLinkURL(
                    'http://' + server_address, media, server_address), _MODE_PLAYSHELF, randomNumber, aToken)
                # s_thumb="http://"+server_address+media.get('grandparentThumb','')
                s_thumb = server_list.getShelfThumb(
                    media, server_address, seasonThumb=1)

                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.Path" % ondeckSeasonCount, s_url)
                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.EpisodeTitle" %
                                   ondeckSeasonCount, media.get('title', '').encode('utf-8'))
                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.EpisodeNumber" %
                                   ondeckSeasonCount, media.get('index', '').encode('utf-8'))
                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.EpisodeSeason" % ondeckSeasonCount, media.get(
                    'grandparentTitle', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.EpisodeSeasonNumber" %
                                   ondeckSeasonCount, media.get('parentIndex', '').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.OnDeckEpisode.%s.ShowTitle" % ondeckSeasonCount, media.get(
                    'title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.Thumb" % ondeckSeasonCount, s_thumb + aToken)
                WINDOW.setProperty(
                    "Plexbmc.OnDeckEpisode.%s.uuid" % ondeckSeasonCount, libuuid.encode('UTF-8'))

                ondeckSeasonCount += 1

                printDebug("Building OnDeck window title: %s" %
                           media.get('title', 'Unknown').encode('UTF-8'))
                printDebug("Building OnDeck window url: %s" % s_url)
                printDebug("Building OnDeck window thumb: %s" % s_thumb)

        server_list.clearOnDeckShelf(ondeckMovieCount, ondeckSeasonCount)

        if __settings__.getSetting('channelShelf') == "true" or __settings__.getSetting('homeshelf') != '3':
            server_list.shelfChannel(server_list)
        else:
            printDebug("Disabling channel shelf items")
            server_list.clearChannelShelf()

    @staticmethod
    def shelf(server_list=None):
        # pylint: disable=E1103
        # Instance of 'dict' has no 'xxx' member

        # Gather some data and set the window properties
        printDebug("== ENTER: shelf() ==", False)

        if (__settings__.getSetting('movieShelf') == "false" and __settings__.getSetting('tvShelf') == "false" and
                __settings__.getSetting('musicShelf') == "false") or __settings__.getSetting('homeshelf') == '3':
            printDebug("Disabling all shelf items")
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
            server_list = PlexServers.discoverAll()

        if server_list == {}:
            xbmc.executebuiltin(
                "XBMC.Notification(Unable to see any media servers,)")
            server_list.clearShelf(0, 0, 0)
            return

        if __settings__.getSetting('homeshelf') == '0' or __settings__.getSetting('homeshelf') == '2':
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

            global _PARAM_TOKEN
            _PARAM_TOKEN = server_details.get('token', '')
            aToken = MyPlexServers.getAuthDetails({'token': _PARAM_TOKEN})
            qToken = MyPlexServers.getAuthDetails(
                {'token': _PARAM_TOKEN}, prefix='?')

            tree = Utility.getXML(
                'http://' + server_details['server'] + ":" + server_details['port'] + endpoint)
            if tree is None:
                xbmc.executebuiltin(
                    "XBMC.Notification(Unable to contact server: " + server_details['serverName'] + ",)")
                server_list.clearShelf()
                return

            for eachitem in tree:
                if direction:
                    added_list[int(eachitem.get('addedAt', 0))] = (
                        eachitem, server_details['server'] + ":" + server_details['port'], aToken, qToken)
                else:
                    added_list[full_count] = (
                        eachitem, server_details['server'] + ":" + server_details['port'], aToken, qToken)
                    full_count += 1

        library_filter = __settings__.getSetting('libraryfilter')
        acceptable_level = __settings__.getSetting('contentFilter')

        # For each of the servers we have identified
        for index in sorted(added_list, reverse=direction):
            media = added_list[index][0]
            server_address = added_list[index][1]
            aToken = added_list[index][2]
            qToken = added_list[index][3]

            if media.get('type', None) == "movie":
                printDebug("Found a recent movie entry: [%s]" % (
                    media.get('title', 'Unknown').encode('UTF-8'), ))

                if __settings__.getSetting('movieShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestMovie.1.Path")
                    continue
                if not Utility.displayContent(acceptable_level, media.get('contentRating')):
                    continue
                if media.get('librarySectionID') == library_filter:
                    printDebug("SKIPPING: Library Filter match: %s = %s " % (
                        library_filter, media.get('librarySectionID')))
                    continue

                m_url = "plugin://plugin.video.plexbmc?url=%s&mode=%s&t=%s%s" % (Utility.getLinkURL(
                    'http://' + server_address, media, server_address), _MODE_PLAYSHELF, randomNumber, aToken)
                m_thumb = Media.getThumb(media, server_address)

                WINDOW.setProperty(
                    "Plexbmc.LatestMovie.%s.Path" % movieCount, m_url)
                WINDOW.setProperty("Plexbmc.LatestMovie.%s.Title" % movieCount, media.get(
                    'title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestMovie.%s.Thumb" % movieCount, m_thumb + qToken)

                movieCount += 1

                printDebug("Building Recent window title: %s" %
                           media.get('title', 'Unknown').encode('UTF-8'))
                printDebug("Building Recent window url: %s" % m_url)
                printDebug("Building Recent window thumb: %s" % m_thumb)
            elif media.get('type', None) == "season":
                printDebug("Found a recent season entry [%s]" % (
                    media.get('parentTitle', 'Unknown').encode('UTF-8'), ))

                if __settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
                    continue

                s_url = "ActivateWindow(VideoLibrary, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (
                    Utility.getLinkURL('http://' + server_address, media, server_address), _MODE_TVEPISODES, aToken)
                s_thumb = Media.getThumb(media, server_address)

                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.Path" % seasonCount, s_url)
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.EpisodeTitle" % seasonCount, '')
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeSeason" % seasonCount, media.get(
                    'title', '').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.ShowTitle" % seasonCount, media.get(
                    'parentTitle', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.Thumb" % seasonCount, s_thumb + qToken)
                seasonCount += 1

                printDebug("Building Recent window title: %s" %
                           media.get('parentTitle', 'Unknown').encode('UTF-8'))
                printDebug("Building Recent window url: %s" % s_url)
                printDebug("Building Recent window thumb: %s" % s_thumb)
            elif media.get('type') == "album":
                if __settings__.getSetting('musicShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestAlbum.1.Path")
                    continue
                printDebug("Found a recent album entry")

                s_url = "ActivateWindow(MusicFiles, plugin://plugin.video.plexbmc?url=%s&mode=%s%s, return)" % (
                    Utility.getLinkURL('http://' + server_address, media, server_address), _MODE_TRACKS, aToken)
                s_thumb = Media.getThumb(media, server_address)

                WINDOW.setProperty(
                    "Plexbmc.LatestAlbum.%s.Path" % musicCount, s_url)
                WINDOW.setProperty("Plexbmc.LatestAlbum.%s.Title" % musicCount, media.get(
                    'title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestAlbum.%s.Artist" % musicCount, media.get(
                    'parentTitle', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestAlbum.%s.Thumb" % musicCount, s_thumb + qToken)
                musicCount += 1

                printDebug("Building Recent window title: %s" %
                           media.get('parentTitle', 'Unknown').encode('UTF-8'))
                printDebug("Building Recent window url: %s" % s_url)
                printDebug("Building Recent window thumb: %s" % s_thumb)

            elif media.get('type', None) == "episode":
                printDebug("Found an onDeck episode entry [%s]" % (
                    media.get('title', 'Unknown').encode('UTF-8'), ))

                if __settings__.getSetting('tvShelf') == "false":
                    WINDOW.clearProperty("Plexbmc.LatestEpisode.1.Path")
                    continue

                s_url = "PlayMedia(plugin://plugin.video.plexbmc?url=%s&mode=%s%s)" % (Utility.getLinkURL(
                    'http://' + server_address, media, server_address), _MODE_PLAYSHELF, aToken)
                s_thumb = "http://" + server_address + \
                    media.get('grandparentThumb', '')

                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.Path" % seasonCount, s_url)
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeTitle" % seasonCount, media.get(
                    'title', '').encode('utf-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.EpisodeSeason" % seasonCount, media.get(
                    'grandparentTitle', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty("Plexbmc.LatestEpisode.%s.ShowTitle" % seasonCount, media.get(
                    'title', 'Unknown').encode('UTF-8'))
                WINDOW.setProperty(
                    "Plexbmc.LatestEpisode.%s.Thumb" % seasonCount, s_thumb + qToken)
                seasonCount += 1

                printDebug("Building Recent window title: %s" %
                           media.get('title', 'Unknown').encode('UTF-8'))
                printDebug("Building Recent window url: %s" % s_url)
                printDebug("Building Recent window thumb: %s" % s_thumb)

        server_list.clearShelf(movieCount, seasonCount, musicCount)

    @staticmethod
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
                WINDOW.clearProperty(
                    "Plexbmc.LatestEpisode.%s.EpisodeTitle" % (i))
                WINDOW.clearProperty(
                    "Plexbmc.LatestEpisode.%s.EpisodeSeason" % (i))
                WINDOW.clearProperty(
                    "Plexbmc.LatestEpisode.%s.ShowTitle" % (i))
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

    @staticmethod
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
                WINDOW.clearProperty(
                    "Plexbmc.OnDeckEpisode.%s.EpisodeTitle" % (i))
                WINDOW.clearProperty(
                    "Plexbmc.OnDeckEpisode.%s.EpisodeSeason" % (i))
                WINDOW.clearProperty(
                    "Plexbmc.OnDeckEpisode.%s.ShowTitle" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckEpisode.%s.Thumb" % (i))
                WINDOW.clearProperty("Plexbmc.OnDeckEpisode.%s.uuid" % (i))
            printDebug("Done clearing On Deck tv")
        except:
            pass

        return

    @staticmethod
    def shelfChannel(server_list=None):
        # pylint: disable=E1103
        # Instance of 'dict' has no 'xxx' member

        # Gather some data and set the window properties
        printDebug("== ENTER: shelfChannels() ==", False)

        if __settings__.getSetting('channelShelf') == "false" or __settings__.getSetting('homeshelf') == '3':
            printDebug("Disabling channel shelf")
            server_list.clearChannelShelf()
            return

        # Get the global host variable set in settings
        WINDOW = xbmcgui.Window(10000)

        channelCount = 1

        if server_list is None:
            server_list = PlexServers.discoverAll()

        if server_list == {}:
            xbmc.executebuiltin(
                "XBMC.Notification(Unable to see any media servers,)")
            server_list.clearChannelShelf()
            return

        for server_details in server_list.values():
            if server_details['class'] == "secondary":
                continue

            if not server_details['owned'] == '1':
                continue

            global _PARAM_TOKEN
            _PARAM_TOKEN = server_details.get('token', '')
            aToken = MyPlexServers.getAuthDetails({'token': _PARAM_TOKEN})

            # XXX: Unused variable 'qToken'
            qToken = MyPlexServers.getAuthDetails({'token': _PARAM_TOKEN}, prefix='?')

            if __settings__.getSetting('channelShelf') == "false" or __settings__.getSetting('homeshelf') == '3':
                WINDOW.clearProperty("Plexbmc.LatestChannel.1.Path")
                return

            tree = Utility.getXML(
                'http://' + server_details['server'] + ":" + server_details['port'] + '/channels/recentlyViewed')
            if tree is None:
                xbmc.executebuiltin(
                    "XBMC.Notification(Unable to contact server: " + server_details['serverName'] + ",)")
                server_list.clearChannelShelf(0)
                return

            # For each of the servers we have identified
            for media in tree:
                printDebug("Found a recent channel entry")
                suffix = media.get('key').split('/')[1]

                if suffix == "photos":
                    mode = _MODE_PHOTOS
                    channel_window = "Pictures"
                elif suffix == "video":
                    mode = _MODE_PLEXPLUGINS
                    channel_window = "VideoLibrary"
                elif suffix == "music":
                    mode = _MODE_MUSIC
                    channel_window = "MusicFiles"
                else:
                    mode = _MODE_GETCONTENT
                    channel_window = "VideoLibrary"

                c_url = "ActivateWindow(%s, plugin://plugin.video.plexbmc?url=%s&mode=%s%s)" % (channel_window,
                                                                                                Utility.getLinkURL(
                                                                                                    'http://' + server_details['server'] + ":" + server_details['port'],
                                                                                                    media,
                                                                                                    server_details['server'] + ":" + server_details['port']),
                                                                                                mode,
                                                                                                aToken)
                pms_thumb = str(media.get('thumb', ''))

                if pms_thumb.startswith('/'):
                    c_thumb = 'http://' + \
                        server_details['server'] + ":" + \
                        server_details['port'] + pms_thumb
                else:
                    c_thumb = pms_thumb

                WINDOW.setProperty(
                    "Plexbmc.LatestChannel.%s.Path" % channelCount, c_url)
                WINDOW.setProperty(
                    "Plexbmc.LatestChannel.%s.Title" % channelCount, media.get('title', 'Unknown'))
                WINDOW.setProperty(
                    "Plexbmc.LatestChannel.%s.Thumb" % channelCount, c_thumb + aToken)

                channelCount += 1

                printDebug("Building Recent window title: %s" %
                           media.get('title', 'Unknown'))
                printDebug("Building Recent window url: %s" % c_url)
                printDebug("Building Recent window thumb: %s" % c_thumb)

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
            printDebug("Done clearing channels")
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
            printDebug("Done clearing Queue shelf")
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
            thumbnail = data.get('grandparentThumb', '').split(
                '?t')[0].encode('utf-8')

        else:
            thumbnail = data.get('thumb', '').split('?t')[0].encode('utf-8')

        if thumbnail == '':
            return g_thumb

        elif thumbnail[0:4] == "http":
            return thumbnail

        elif thumbnail[0] == '/':
            if __settings__.getSetting("fullres_thumbs") != "false":
                return 'http://' + server + thumbnail

            else:
                return Utility.photoTranscode(server, 'http://localhost:32400' + thumbnail, width, height)

        else:
            return g_thumb


def jason_test():
    listitems = list()
    #self.section = 'Hey there'
    xbmcplugin.setContent(pluginhandle, 'movies')
    #self.parse_movies( 'recentmovies', 32005, listitems )
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
    xbmcplugin.addDirectoryItems(pluginhandle, listitems)
    xbmcplugin.endOfDirectory(handle=pluginhandle)
    print 'Finish jason_test'  # So this is where we really start the plugin.


def main():
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

    params = Utility.get_params(sys.argv)

    # Now try and assign some data to them
    param_url = params.get('url', None)
    if param_url and (param_url.startswith('http') or param_url.startswith('file')):
        param_url = urllib.unquote(param_url)

    param_name = urllib.unquote_plus(params.get('name', ''))
    param_indirect = params.get('indirect', None)
    param_identifier = params.get('identifier', None)
    param_transcodeOverride = int(params.get('transcode', 0))
    _PARAM_TOKEN = params.get('X-Plex-Token', None)

    global pluginhandle
    pluginhandle = None if not (
        len(sys.argv) >= 1 and sys.argv[1].isdigit()) else int(sys.argv[1])
    mode = - \
        1 if not params.get('mode', '').isdigit() else int(params.get('mode'))
    force = params.get('force', False)
    content = params.get('content', None)

    if content:
        # Don't overwrite contents, append it
        container_id = None if not params.get(
            'append', '').isdigit() else int(params.get('append'))

        if 'sections' in content:
            Skin.amberskin(container_id)
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
        Skin.shelf()

    # Populate both recently AND on deck shelf items
    elif str(sys.argv[1]) == "fullshelf":
        Skin.fullShelf()

    # Populate channel recently viewed items
    elif str(sys.argv[1]) == "channelShelf":
        Skin.shelfChannel()

    # Send a library update to Plex
    elif sys.argv[1] == "update":
        url = sys.argv[2]
        Commands.libraryRefresh(url)

    # Mark an item as watched/unwatched in plex
    elif sys.argv[1] == "watch":
        url = sys.argv[2]
        Commands.watched(url)

    # Open the add-on settings page, then refresh plugin
    elif sys.argv[1] == "setting":
        __settings__.openSettings()
        WINDOW = xbmcgui.getCurrentWindowId()
        if WINDOW == 10000:
            printDebug(
                "Currently in home - refreshing to allow new settings to be taken")
            xbmc.executebuiltin("XBMC.ActivateWindow(Home)")

    # nt currently used
    elif sys.argv[1] == "refreshplexbmc":
        server_list = PlexServers.discoverAll()
        Skin.skin(server_list)
        Skin.shelf(server_list)
        Skin.shelfChannel(server_list)

    # delete media from PMS
    elif sys.argv[1] == "delete":
        url = sys.argv[2]
        Commands.deleteMedia(url)

    # Refresh the current XBMC listing
    elif sys.argv[1] == "refresh":
        xbmc.executebuiltin("Container.Refresh")

    # Display subtitle selection screen
    elif sys.argv[1] == "subs":
        url = sys.argv[2]
        Commands.alterSubs(url)

    # Display audio streanm selection screen
    elif sys.argv[1] == "audio":
        url = sys.argv[2]
        Commands.alterAudio(url)

    # Allow a mastre server to be selected (for myplex queue)
    elif sys.argv[1] == "master":
        PlexServers.setMasterServer()

    # Delete cache and refresh it
    elif str(sys.argv[1]) == "cacherefresh":
        Cache.delete()
        xbmc.executebuiltin("ReloadSkin()")

    # XXX  WE be sending non ints for some reason
    # elif not str(sys.argv[1]).isdigit():
    #    pass

    # else move to the main code
    elif pluginhandle:
       #pluginhandle = int(sys.argv[1])

        WINDOW = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        WINDOW.clearProperty("heading")
        WINDOW.clearProperty("heading2")

        if g_debug == "true":
            print "PleXBMC -> Mode: " + str(mode)
            print "PleXBMC -> URL: " + str(param_url)
            print "PleXBMC -> Name: " + str(param_name)
            print "PleXBMC -> identifier: " + str(param_identifier)
            print "PleXBMC -> token: " + str(_PARAM_TOKEN)

        # Run a function based on the mode variable that was passed in the URL
        if (mode is None) or (param_url is None) or (len(param_url) < 1):
            Sections.displaySections()

        elif mode == _MODE_GETCONTENT:
            Media.getContent(param_url)

        elif mode == _MODE_TVSHOWS:
            GUI.TVShows(param_url)

        elif mode == _MODE_MOVIES:
            xbmcplugin.addSortMethod(
                pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
            GUI.Movies(param_url)

        elif mode == _MODE_ARTISTS:
            GUI.artist(param_url)

        elif mode == _MODE_TVSEASONS:
            GUI.TVSeasons(param_url)

        elif mode == _MODE_PLAYLIBRARY:
            Commands.playLibraryMedia(
                param_url, force=force, override=param_transcodeOverride)

        elif mode == _MODE_PLAYSHELF:
            Commands.playLibraryMedia(param_url, full_data=True, shelf=True)

        elif mode == _MODE_TVEPISODES:
            GUI.TVEpisodes(param_url)

        elif mode == _MODE_PLEXPLUGINS:
            OtherModes.PlexPlugins(param_url)

        elif mode == _MODE_PROCESSXML:
            Utility.processXML(param_url)

        elif mode == _MODE_BASICPLAY:
            Commands.PLAY(param_url)

        elif mode == _MODE_ALBUMS:
            GUI.albums(param_url)

        elif mode == _MODE_TRACKS:
            GUI.tracks(param_url)

        elif mode == _MODE_PHOTOS:
            GUI.photo(param_url)

        elif mode == _MODE_MUSIC:
            GUI.music(param_url)

        elif mode == _MODE_VIDEOPLUGINPLAY:
            Commands.videoPluginPlay(
                param_url, param_identifier, param_indirect)

        elif mode == _MODE_PLEXONLINE:
            OtherModes.plexOnline(param_url)

        elif mode == _MODE_CHANNELINSTALL:
            OtherModes.install(param_url, param_name)

        elif mode == _MODE_CHANNELVIEW:
            OtherModes.channelView(param_url)

        elif mode == _MODE_DISPLAYSERVERS:
            OtherModes.displayServers(param_url)

        elif mode == _MODE_PLAYLIBRARY_TRANSCODE:
            Commands.playLibraryMedia(param_url, override=True)

        elif mode == _MODE_MYPLEXQUEUE:
            OtherModes.myPlexQueue()

        elif mode == _MODE_CHANNELSEARCH:
            OtherModes.channelSearch(param_url, params.get('prompt'))

        elif mode == _MODE_CHANNELPREFS:
            OtherModes.channelSettings(param_url, params.get('id'))

        elif mode == _MODE_SHARED_MOVIES:
            Sections.displaySections(filter="movies", shared=True)

        elif mode == _MODE_SHARED_SHOWS:
            Sections.displaySections(filter="tvshows", shared=True)

        elif mode == _MODE_SHARED_PHOTOS:
            Sections.displaySections(filter="photos", shared=True)

        elif mode == _MODE_SHARED_MUSIC:
            Sections.displaySections(filter="music", shared=True)

        elif mode == _MODE_SHARED_ALL:
            Sections.displaySections(shared=True)

        elif mode == _MODE_DELETE_REFRESH:
            Cache.delete()
            xbmc.executebuiltin("Container.Refresh")

# Run
wake_on_lan()
nas_override()
main()

print "===== PLEXBMC STOP ====="
# Clear done and exit.
sys.modules.clear()
