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

'''
NOTES:

Goal:  process...

- Incoming request for media section
- handler will pick it up an adapt to proper class
- that class will know how to retreive its section from plex
- once section is retreived, it will be adapted again all info labels that are provide by section
- each label will know who to format itself based on the section it is in and will create



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
