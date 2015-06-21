__author__ = 'Dimitrii Kozlov'

import xml.etree.cElementTree as ET
# from xml.dom import minidom
# import re
# import sys
# import requests
import feedparser
import binascii
import gevent
from gevent import Greenlet
import time


split_symbols = ['.', ',', '!', '?', ':', ';', '-', '\n', '\t', '(', ')', "'"]
split_words = ['about', 'above', 'according to', 'across', 'after', 'against', 'along', 'along with', 'among',
               'apart from', 'around', 'as', 'as for', 'at',
               'because of', 'before', 'behind', 'below', 'beneath', 'beside', 'between', 'beyond', 'but*', 'by',
               'by means of', 'concerning', 'despite', 'down', 'during', 'except', 'except for', 'excepting', 'for',
               'from', 'in', 'in addition to', 'in back of', 'in case of', 'in front of', 'in place of', 'inside',
               'in spite of', 'instead of', 'into', 'like', 'near', 'next', 'of', 'off', 'on', 'onto', 'on top of',
               'out', 'out of', 'outside', 'over', 'past', 'regarding', 'round', 'since', 'through', 'throughout',
               'till', 'to', 'toward', 'under', 'underneath', 'unlike', 'until', 'up', 'upon', 'up to', 'with',
               'within', 'without']


class News(Greenlet):

    def __init__(self, channel, theme, text):
        Greenlet.__init__(self)
        self.channel = channel
        self.theme = theme
        self.text = text
        self.duplication = 0

    def _run(self, channels):
        max_duplication = 0
        for news in channels:
            if news.get_channel() == self.channel:
                continue
            duplication = find_duplication2(get_hash(get_list_of_shingles(self.text)),
                                            get_hash(get_list_of_shingles(news.get_text())))
            if max_duplication < duplication:
                max_duplication = duplication
        self.duplication = max_duplication

    def get_channel(self):
        return self.channel

    def get_theme(self):
        return self.theme

    def get_text(self):
        return self.text

    def get_duplication(self):
        return self.duplication

    # def _run(self):
    #     print(self.message)
    #     gevent.sleep(self.n)


def get_data_from_xml():
    f = open('data.xml', 'r')
    tree = ET.parse(f.name)
    root = tree.getroot()

    urls = []
    for url in root.findall('url'):
        urls.append(url.text)
    return urls


def get_channels(urls):
    channels = []
    for url in urls:
        feed = feedparser.parse(url)
        for item in feed['items']:
            summary = item['summary']
            if '<' in summary:
                summary = summary[:summary.index('<')]
            if len(summary) < 5:
                continue
            channels.append(News(feed['channel'], item['title'], summary))
    return channels


def print_channels(channels):
    root = ET.Element('data')
    for news in channels:
        chan = ET.SubElement(root, 'channel')
        ET.SubElement(chan, 'name').text = unicode(news.get_channel())
        news_et = ET.SubElement(chan, 'news')
        ET.SubElement(news_et, 'theme').text = unicode(news.get_theme())
        ET.SubElement(news_et, 'text').text = unicode(news.get_text())
        # print(news.get_text())
        ET.SubElement(news_et, 'duplication').text = str(news.get_duplication())
    tree = ET.ElementTree(root)
    tree.write('channels.xml')


def get_hash(text):
    shingle_len = 3
    hash = []
    for i in range(len(text) - (shingle_len - 1)):
        hash.append(binascii.crc32(' '.join([x for x in text[i:i + shingle_len]]).encode('utf-8')))
    return hash


def find_duplication2(hash1, hash2):
    duplication = 0
    if len(hash1) == 0 or len(hash2) == 0:
        return 0
    for i in range(len(hash1)):
        if hash1[i] in hash2:
            duplication += 1
    return duplication * 2 / float(len(hash1) + len(hash2)) * 100


def get_threads(channels):
    threads = []
    for news in channels:
        threads.append(gevent.spawn(news._run, channels))
    return threads


def get_list_of_shingles(text):
    text = text.lower()
    for i in range(len(split_symbols)):
        while split_symbols[i] in text:
            j = text.index(split_symbols[i])
            text = text[:j] + ' ' + text[j + len(split_symbols[i]):]
    new_text = []
    arr_text = text.split()
    for i in range(len(arr_text)):
        if not (arr_text[i] in split_words):
            new_text.append(arr_text[i])
    return new_text


# print_channels(get_channels(get_data_from_xml()))

# threads = [thread1, thread2, thread3]

# gevent.joinall(threads)

channels = get_channels(get_data_from_xml())

t = time.time()

gevent.joinall(get_threads(channels))

print time.time() - t

print_channels(channels)