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

# from plexbmc import main
# main.wake_on_lan()
# main.nas_override()
# main.main()

# Run
import plexbmc
from plexbmc import main
plexbmc.wake_on_lan()
plexbmc.nas_override()
main.PleXBMC()
main.PleXBMC.reset()  # Dunno if we really need this since we gc the module anyway

print "===== PLEXBMC STOP ====="

# clear done and exit.
sys.modules.clear()
