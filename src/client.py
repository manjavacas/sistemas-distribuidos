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


class Client(Ice.Application):
    '''
    Client class which calls the orchestrator
    '''

    def run(self, argv):
        '''
        Run method
        '''
        proxy = self.communicator().stringToProxy(argv[1])
        orchestrator = TrawlNet.OrchestratorPrx.checkedCast(proxy)

        if not orchestrator:
            raise RuntimeError('[CLIENT] error: invalid orchestrator proxy')

        print('[CLIENT] sending URL {0} to {1}...'.format(argv[2], argv[1]))
        orchestrator.downloadTask(argv[2])

        return 0


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print(
            '[CLIENT] usage: client.py <orchestrator_proxy> <file_url> --Ice.Config=Client.config')
        exit()

    CLIENT = Client()
    sys.exit(CLIENT.main(sys.argv))
