#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
    Client for sending requests to download videos
'''

# Libs
import sys
import Ice

Ice.loadSlice('trawlnet.ice')
import TrawlNet

__author__ = 'Antonio Manjavacas'
__license__ = 'GPL'

'''
    Client class which calls the orchestrator
'''
class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        orchestrator = TrawlNet.OrchestratorPrx.checkedCast(proxy)

        if not orchestrator:
            raise RuntimeError('[CLIENT] error: invalid proxy')

        print('[CLIENT] sending URL to {0}...'.format(argv[2]))
        orchestrator.downloadTask(argv[2])

        return 0


if len(sys.argv) != 3:
    print('[CLIENT] usage: client.py <proxy> <file-url>')
    exit()

CLIENT = Client()
sys.exit(CLIENT.main(sys.argv))
