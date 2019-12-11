#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' 
Client class 
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
    Client class 
    '''

    def run(self, argv):
        ''' 
        Run method 
        '''
        
        proxy = self.communicator().stringToProxy(argv[1])
        orchestrator = TrawlNet.OrchestratorPrx.checkedCast(proxy)

        if not orchestrator:
            raise RuntimeError('[CLIENT] Error: invalid orchestrator proxy')

        # Download audio
        if len(argv) == 3:
            url = argv[2]
            parsed_url = urlparse(url)
            if parsed_url.scheme:
                print('[CLIENT] Sending URL {0} to {1}...'.format(
                    url, argv[1]))
                file_info = orchestrator.downloadTask(url)
                print('[CLIENT] Received confirmation to ' + file_info.name)
            else:
                raise RuntimeError('[CLIENT] Error: the entered URL is not valid')
        # Get file list
        elif len(argv) == 2:
            print('[CLIENT] Requesting list of available files...')
            print(str(orchestrator.getFileList()))

        return 0


if __name__ == '__main__':
    app = Client()
    sys.exit(app.main(sys.argv))
