from bs4 import BeautifulSoup
import requests
import argparse
from datetime import datetime
import sys


class Crawler:
    """
    Main class
    """

    def __init__(self):
        """

        :return:
        """
        pass

    url = 'http://mail-archives.apache.org/mod_mbox/maven-users/'

    def start_crawl(self, year):
        """

        :param year:
        :return:
        """

        month = 12
        curr_year = datetime.now().year

        if year > curr_year:
            print 'future date given'
            sys.exit(0)

        elif year == curr_year:
            month = datetime.now().month

        for i in xrange(1, month + 1):
            new_generated_url = self.url + str(year) + "%02d" % i + '.mbox/'

           # while page:

            link_to_fetch = new_generated_url + 'ajax/thread'

            print link_to_fetch

            response = requests.get(link_to_fetch)

            soup = BeautifulSoup(response.text, 'xml')
            index = soup.find_all('index')
            total_page = index[0]['pages']


            all_messages = soup.find_all('message')
            for msg_tag in all_messages:
                msg_id = msg_tag['id']
                message = requests.get(new_generated_url + 'ajax/' + msg_id) .text

                print message


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="mini crawler project .")
    parser.add_argument('-y', '--year', type=int, required=True)

    args = parser.parse_args()
    # print args

    crawler = Crawler()

    crawler.start_crawl(args.year)