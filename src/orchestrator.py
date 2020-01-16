#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Orchestrator class
'''

from exceptions import DownloadError

import sys
import hashlib
import Ice
import youtube_dl
import IceStorm

Ice.loadSlice('trawlnet.ice')
import TrawlNet

__author__ = 'Antonio Manjavacas'
__license__ = 'GPL'


class OrchestratorServer(Ice.Application):
    '''
    Orchestrator server
    '''

    def __init__(self):
        '''
        Class constructor
        '''
        self.files = {}
        self.orchestrators = []


    def get_topic_manager(self):
        '''
        Obtains the topic manager
        '''

        key = 'YoutubeDownloaderApp.IceStorm/TopicManager'
        proxy = self.communicator().stringToProxy(key)

        if proxy is None:
            print('[ORCHESTRATOR] Error: topic key not set')
            return None

        return IceStorm.TopicManagerPrx.checkedCast(proxy)


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
        print('[ORCHESTRATOR] ' + str(subscriber) + ' is now subscribed to ' + topic_name)


    def run(self, argv):
        '''
        Run method
        '''

        broker = self.communicator()
        properties = broker.getProperties()

        ######## ORCHESTRATOR SERVANT ########
        servant_orchestrator = OrchestratorI()
        adapter = broker.createObjectAdapter('OrchestratorAdapter')
        orchestrator_id = properties.getProperty('Identity')
        orchestrator_proxy = adapter.add(servant_orchestrator,
                                         broker.stringToIdentity(orchestrator_id))

        servant_orchestrator.orchestrator = self

        # Show proxy
        print(orchestrator_proxy, flush=True)

        # Get factories
        downloader_factory_proxy = broker.stringToProxy(argv[1])
        downloader_factory = TrawlNet.DownloaderFactoryPrx.checkedCast(downloader_factory_proxy)
        servant_orchestrator.downloader_factory = downloader_factory

        transfer_factory_proxy = broker.stringToProxy(argv[2])
        transfer_factory = TrawlNet.TransferFactoryPrx.checkedCast(transfer_factory_proxy)
        servant_orchestrator.transfer_factory = transfer_factory

        ######## UPDATER SERVANT ########
        servant_updater = UpdateEventI()
        updater_id = properties.getProperty('UpdaterIdentity')
        updater_proxy = adapter.add(servant_updater, broker.stringToIdentity(updater_id))

        # Get direct proxy for topic subscription
        id_ = updater_proxy.ice_getIdentity()
        updater_direct_proxy = adapter.createDirectProxy(id_)
        self.subscribe_to('UpdateEvents', updater_direct_proxy)
        servant_updater.orchestrator = self

        ######## GREETER SERVANT ########
        servant_greeter = OrchestratorEventI()
        greeter_id = properties.getProperty('GreeterIdentity')
        greeter_proxy = adapter.add(servant_greeter, broker.stringToIdentity(greeter_id))

        # Get direct proxy for topic subscription
        id_ = greeter_proxy.ice_getIdentity()
        greeter_direct_proxy = adapter.createDirectProxy(id_)
        self.subscribe_to('OrchestratorSync', greeter_direct_proxy)

        # Publish in OrchestratorSync topic
        servant_greeter.orchestrator = TrawlNet.OrchestratorPrx.uncheckedCast(
            orchestrator_proxy)

        topic = self.get_topic('OrchestratorSync')
        publisher = topic.getPublisher()
        greeter = TrawlNet.OrchestratorEventPrx.uncheckedCast(publisher)

        adapter.activate()

        # Make public
        greeter.hello(
            TrawlNet.OrchestratorPrx.uncheckedCast(orchestrator_proxy))

        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        # Unsubscribe
        self.get_topic('UpdateEvents').unsubscribe(updater_direct_proxy)
        self.get_topic('OrchestratorSync').unsubscribe(greeter_direct_proxy)

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
        self.downloader_factory = None
        self.transfer_factory = None

    def announce(self, other, current=None):
        '''
        Announces to another orchestrator
        '''

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

        video_hash = hashlib.sha256(get_title(url).encode()).hexdigest()

        if video_hash in self.orchestrator.files:
            print('[ORCHESTRATOR] The file has been previously downloaded')
            file_info = TrawlNet.FileInfo()
            file_info.name = self.orchestrator.files[video_hash]
            file_info.hash = video_hash
            return file_info
        else:
            downloader = self.downloader_factory.create()
            if not downloader:
                raise DownloadError(
                    '[ORCHESTRATOR] Error: error creating downloader')
            file_info = downloader.addDownloadTask(url)
            downloader.destroy()

            # Inform to the rest of orchestrators
            for other in self.orchestrator.orchestrators:
                other_list = other.getFileList()
                if file_info not in other_list:
                    other_list.append(file_info)

            return file_info

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

    def getFile(self, file_name, current=None):
        '''
        Returns a transfer for a specific file
        '''
        return self.transfer_factory.create(file_name)


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


def get_title(url):
    '''
    Gets a video title from its url
    '''

    with youtube_dl.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(url, download=False)

    return info_dict['title']


if __name__ == '__main__':
    sys.exit(OrchestratorServer().main(sys.argv))
