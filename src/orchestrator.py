#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
    Orchestrator for the management of download requests
'''

# Libs
import sys
import Ice

Ice.loadSlice('trawlnet.ice')
import TrawlNet


__author__ = 'Antonio Manjavacas'
__license__ = 'GPL'


class OrchestratorServer(Ice.Application):
    '''
    Download request receiver
    '''

    def run(self, argv):

        broker = self.communicator()
        servant = OrchestratorI()

        adapter = broker.createObjectAdapter("OrchestratorAdapter")
        orchestrator_proxy = adapter.add(
            servant, broker.stringToIdentity("orchestrator1"))

        print(orchestrator_proxy, flush=True)
        
        downloader_proxy = broker.stringToProxy(argv[1])
        downloader = TrawlNet.DownloaderPrx.checkedCast(downloader_proxy)

        if not downloader:
            raise RuntimeError(
                '[ORCHESTRATOR] error: invalid downloader proxy')

        servant.downloader = downloader

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


class OrchestratorI(TrawlNet.Orchestrator):
    '''
    Orchestrator servant
    '''

    def __init__(self):
        self.n = 0
        self.downloader = None

    def downloadTask(self, url, current=None):

        print('[ORCHESTRATOR] receives download task {0}: {1}'.format(
            self.n, url))
        self.n += 1

        print('[ORCHESTRATOR] sending task to downloader...')
        self.downloader.addDownloadTask(url)
        return 0


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('[ORCHESTRATOR] usage: orchestrator.py <downloader-proxy> --Ice.Config=Orchestrator.config')
        exit()

    SERVER = OrchestratorServer()
    sys.exit(SERVER.main(sys.argv))
