#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Youtube video downloader
'''

from exceptions import DownloadError

import sys
import hashlib
import os

import Ice
import youtube_dl
import IceStorm

Ice.loadSlice('trawlnet.ice')
import TrawlNet

__author__ = 'Antonio Manjavacas'
__license__ = 'GPL'


class DownloaderServer(Ice.Application):
    '''
    Downloader task receiver
    '''

    def get_topic_manager(self):
        '''
        Obtains topic manager
        '''

        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)

        if proxy is None:
            print('[ÐOWNLOADER] Error: topic key not set')
            return None

        print('Using IceStorm in: ' + key)
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def get_topic(self, topic_name):
        '''
        Creates a new topic or returns an existing one
        '''

        topic_mgr = self.get_topic_manager()

        if not topic_mgr:
            raise RuntimeError('[ÐOWNLOADER] Error getting topic manager')

        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            print('[DOWNLOADER] No such topic found, creating...')
            topic = topic_mgr.create(topic_name)

        return topic

    def run(self, argv):
        '''
        Run method
        '''

        broker = self.communicator()

        servant_downloader = DownloaderI()
        adapter = broker.createObjectAdapter('DownloaderAdapter')
        downloader_proxy = adapter.addWithUUID(servant_downloader)

        # Show proxy to orchestrator
        print(downloader_proxy, flush=True)

        topic = self.get_topic('UpdateEvents')
        publisher = topic.getPublisher()
        updater = TrawlNet.UpdateEventPrx.uncheckedCast(publisher)

        servant_downloader.updater = updater

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


class DownloaderI(TrawlNet.Downloader):
    '''
    Downloader servant
    '''

    def __init__(self):
        '''
        Class constructor
        '''
        self.updater = None

    def addDownloadTask(self, url, current=None):
        '''
        Processes a download task from an url
        '''

        print('[DOWNLOADER] Received download task: ' + url)

        try:
            audio = download_mp3(url)
        except:
            raise DownloadError('[DOWNLOADER] Error in audio download')

        print('[DOWNLOADER] The file ' + os.path.basename(audio) + ' has been downloaded')

        file_info = TrawlNet.FileInfo()
        file_info.name = generate_id(url)
        file_info.hash = hashlib.sha256(file_info.name.encode()).hexdigest()

        if not self.updater:
            raise DownloadError('[ÐOWNLOADER] Error getting publisher')

        self.updater.newFile(file_info)

        return file_info


class NullLogger:
    '''
    NullLogger used by YouTube video downloader
    '''

    def debug(self, msg):
        '''
        Debug
        '''
        pass

    def warning(self, msg):
        '''
        Warning
        '''
        pass

    def error(self, msg):
        '''
        Error
        '''
        pass


_YOUTUBEDL_OPTS_ = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': NullLogger()
}


def download_mp3(url, destination='./'):
    '''
    Synchronous download from YouTube
    '''

    options = {}
    task_status = {}

    def progress_hook(status):
        '''
        Progress hook
        '''
        task_status.update(status)

    options.update(_YOUTUBEDL_OPTS_)
    options['progress_hooks'] = [progress_hook]
    options['outtmpl'] = os.path.join(destination, '%(title)s.%(ext)s')
    with youtube_dl.YoutubeDL(options) as youtube:
        youtube.download([url])
    filename = task_status['filename']
    # BUG: filename extension is wrong, it must be mp3
    filename = filename[:filename.rindex('.') + 1]
    return filename + options['postprocessors'][0]['preferredcodec']

def generate_id(url):
    '''
    Gets a video id from its url
    '''

    with youtube_dl.YoutubeDL(_YOUTUBEDL_OPTS_) as ydl:
        info_dict = ydl.extract_info(url, download=False)

    return info_dict['id']

if __name__ == '__main__':
    sys.exit(DownloaderServer().main(sys.argv))
