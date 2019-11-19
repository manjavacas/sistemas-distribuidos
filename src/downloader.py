#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Youtube video downloader
'''

# Libs
import sys
import Ice

Ice.loadSlice('trawlnet.ice')
import TrawlNet


__author__ = 'Antonio Manjavacas'
__license__ = 'GPL'


class DownloaderServer(Ice.Application):
    '''
    Downloader task receiver
    '''

    def run(self, argv):
        '''
        Run method
        '''

        broker = self.communicator()
        servant = DownloaderI()

        adapter = broker.createObjectAdapter("DownloaderAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("downloader1"))

        # Save proxy
        proxy_file = open('downloader.proxy','w')
        print(proxy, file = proxy_file)
        proxy_file.close()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


class DownloaderI(TrawlNet.Downloader):
    '''
    Downloader servant
    '''

    def __init__(self):
        '''
        Class constructor
        '''
        self.n = 0

    def addDownloadTask(self, url, current=None):
        '''
        Adds a download task from an url
        '''

        print('[DOWNLOADER] adds download task {0}: {1}'.format(self.n, url))
        self.n += 1

        return 'ok'


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('[DOWNLOADER] usage: downloader.py --Ice.Config=Downloader.config')
        exit()

    SERVER = DownloaderServer()
    sys.exit(SERVER.main(sys.argv))
