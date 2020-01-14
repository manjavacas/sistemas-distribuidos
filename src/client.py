#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Client class
'''

from urllib.parse import urlparse
from optparse import OptionParser

import os
import sys
import binascii

import Ice

Ice.loadSlice('trawlnet.ice')
import TrawlNet

__author__ = 'Antonio Manjavacas'
__license__ = 'GPL'

DOWNLOADS_DIRECTORY = '/tmp/trawlnet_cache/downloads'


class Client(Ice.Application):
    '''
    Client class
	./client.py orchestrator --download <url> <Ice.Config>
	./client.py orchestrator --transfer <filename> <Ice.Config>
	./client.py orchestrator <Ice.Config>
    '''

    def transfer_request(self, file_name):
        '''
        Requests a file
        '''
        remote_EOF = False
        BLOCK_SIZE = 1024
        transfer = None

        try:
            transfer = self.orchestrator.getFile(file_name)
        except TrawlNet.TransferError as e:
            print(e.reason)
            return 1

        with open(os.path.join(DOWNLOADS_DIRECTORY, file_name), 'wb') as file_:
            remote_EOF = False
            while not remote_EOF:
                data = transfer.recv(BLOCK_SIZE)
                if len(data) > 1:
                    data = data[1:]
                data = binascii.a2b_base64(data)
                remote_EOF = len(data) < BLOCK_SIZE
                if data:
                    file_.write(data)
            transfer.close()

        transfer.destroy()
        print('[CLIENT] Transfer finished!')

    def run(self, argv):
        '''
        Run method
        '''

        # Check options and arguments
        parser = OptionParser()
        parser.add_option('--download', metavar='URL',
                          help='Download a file from URL')
        parser.add_option('--transfer', metavar='ID',
                          help='Transfer a file using its ID')

        (options, args) = parser.parse_args()

        # Get proxy
        proxy = self.communicator().stringToProxy(argv[1])
        self.orchestrator = TrawlNet.OrchestratorPrx.checkedCast(proxy)

        if not self.orchestrator:
            raise RuntimeError('[CLIENT] Error: invalid orchestrator proxy')

        # Download file: client.py <proxy> --download <url> <config>
        if options.download != None:
            url = argv[3]
            parsed_url = urlparse(url)
            if parsed_url.scheme:
                print('[CLIENT] Sending URL {0} to {1}...'.format(
                    url, argv[1]))
                file_info = self.orchestrator.downloadTask(url)
                print('[CLIENT] Received confirmation to ' + file_info.name)
            else:
                raise RuntimeError(
                    '[CLIENT] Error: the entered URL is not valid: ' + url)
        # Transfer file: client.py <proxy> --transfer <filename> <config>
        elif options.transfer != None:
            self.transfer_request(argv[3])
        # Get file list: client.py <proxy> <config>
        else:
            print('[CLIENT] Requesting list of available files...')
            print(str(self.orchestrator.getFileList()))

        return 0


if __name__ == '__main__':
    sys.exit(Client().main(sys.argv))
