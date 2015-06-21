__author__ = 'Dimitrii'

import unittest
from gevent import Greenlet
from mock import *
from python import common


class Tests(unittest.TestCase):
    def test_get_data_from_xml(self):
        name = 'TestData.xml'
        data = common.get_data_from_xml(name)
        self.assertEqual(data, 'url_test')

    def test_print_channels(self):
        name = 'OutTest.xml'

        class News(Greenlet):
            def __init__(self, _channel, theme, _text):
                Greenlet.__init__(self)
                self.channel = _channel
                self.theme = theme
                self.text = _text
                self.duplication = 0

        channel = [News('C', 'T', 'T')]
        common.print_channels(name, channel)
        f = open(name, 'r')
        text = f.read()
        s = '<data><news><channel>C</channel><theme>T</theme><text>T</text><duplication>0</duplication></news></data>'
        self.assertEqual(text, s)

    @patch('requests.get')
    def test_get_hash(self, request_function):
        mock = Mock()

        mock.return_value = [-659882130]
        request_function.return_value = mock.return_value

        res = common.get_hash(['Test', 'test', 'TEST'])
        self.assertEqual(res[0], -659882130)

    def test_find_duplication2(self):
        data = common.find_duplication2([-659882130], [-659882130])
        self.assertEqual(data, 100.0)


if __name__ == '__main__':
    unittest.main()
