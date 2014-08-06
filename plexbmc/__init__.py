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
import xbmc  # pylint: disable=F0401
import xbmcaddon  # pylint: disable=F0401

# If DEBUG/DEBUG_DEV == None, skin settings will be used.  Otherwise
# override the skin settings by setting to True or False
DEBUG = None
DEBUG_DEV = None

# Get the setting from the appropriate file.
DEFAULT_PORT = "32400"
#MYPLEX_SERVER = "my.plexapp.com"
MYPLEX_SERVER = "plex.tv"
TOKEN = 'X-Plex-Token'

# g_loc = PLUGINPATH   * Does not work right, why? *
LOC = "special://home/addons/plugin.video.plexbmc"
THUMB = "special://home/addons/plugin.video.plexbmc/resources/thumb.png"

# Create the standard header structure and load with a User Agent to
# ensure we get back a response.
#
# XXX: Unused variable 'TX_HEADERS' (was 'g_txheaders')
TX_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US;rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3 ( .NET CLR 3.5.30729)',
}


__addon__ = xbmcaddon.Addon()
__plugin__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__icon__ = __addon__.getAddonInfo('icon')
__cachedir__ = __addon__.getAddonInfo('profile')
__settings__ = xbmcaddon.Addon(id='plugin.video.plexbmc')
__localize__ = __addon__.getLocalizedString
__cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')

BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib'))
sys.path.insert(1, BASE_RESOURCE_PATH)

PLUGINPATH = xbmc.translatePath(os.path.join(__cwd__))
CACHE_DATA = __cachedir__
PLEXBMC_VERSION = __version__

MODE_GETCONTENT = 0
MODE_TVSHOWS = 1
MODE_MOVIES = 2
MODE_ARTISTS = 3
MODE_TVSEASONS = 4
MODE_PLAYLIBRARY = 5
MODE_TVEPISODES = 6
MODE_PLEXPLUGINS = 7
MODE_PROCESSXML = 8
MODE_CHANNELSEARCH = 9
MODE_CHANNELPREFS = 10
MODE_PLAYSHELF = 11
MODE_BASICPLAY = 12
MODE_SHARED_MOVIES = 13
MODE_ALBUMS = 14
MODE_TRACKS = 15
MODE_PHOTOS = 16
MODE_MUSIC = 17
MODE_VIDEOPLUGINPLAY = 18
MODE_PLEXONLINE = 19
MODE_CHANNELINSTALL = 20
MODE_CHANNELVIEW = 21
MODE_DISPLAYSERVERS = 22
MODE_PLAYLIBRARY_TRANSCODE = 23
MODE_MYPLEXQUEUE = 24
MODE_SHARED_SHOWS = 25
MODE_SHARED_MUSIC = 26
MODE_SHARED_PHOTOS = 27
MODE_DELETE_REFRESH = 28
MODE_SHARED_ALL = 29

SUB_AUDIO_XBMC_CONTROL = "0"
SUB_AUDIO_PLEX_CONTROL = "1"
SUB_AUDIO_NEVER_SHOW = "2"


def settings(name):
    '''
    Normalize xbmcaddon.Addon settings lookup
    '''
    setting = __settings__.getSetting(name)

    if setting.lower() == 'true':
        return True
    elif setting.lower() == 'false':
        return False
    else:
        return setting

DEBUG = settings('debug') if DEBUG is None else DEBUG
DEBUG_DEV = settings('debug_dev') if DEBUG_DEV is None else DEBUG_DEV

# Check debug first...
# elementtree imports. If debugging on, use python elementtree, as c implementation
# is horrible for debugging.
if DEBUG:
    import xml.etree.ElementTree as etree
    print("PleXBMC -> Running with built-in ElemenTree (debug).")
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
                print("PleXBMC -> Failed to import ElementTree from any known place")


def printDebug(msg, function_name=True):
    if DEBUG:
        if function_name is False:
            print str(msg)
        else:
            print "PleXBMC -> " + inspect.stack()[1][3] + ": " + str(msg)


def printDev(msg, function_name=True):
    if DEBUG_DEV:
        if function_name is False:
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


def WakeOnLan():
    # Next Check the WOL status - lets give the servers as much time as
    # possible to come up
    wolon = settings('wolon')
    if wolon:
        from WOL import wake_on_lan
        printDebug("PleXBMC -> Wake On LAN: %s" % wolon, False)
        for i in range(1, 12):
            wakeserver = settings('wol' + str(i))
            #if not wakeserver == "":
            if wakeserver:
                try:
                    printDebug("PleXBMC -> Waking server " + str(i) + " with MAC: " + wakeserver, False)
                    wake_on_lan(wakeserver)
                except ValueError:
                    printDebug("PleXBMC -> Incorrect MAC address format for server " + str(i), False)
                except:
                    printDebug("PleXBMC -> Unknown wake on lan error", False)


class _Nas:
    override = False
    override_ip = None
    root = None

    def __init__(self):
        self.test = 'updated'
        # NAS Override
        self.override = settings('nasoverride')
        printDebug("PleXBMC -> SMB IP Override: %s" % self.override, False)
        if self.override:
            self.override_ip = settings('nasoverrideip')
            if self.override_ip:
                printDebug("PleXBMC -> NAS IP: " + self.override_ip, False)
            else:
                printDebug("PleXBMC -> No NAS IP Specified.  Ignoring setting")

            self.root = settings('nasroot')

PLEXBMC_PLATFORM = getPlatform()
etree = etree
nas = _Nas()
