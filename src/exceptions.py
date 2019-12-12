#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Exceptions class
'''

import Ice

Ice.loadSlice('trawlnet.ice')
import TrawlNet

class DownloadError(TrawlNet.DownloadError):
    '''
    Download error exception
    '''

    def __init__(self, reason):
        '''
        Class constructor
        '''
        self.reason = reason
