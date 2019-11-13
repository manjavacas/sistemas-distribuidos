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

        broker = self.communicator()
        servant = DownloaderI()

        adapter = broker.createObjectAdapter("DownloaderAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("downloader1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


class DownloaderI(TrawlNet.Downloader):
    '''
    Downloader servant
    '''

    n = 0

    def addDownloadTask(self, url, current=None):

        print('[DOWNLOADER] adds download task {0}: {1}'.format(self.n, url))
        sys.stdout.flush()
        self.n += 1

        return 0

if len(sys.argv) != 2:
    print('[DOWNLOADER] usage: downloader.py --Ice.Config=Downloader.config')
    exit()

SERVER = DownloaderServer()
sys.exit(SERVER.main(sys.argv))
