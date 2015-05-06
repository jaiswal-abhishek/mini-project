import unittest
import shutil
from crawler import Crawler


class CrawlerTest(unittest.TestCase):

    def test_creating_folder(self):
        maven_url = 'http://mail-archives.apache.org/mod_mbox/maven-users/'
        crawler = Crawler(maven_url, '2014', None)
        self.assertEqual('mailbox/2014/', crawler.folder)

    def test_folder_exists_error(self):
        maven_url = 'http://mail-archives.apache.org/mod_mbox/maven-users/'

        with self.assertRaises(SystemExit) as cm:
            crawler = Crawler(maven_url, '2014', None)

        self.assertEqual(cm.exception.code, 0)

        # deleting folder
        shutil.rmtree('mailbox/2014/')



if __name__ == '__main__':
    unittest.main()