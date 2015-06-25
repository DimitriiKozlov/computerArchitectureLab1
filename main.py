__author__ = 'Dimitrii Kozlov'

import xml.etree.cElementTree as eT
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

    # Set duplication percentage
    def find_duplications(self, _channels):
        max_duplication = 0
        for news in _channels:
            if news.get_channel() == self.channel:
                continue
            duplication = find_duplication2(get_hash(get_canonising_text(self.text)),
                                            get_hash(get_canonising_text(news.get_text())))
            if max_duplication < duplication:
                max_duplication = duplication
        self.duplication = max_duplication

    # Get channel name
    def get_channel(self):
        return self.channel

    # Get theme name
    def get_theme(self):
        return self.theme

    # Get text of news
    def get_text(self):
        return self.text

    # Get duplication value
    def get_duplication(self):
        return self.duplication


# Get urls from xml-file
def get_data_from_xml():
    f = open('data.xml', 'r')
    tree = eT.parse(f.name)
    root = tree.getroot()

    urls = []
    for url in root.findall('url'):
        urls.append(url.text)
    return urls


# Get list of news from urls
def get_channels(urls):
    _channels = []
    for url in urls:
        feed = feedparser.parse(url)
        for item in feed['items']:
            summary = item['summary']
            if '<' in summary:
                summary = summary[:summary.index('<')]
            if len(summary) < 5:
                continue
            _channels.append(News(feed['feed']['title'], item['title'], summary))
    return _channels


# Write list of news in xml-file
def print_channels(name, _channels):
    root = eT.Element('data')
    for news in _channels:
        chan = eT.SubElement(root, 'news')
        eT.SubElement(chan, 'channel').text = unicode(news.get_channel())
        eT.SubElement(chan, 'theme').text = unicode(news.get_theme())
        eT.SubElement(chan, 'text').text = unicode(news.get_text())
        eT.SubElement(chan, 'duplication').text = str(news.get_duplication())
    tree = eT.ElementTree(root)
    tree.write(name)


# From list of words set shingle and get hash from it
def get_hash(text):
    shingle_len = 3
    _hash = []
    for i in range(len(text) - (shingle_len - 1)):
        _hash.append(binascii.crc32(' '.join([x for x in text[i:i + shingle_len]]).encode('utf-8')))
    return _hash


# Find duplication percentage from two list of hash
def find_duplication2(hash1, hash2):
    duplication = 0
    if len(hash1) == 0 or len(hash2) == 0:
        return 0
    for i in range(len(hash1)):
        if hash1[i] in hash2:
            duplication += 1
    return duplication * 2 / float(len(hash1) + len(hash2)) * 100


# Get list of function for gevent
def get_threads(_channels):
    threads = []
    _channels = [News('C', 'T', 'T')]
    for news in _channels:
        threads.append(gevent.spawn(news.find_duplications, _channels))
    return threads


# Canonising text to list of words
def get_canonising_text(text):
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


# Find duplication synchronise
def work_sync(_channels):
    for news in _channels:
        news.find_duplications(_channels)


# Set work depend of mode
def work(_channels):
    f = open('main.config', 'r')
    s = f.read()
    if s[14:] == 'async':
        print 'Async:\n\t'
        gevent.joinall(get_threads(_channels))
    else:
        print 'Sync:\n\t'
        work_sync(_channels)


# Set list of news
channels = get_channels(get_data_from_xml())

print("Complete downloading rss file's")

# Start timing of work
t = time.time()

work(channels)

# Finish timing of work and print it
print 'work time:', time.time() - t, ' ms'

# Write result
print_channels('channels.xml', channels)
