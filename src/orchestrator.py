#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Orchestrator for the management of download requests
'''

# Libs
import sys
import Ice
import IceStorm
import json

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

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)

        if proxy is None:
            print('[ORCHESTRATOR] Error: topic key not set')
            return None

        print('[ORCHESTRATOR] Using IceStorm in: {0}'.format(key))
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        '''
        Run method
        '''

        broker = self.communicator()

        # Tasker
        servant_orchestrator = OrchestratorI()
        adapter = broker.createObjectAdapter("OrchestratorAdapter")
        orchestrator_proxy = adapter.addWithUUID(servant_orchestrator)

        # Show proxy
        print(orchestrator_proxy, flush=True)

        # Set class attributes
        downloader_proxy = broker.stringToProxy(argv[1])
        downloader = TrawlNet.DownloaderPrx.checkedCast(downloader_proxy)

        if not downloader:
            raise RuntimeError(
                '[ORCHESTRATOR] Error: invalid downloader proxy')

        servant_orchestrator.downloader = downloader
        servant_orchestrator.orchestrator = self

        # Updater
        servant_updater = UpdateEventI()
        servant_updater.orchestrator = self
        broker.createObjectAdapter('UpdaterAdapter')
        updater_subscriber = adapter.addWithUUID(servant_updater)

        # Subscribe to file update events topic
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            raise RuntimeError('[ORCHESTRATOR] Error getting topic manager')

        topic_name = 'UpdateEvents'
        qos = {}

        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        topic.subscribeAndGetPublisher(qos, updater_subscriber)

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
        self.orchestrator = None

    def downloadTask(self, url, current=None):
        '''
        Sends a download task to a downloader
        '''

        print('[ORCHESTRATOR] receives download task {0}:'.format(url))
        print('[ORCHESTRATOR] sending task to downloader...')

        file_data = self.downloader.addDownloadTask(url)

        return file_data

    def getFileList(self, current=None):

        file_list = []
        
        for file_hash in self.orchestrator.files:
            file_info = TrawlNet.FileInfo()
            file_info.hash = file_hash
            file_info.name= self.orchestrator.files[file_hash]
            file_list.append(file_info)
        
        return file_list
    

    def announce(self):
        raise NotImplementedError


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
            raise RuntimeError('[UPDATER] Error getting orchestrator')

        if file_info.hash not in self.orchestrator.files:
            print('[UPDATER] New file named {0}, with hash = {1}'.format(
                file_info.name, file_info.hash))
            self.orchestrator.files[file_info.hash] = file_info.name


if __name__ == '__main__':

    orchestrator = Orchestrator()
    sys.exit(orchestrator.main(sys.argv))
