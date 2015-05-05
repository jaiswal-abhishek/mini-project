import unittest
import shutil
import crawler


class CrawlerTest(unittest.TestCase):

    def test_creating_folder(self):
        result = crawler.process_folder(2014, '2014')
        self.assertEqual('mailbox/2014/', result)

    def test_folder_exists_error(self):
        with self.assertRaises(SystemExit) as cm:
            crawler.process_folder(2014, '2014')

        self.assertEqual(cm.exception.code, 0)

        # deleting folder
        shutil.rmtree('mailbox/2014/')



if __name__ == '__main__':
    unittest.main()