import codecs
import xbmcvfs
from plexbmc import printDebug, DEBUG
import plexbmc


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
    if not text:
        printDebug("PleXBMC -> Failed to convert XML: %s" % text, True)
        return None
    try:
        elem = etree.fromstring(text)
    except (etree.ParseError, TypeError) as e:
        printDebug("PleXBMC -> Failed to convert XML: %s\nERROR: %s" % (text, e), True)
        return None
    return elem

