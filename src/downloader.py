#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Youtube video downloader
'''

# Libs
import sys
import hashlib
import Ice
import IceStorm
import os
import youtube_dl

Ice.loadSlice('trawlnet.ice')
import TrawlNet

__author__ = 'Antonio Manjavacas'
__license__ = 'GPL'


class Downloader(Ice.Application):
    '''
    Downloader task receiver
    '''

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)

        if proxy is None:
            print('[ÐOWNLOADER] Error: topic key not set.')
            return None

        print('Using IceStorm in: {0} '.format(key))
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        '''
        Run method
        '''

        broker = self.communicator()

        # Downloader
        servant_downloader = DownloaderI()
        adapter = broker.createObjectAdapter('DownloaderAdapter')
        downloader_proxy = adapter.addWithUUID(servant_downloader)

        # Updater
        servant_updater = UpdateEventI()
        broker.createObjectAdapter('UpdaterAdapter')
        updater_proxy = adapter.addWithUUID(servant_updater)

        # Show proxy
        print(downloader_proxy, flush=True)

        # UpdateEvents topic
        topic_mgr = self.get_topic_manager()

        if not topic_mgr:
            raise RuntimeError('[ÐOWNLOADER] Error getting topic manager')

        topic_name = 'UpdateEvents'
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            print('[DOWNLOADER] No such topic found, creating...')
            topic = topic_mgr.create(topic_name)

        # Set publisher
        servant_updater.publisher = topic.getPublisher()

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


class DownloaderI(TrawlNet.Downloader):
    '''
    Downloader servant
    '''

    def addDownloadTask(self, url, current=None):
        '''
        Adds a download task from an url
        '''

        print('[DOWNLOADER] processing download task: {0}'.format(url))

        try:
            audio=download_mp3(url)
        except:
            raise RuntimeError('[DOWNLOADER] Error in audio download')

        file_info=TrawlNet.FileInfo()
        file_info.name=os.path.basename(audio)
        file_info.hash=hashlib.sha256(file_info.name.encode()).hexdigest()

        return file_info

class UpdateEventI(TrawlNet.UpdateEvent):
    '''
    Class for publishing in UpdateEvents topic
    '''

    def __init__(self):
        '''
        Class constructor
        '''
        self.publisher=None

    def newFile(self, file_info):
        '''
        Notify new file in channel
        '''
        if not self.publisher:
            raise RuntimeError('[ÐOWNLOADER] Error getting publisher')
        
        print('¡NEW FILE!')

class NullLogger:
    '''
    NullLogger used by YouTube video downloader
    '''

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


_YOUTUBEDL_OPTS_={
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': NullLogger()
}


def download_mp3(url, destination='./downloads'):
    '''
    Synchronous download from YouTube
    '''
    options={}
    task_status={}

    def progress_hook(status):
        task_status.update(status)
    options.update(_YOUTUBEDL_OPTS_)
    options['progress_hooks']=[progress_hook]
    options['outtmpl']=os.path.join(destination, '%(title)s.%(ext)s')
    with youtube_dl.YoutubeDL(options) as youtube:
        youtube.download([url])
    filename=task_status['filename']
    # BUG: filename extension is wrong, it must be mp3
    filename=filename[:filename.rindex('.') + 1]
    return filename + options['postprocessors'][0]['preferredcodec']


if __name__ == '__main__':

    downloader=Downloader()
    sys.exit(downloader.main(sys.argv))
