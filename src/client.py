#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Client for sending requests to download videos
'''

# Libs
import sys
import Ice
import IceStorm
from urllib.parse import urlparse

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

        # Check options
        if len(argv) == 3:
            url = argv[2]
            parsed_url = urlparse(url)
            if parsed_url.scheme:
                print('[CLIENT] sending URL {0} to {1}...'.format(
                    url, argv[1]))
                orchestrator.downloadTask(url)
            else:
                raise RuntimeError('[CLIENT] the entered URL is not valid')
        elif len(argv) == 2:
            print('[CLIENT] requesting list of available files...')
            print(orchestrator.getFileList())

        return 0


if __name__ == '__main__':

    client = Client()
    sys.exit(client.main(sys.argv))
