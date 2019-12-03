#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Youtube video downloader
'''

# Libs
import sys
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
        servant_downloader = DownloaderI()

        adapter = broker.createObjectAdapter('DownloaderAdapter')
        downloader_proxy = adapter.add(
            servant_downloader, broker.stringToIdentity('downloader1'))

        # Show proxy
        print(downloader_proxy, flush=True)

        ########## PUBLISHER ##########
        topic_mgr = self.get_topic_manager()

        if not topic_mgr:
            raise RuntimeError('[ÐOWNLOADER] Error getting topic manager')

        topic_name = 'UpdateEvents'
        try:
            topic = topic_mgr.retrieve(topic_name)
        except IceStorm.NoSuchTopic:
            print('[DOWNLOADER] No such topic found, creating...')
            topic = topic_mgr.create(topic_name)

        publisher = topic.getPublisher()
        servant_downloader.publisher = publisher

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


class DownloaderI(TrawlNet.Downloader):
    '''
    Downloader servant
    '''

    publisher = None

    def __init__(self):
        '''
        Class constructor
        '''
        self.n = 0

    def addDownloadTask(self, url, current=None):
        '''
        Adds a download task from an url
        '''

        print('[DOWNLOADER] processing download task {0}: {1}'.format(
            self.n, url))
        self.n += 1

        file_data = download_mp3(url)

        if not publisher:
            raise RuntimeError('[ÐOWNLOADER] Error getting publisher')

        updater = TrawlNet.UpdateEventPrx.checkedCast(publisher)
        updater.newFile(file_data)

        return file_data


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


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('[DOWNLOADER] usage: downloader.py --Ice.Config=Downloader.config')
        exit()

    downloader = Downloader()
    sys.exit(downloader.main(sys.argv))
