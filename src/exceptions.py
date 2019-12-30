#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Exceptions class
'''

import Ice

Ice.loadSlice('trawlnet.ice')
import TrawlNet


class GeneralError(TrawlNet.GeneralError):
    '''
    General error exception
    '''

    def __init__(self, reason=''):
        '''
        Class constructor
        '''
        self.reason = reason


class TransferError(TrawlNet.TransferError, GeneralError):
    '''
    Transfer error exception
    '''

    def __init__(self, reason):
        '''
        Class constructor
        '''
        GeneralError.__init__(self, reason)


class DownloadError(TrawlNet.DownloadError, GeneralError):
    '''
    Download error exception
    '''

    def __init__(self, reason):
        '''
        Class constructor
        '''
        GeneralError.__init__(self, reason)
