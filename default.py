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
import sys
#import os
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from plexbmc import settings, printDebug, DEBUG, PLEXBMC_PLATFORM, PLEXBMC_VERSION
import plexbmc
import plexbmc.main

print "===== PLEXBMC START ====="
print "PleXBMC -> Running Python: " + str(sys.version_info)
print "PleXBMC -> Running PleXBMC: " + str(PLEXBMC_VERSION)
print "PleXBMC -> FullRes Thumbs are set to: %s" % settings("fullres_thumbs")
print "PleXBMC -> CWD is set to: " + plexbmc.__cwd__
print "PleXBMC -> Platform: " + str(PLEXBMC_PLATFORM)

if DEBUG:
    print "PleXBMC -> Settings streaming: " + plexbmc.servers.PlexServers.getStreaming()
    print "PleXBMC -> Setting filter menus: %s" % settings('secondary')
    print "PleXBMC -> Setting debug to %s" % DEBUG
    if settings('streamControl') == plexbmc.SUB_AUDIO_XBMC_CONTROL:
        print "PleXBMC -> Setting stream Control to : XBMC CONTROL (%s)" % settings('streamControl')
    elif settings('streamControl') == plexbmc.SUB_AUDIO_PLEX_CONTROL:
        print "PleXBMC -> Setting stream Control to : PLEX CONTROL (%s)" % settings('streamControl')
    elif settings('streamControl') == plexbmc.SUB_AUDIO_NEVER_SHOW:
        print "PleXBMC -> Setting stream Control to : NEVER SHOW (%s)" % settings('streamControl')
    print "PleXBMC -> Force DVD playback: %s" % settings('forcedvd')
else:
    print "PleXBMC -> Debug is turned off.  Running silent"

printDebug("PleXBMC -> Flatten is: " + settings('flatten'), False)

# Run
plexbmc.WakeOnLan()
plexbmc.main.PleXBMC()
# plexbmc.main.PleXBMC.reset()  # Dunno if we really need this since we gc the module anyway

print "===== PLEXBMC STOP ====="

# clear done and exit.
sys.modules.clear()
