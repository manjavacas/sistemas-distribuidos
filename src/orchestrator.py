#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Orchestrator for the management of download requests
'''

# Libs
import sys
import Ice
import IceStorm

Ice.loadSlice('trawlnet.ice')
import TrawlNet

__author__ = 'Antonio Manjavacas'
__license__ = 'GPL'


class Orchestrator(Ice.Application):
    '''
    Download request receiver
    '''

    def __init__(self):
        '''
        Class constructor
        '''
        self.files = {}

    def run(self, argv):
        '''
        Run method
        '''

        broker = self.communicator()

        servant_orchestrator = OrchestratorI()
        adapter = broker.createObjectAdapter("OrchestratorAdapter")
        orchestrator_proxy = adapter.addWithUUID(servant_orchestrator)

        # Updater
        servant_updater = UpdateEventI()
        servant_updater.orchestrator = self
        broker.createObjectAdapter('UpdaterAdapter')
        adapter.addWithUUID(servant_updater)

        # Show proxy
        print(orchestrator_proxy, flush=True)

        downloader_proxy = broker.stringToProxy(argv[1])
        downloader = TrawlNet.DownloaderPrx.checkedCast(downloader_proxy)

        if not downloader:
            raise RuntimeError(
                '[ORCHESTRATOR] Error: invalid downloader proxy')

        servant_orchestrator.downloader = downloader

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


class OrchestratorI(TrawlNet.Orchestrator):
    '''
    Orchestrator servant
    '''

    def __init__(self):
        '''
        Class constructor
        '''
        self.downloader = None

    def downloadTask(self, url, current=None):
        '''
        Sends a download task to a downloader
        '''

        print('[ORCHESTRATOR] receives download task {0}:'.format(url))

        print('[ORCHESTRATOR] sending task to downloader...')

        file_data = self.downloader.addDownloadTask(url)

        return file_data


class UpdateEventI(TrawlNet.UpdateEvent):
    '''
    Class for publishing in UpdateEvents topic
    '''

    def __init__(self):
        '''
        Class constructor
        '''

        self.orchestrator = None

    def newFile(self, file_info, current=None):
        '''
        Notify new file
        '''

        if not self.orchestrator:
            raise RuntimeError('[ÐOWNLOADER] Error getting orchestrator')

        if file_info.hash not in self.orchestrator.files:
            print('[DOWNLOADER] New file named {0}, with hash = {1}'.format(
                file_info.name, file_info.hash))
            self.orchestrator.files[fileHash] = file_info.name


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('[ORCHESTRATOR] usage: orchestrator.py <downloader_proxy> --Ice.Config=Orchestrator.config')
        exit()

    orchestrator = Orchestrator()
    sys.exit(orchestrator.main(sys.argv))
