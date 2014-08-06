#from __future__ import absolute_import
#import pkg_resources
import sys
import os
import urlparse
import urllib
import re
import random
#import xbmc  # pylint: disable=F0401
#import xbmcgui  # pylint: disable=F0401
#import xbmcplugin  # pylint: disable=F0401
from xbmcgui import ListItem
import plexbmc.interfaces
from plexbmc.interfaces import IInfo

#from zope.interface import Interface, implements
#import zope.interface;print(zope.interface.__file__)

# Zope note.  Needed to remove replace the __init__.py file in zope directory since namespace was causing errors
# I think its a bug with this version (twisted) from what I read
import zope.interface
from zope.interface import Interface





class Info(ListItem):
    zope.interface.implements(IInfo)
    def __init__(self, label='', label2='', iconImage=None, thumbnailImage=None, path=None):
        super(ListItem, self).__init__()

class Test(object):
    items = []
    def __init__(self):
        pass

    def start(self):
        '''
        '''
        info = Info(
            label='Label',
            label2='Label2',
            iconImage=None,
            thumbnailImage=None,
            path=None,
        )
        info.setProperty('uuid', '12345')
        info.setProperty('node.target', 'Videos')
        self.items.append(('', info, True))
        print 'hello'
