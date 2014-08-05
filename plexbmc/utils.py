import codecs
import xbmcvfs
from plexbmc import printDebug, etree

try:
    from codecs import BOM_UTF8
except ImportError:
    # only available since Python 2.3
    BOM_UTF8 = '\xef\xbb\xbf'


def readFile(name):
    try:
        file_ = xbmcvfs.File(name, "r")
        content = unicode(file_.read().strip(BOM_UTF8), "UTF-8")
        file_.close()

        if not content:
            printDebug("PleXBMC -> File is empty: %s" % name, True)
            content = None
    except:
        content = None
        printDebug("PleXBMC -> Failed to open/read file: %s" % name, True)
        try: file_.close(self)
        except: pass

    return content


def convertTextToXML(text):
    try:
        elem = etree.fromstring(text)
    except plexbmc.etree.ParseError:
        printDebug("PleXBMC -> Failed to convert XML: %s" % text, True)
        return None
    return elem

