import time
import xbmcvfs  # pylint: disable=F0401
from plexbmc import settings, printDebug, CACHE_DATA

try:
    import cPickle as pickle
except ImportError:
    import pickle


def read(cachefile):
    if not settings('cache'):
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


def write(cachefile, object):
    if not settings('cache'):
        return True

    printDebug("CACHE [%s]: Writing file" % cachefile)
    cache = xbmcvfs.File(cachefile, 'w')
    cache.write(pickle.dumps(object))
    cache.close()
    return True


def check(cachefile, life=3600):
    if not settings('cache'):
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

            return read(cachefile)
    else:
        printDebug("CACHE [%s]: does not exist" % cachefile)

    return (False, None)


def delete():
    printDebug("== ENTER: deleteCache ==", False)

    # cache_header=".cache.directory"
    cache_suffix = "cache"
    dirs, files = xbmcvfs.listdir(CACHE_DATA)

    printDebug("List of file: [%s]" % files)
    printDebug("List of dirs: [%s]" % dirs)

    for i in files:
        if cache_suffix not in i:
            continue

        success = xbmcvfs.delete(CACHE_DATA + i)
        if success:
            printDebug("SUCCESSFUL: removed %s" % i)
        else:
            printDebug("UNSUCESSFUL: did not remove %s" % i)
