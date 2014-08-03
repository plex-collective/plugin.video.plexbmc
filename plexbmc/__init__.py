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

import inspect
import os
import sys
import time
import xbmc  # pylint: disable=F0401
import xbmcaddon  # pylint: disable=F0401
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
__cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')

BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib'))
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

g_secondary = __settings__.getSetting('secondary')
g_streamControl = __settings__.getSetting('streamControl')
g_channelview = __settings__.getSetting('channelview')
g_flatten = __settings__.getSetting('flatten')
printDebug("PleXBMC -> Flatten is: " + g_flatten, False)
g_forcedvd = __settings__.getSetting('forcedvd')

'''
if g_debug == "true":
    print "PleXBMC -> Settings streaming: " + plexbmc.servers.PlexServers.getStreaming()
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
'''


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


class Cache:
    '''
    '''
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

class _Nas:
    '''
    '''
    override = 'false'
    override_ip = None
    root = None
    test = 'default'

    def __init__(self):
        self.test = 'updated'
        # NAS Override
        self.override = __settings__.getSetting('nasoverride')
        printDebug("PleXBMC -> SMB IP Override: " + self.override, False)
        if self.override == "true":
            self.override_ip = __settings__.getSetting('nasoverrideip')
            if self.override_ip == "":
                printDebug("PleXBMC -> No NAS IP Specified.  Ignoring setting")
            else:
                printDebug("PleXBMC -> NAS IP: " + self.override_ip, False)

            self.override_ip = __settings__.getSetting('nasroot')

nas = _Nas()
