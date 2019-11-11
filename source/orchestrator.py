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

'''
    Download request receiver
'''
class OrchestratorServer(Ice.Application):
    def run(self, argv):

        broker = self.communicator()
        servant = OrchestratorI()

        adapter = broker.createObjectAdapter("OrchestratorAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("orchestrator1"))

        print('[ORCHESTRATOR] showing proxy...\n{0}'.format(proxy))

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


'''
    Orchestrator servant
'''
class OrchestratorI(TrawlNet.Orchestrator):

    n = 0

    def downloadTask(self, url, current=None):
        
        print('[ORCHESTRATOR] receives download task {0}: {1}'.format(self.n, url))
        sys.stdout.flush()
        self.n += 1

        proxy = self.communicator().stringToProxy("PROXY_DOWNLOADER") # CHECK -> proxy & communicator
        downloader = TrawlNet.DownloaderPrx.checkedCast(proxy)

        if not downloader:
            raise RuntimeError('[ORCHESTRATOR] error: invalid proxy')

        print('[ORCHESTRATOR] sending task to downloader...')
        downloader.addDownloadTask(url)
        return 0

SERVER = OrchestratorServer()
sys.exit(SERVER.main(sys.argv))
