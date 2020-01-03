#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import binascii
import sys
import os

import IceGrid
import Ice

Ice.loadSlice('trawlnet.ice')
import TrawlNet

APP_DIRECTORY = './'
DOWNLOADS_DIRECTORY = os.path.join(APP_DIRECTORY, 'downloads')


class TransferServer(Ice.Application):
    '''
    Transfer server
    '''

    def run(self, args):
        '''
        Run method
        '''

        broker = self.communicator()
        properties = broker.getProperties()
        
        servant = TransferFactoryI()
        adapter = broker.createObjectAdapter('TransferAdapter')
        factory_id = properties.getProperty('TransferFactoryIdentity')
        proxy = adapter.add(servant, broker.stringToIdentity(factory_id))

        # Show proxy
        print('{}'.format(proxy), flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


class TransferFactoryI(TrawlNet.TransferFactory):
    def create(self, file_name, current):
        '''
        Creates transfers
        '''

        file_path = os.path.join(DOWNLOADS_DIRECTORY, file_name)
        servant = TransferI(file_path)
        proxy = current.adapter.addWithUUID(servant)
        print('[TRANSFER-FACTORY] New transfer for {}'.format(file_path), flush=True)

        return TrawlNet.TransferPrx.checkedCast(proxy)


class TransferI(TrawlNet.Transfer):
    '''
    Transfer class
    '''

    def __init__(self, file_path):
        '''
        Class constructor
        '''
        self.file_ = open(file_path, 'rb')

    def recv(self, size, current):
        '''
        Transfer receiving
        '''
        return str(binascii.b2a_base64(self.file_.read(size), newline=False))

    def close(self, current):
        '''
        Closes the file
        '''
        self.file_.close()

    def destroy(self, current):
        '''
        Destroy transfer
        '''
        try:
            current.adapter.remove(current.id)
            print('[TRANSFER] Transfer destroyed', flush=True)
        except Exception as e:
            print(e, flush=True)


if __name__ == '__main__':
    sys.exit(TransferServer().main(sys.argv))
