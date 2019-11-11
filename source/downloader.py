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

'''
    Downloader task receiver
'''
class DownloaderServer(Ice.Application):
    def run(self, argv):

        broker = self.communicator()
        servant = DownloaderI()

        adapter = broker.createObjectAdapter("DownloaderAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("downloader1"))

        print('[DOWNLOADER] showing proxy...\n{0}'.format(proxy))

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


'''
    Downloader servant
'''
class DownloaderI(TrawlNet.Downloader):

    n = 0

    def addDownloadTask(self, url, current=None):

        print('[DOWNLOADER] receives download task {0}: {1}'.format(self.n, url))
        sys.stdout.flush()
        self.n += 1

        return 0


SERVER = DownloaderServer()
sys.exit(SERVER.main(sys.argv))
