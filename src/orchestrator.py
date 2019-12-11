#!/usr/bin/python3
# -*- coding: utf-8 -*-

''' 
Orchestrator class
'''

import sys
import Ice
import IceStorm
import json

Ice.loadSlice('trawlnet.ice')
import TrawlNet

__author__ = 'Antonio Manjavacas'
__license__ = 'GPL'


class OrchestratorServer(Ice.Application):
    ''' 
    Orchestrator creator 
    '''
    def __init__(self):
        self.downloader = None
        self.files = {}
        self.orchestrators = []
    
    def get_topic(self, topic_name):
        ''' 
        Creates a new topic or returns an existing one 
        '''

        topic_mgr = self.get_topic_manager()

        if not topic_mgr:
            raise RuntimeError('[ORCHESTRATOR] Error getting topic manager')

        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            print('[ORCHESTRATOR] No such topic found, creating...')
            topic = topic_mgr.create(topic_name)

        return topic

    def get_topic_manager(self):
        ''' 
        Obtains the topic manager 
        '''
        
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)

        if proxy is None:
            print('[ORCHESTRATOR] Error: topic key not set')
            return None

        print('[ORCHESTRATOR] Using IceStorm in: ' + key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def subscribe_to(self, topic_name, subscriber):
        ''' 
        Implements topic subscription 
        '''
        
        topic_mgr = self.get_topic_manager()
        if not topic_mgr:
            raise RuntimeError('[ORCHESTRATOR] Error getting topic manager')

        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(topic_name)

        topic.subscribeAndGetPublisher({}, subscriber)

    def run(self, argv):
        ''' 
        Run method 
        '''
        
        # Create servants
        broker = self.communicator()
        
        servant_orchestrator = OrchestratorI()
        adapter = broker.createObjectAdapter('OrchestratorAdapter')
        orchestrator_proxy = adapter.addWithUUID(servant_orchestrator)

        # Show proxy to downloader
        print(orchestrator_proxy, flush=True)

        servant_greeter = OrchestratorEventI()
        broker.createObjectAdapter('GreeterAdapter')
        greeter_proxy = adapter.addWithUUID(servant_greeter)
        self.subscribe_to('OrchestratorSync', greeter_proxy)

        servant_updater = UpdateEventI()
        broker.createObjectAdapter('UpdaterAdapter')
        updater_proxy = adapter.addWithUUID(servant_updater)
        self.subscribe_to('UpdateEvents', updater_proxy)

        downloader_proxy = broker.stringToProxy(argv[1])
        downloader = TrawlNet.DownloaderPrx.checkedCast(downloader_proxy)

        if not downloader:
            raise RuntimeError(
                '[ORCHESTRATOR] Error: invalid downloader proxy')

        servant_orchestrator.downloader = downloader
        servant_orchestrator.orchestrator = self
        servant_updater.orchestrator = self
        
        servant_greeter.orchestrator = TrawlNet.OrchestratorPrx.checkedCast(orchestrator_proxy)
        
        # Make public
        topic = self.get_topic('OrchestratorSync')
        publisher = topic.getPublisher()

        servant_greeter.hello(TrawlNet.OrchestratorPrx.uncheckedCast(publisher))

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
        self.orchestrator = None
           
    def announce(self, other, current=None):
        ''' 
        Announces to another orchestrator 
        '''
        print("HELLO HELLO!")
        if other not in self.orchestrator.orchestrators:
            print('[ORCHESTRATOR] Hi rookie!')
            self.orchestrator.orchestrators.append(other)

        other_list = other.getFileList()
        for file_hash in self.orchestrator.files:
            if file_hash not in other_list:
                other_list[file_hash] = self.orchestrator.files[file_hash]

    def downloadTask(self, url, current=None):
        ''' 
        Sends a download task to a downloader 
        '''
        return self.downloader.addDownloadTask(url)

    def getFileList(self, current=None):
        ''' 
        Returns the list of available files 
        '''
        
        file_list = []

        for file_hash in self.orchestrator.files:
            file_info = TrawlNet.FileInfo()
            file_info.hash = file_hash
            file_info.name = self.orchestrator.files[file_hash]
            file_list.append(file_info)

        return file_list


class OrchestratorEventI(TrawlNet.OrchestratorEvent):
    ''' 
    Orchestrator event servant 
    '''

    def __init__(self):
        ''' 
        Class constructor 
        '''
        self.orchestrator = None

    def hello(self, me, current=None):
        ''' 
        Sync with the rest of orchestrators 
        '''
        me.announce(self.orchestrator)
            

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
        Updates list with new files 
        '''
        
        if not self.orchestrator:
            raise RuntimeError('[UPDATER] Error getting orchestrator')

        if file_info.hash not in self.orchestrator.files:
            print('[UPDATER] New file named {0}, with hash = {1}'.format(
                file_info.name, file_info.hash))
            self.orchestrator.files[file_info.hash] = file_info.name

if __name__ == '__main__':
    app = OrchestratorServer()
    sys.exit(app.main(sys.argv))