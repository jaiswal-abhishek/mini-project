#!/usr/bin/env
from bs4 import BeautifulSoup
import requests
import re
import urlparse
import argparse
import sys
import os
import json
import logging
import time
import shelve


class Crawler():
    """
    main crawler class which parse
    "http://mail-archives.apache.org/mod_mbox/maven-users/"
    link and download all mails  for given year
    """

    def __init__(self, main_url, year, folder):
        """
        Constructor to initialize the required values
        :param main_url: string
        :param year: string year for which mail will download
        :param folder: folder name in which mails will be stored
        :return:
        """

        # logger setting
        logging.basicConfig(
            filename='crawler.log',
            level=logging.INFO,
            format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s'
                   '- %(message)s',
            datefmt='%H:%M:%S'
        )

        # set up logging to console
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s '
                                      '%(message)s')
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('crawler_app').addHandler(console)

        self.logger = logging.getLogger('crawler_app')

        # configuration / init

        self.shelve_obj = None
        self.maven_url = main_url
        self.year = year
        self.file_ext = '.txt'
        self.counter = 0
        self.url_to_parse = list()
        self.list_year_month_url = list()
        self.folder = 'mailbox/'
        self.meta_file_name = self.folder + 'meta.shelve'
        self.process_folder(folder)

        list_url = self.parse_main_page()
        msg_year_month = self.parse_year_month_link()
        self.parse_raw_msg()

    def parse_main_page(self):
        """
        :return: list containing month mail url's
        """

        self.logger.info("Timestamp of start: " + time.strftime("%c"))
        try:
            response = requests.get(self.maven_url, timeout=5)
        except requests.exceptions.RequestException as e:
            self.logger.info(e)

            # writing meta file for resuming from last run

            self.shelve_obj['resume_function'] = 'parse_main_page'
            self.shelve_obj['maven_url'] = self.maven_url
            self.shelve_obj['counter'] = self.counter
            self.shelve_obj['status'] = 'incomplete'
            self.shelve_obj['list_year_month_url'] = self.list_year_month_url
            self.shelve_obj['url_to_parse'] = self.url_to_parse

            self.shelve_obj.close()

            sys.exit(0)

        pattern = re.compile(r'%s' % self.year)

        soup = BeautifulSoup(response.text)

        tables = soup.find('th', text=pattern)

        if not tables:
            self.logger.info('given year "{}" not found'.format(self.year))
            sys.exit(0)

        else:
            for table in tables:
                # self.logger.info(table.parent.parent.parent.parent)
                table_by_year = table.findParents('table', {'class': 'year'})
                list_year_month_url = list()

                for a_tags in table_by_year[0].\
                        find_all('a', href=True, text='Thread'):

                    # self.logger.info("Found the URL:",self.maven_url +
                    #             a_tags['href'])
                    self.list_year_month_url.append(self.maven_url +
                                                    a_tags['href'])

                return self.list_year_month_url

    def parse_year_month_link(self):
        """
        :param list_year_month_url:
        :return: list of tuple containing (url for raw msgs, year_month)
        """

        while len(self.list_year_month_url):
            year_month_url = self.list_year_month_url.pop()

            bool_next = True
            hostname = 'http://' + urlparse.urlparse(self.maven_url).hostname

            sliced_url = year_month_url.rsplit('/', 1)
            raw_msg_url = sliced_url[0] + '/raw/'
            msg_year_month = sliced_url[0][-11:-5]

            while bool_next:
                self.logger.info(year_month_url)
                try:
                    tag_response = requests.get(year_month_url, timeout=5)
                except requests.exceptions.RequestException as e:
                    self.logger.info(e)

                    # writing meta file for resuming from last run

                    self.shelve_obj['resume_function'] = 'parse_year_month_link'
                    self.shelve_obj['maven_url'] = self.maven_url
                    self.shelve_obj['counter'] = self.counter
                    self.shelve_obj['status'] = 'incomplete'
                    self.shelve_obj['list_year_month_url'] = self.list_year_month_url
                    self.shelve_obj['url_to_parse'] = self.url_to_parse

                    self.shelve_obj.close()

                    sys.exit(0)

                tag_soup = BeautifulSoup(tag_response.text)
                msg_list_table = tag_soup.find(id='msglist')

                # messages
                msg_table_rows = msg_list_table.findAll('tr')

                for table_row in msg_table_rows:

                    # author = table_row.find('td', {'class': 'author'})
                    subject = table_row.find('a', href=True)
                    # mail_date = table_row.find('td', {'class': 'date'})

                    if subject:
                        # self.logger.info(raw_msg_url + subject['href'] + '/')
                        self.url_to_parse.append([
                            raw_msg_url + subject['href'] + '/',
                            msg_year_month,
                        ])

                th_pages = msg_list_table.find('th', {'class': 'pages'})
                next_page = th_pages.find('a', href=True,
                                          text=re.compile(r'Next'))

                if next_page:
                    year_month_url = hostname + next_page['href']

                else:
                    bool_next = False

        return self.url_to_parse

    def parse_raw_msg(self):
        """
        :return: True on completion
        """

        # for url, msg_year_month in list_raw_msg_url:
        while len(self.url_to_parse):
            popped_list = self.url_to_parse.pop()
            url = popped_list[0]
            msg_year_month = popped_list[1]
            self.logger.info(url + '--' + msg_year_month)

            try:
                mail_response = requests.get(url, timeout=5)
            except requests.exceptions.RequestException as e:
                self.logger.info(e)

                # writing meta file for resuming from last run

                self.shelve_obj['resume_function'] = 'parse_raw_msg'
                self.shelve_obj['maven_url'] = self.maven_url
                self.shelve_obj['counter'] = self.counter
                self.shelve_obj['status'] = 'incomplete'
                self.shelve_obj['list_year_month_url'] = self.list_year_month_url
                self.shelve_obj['url_to_parse'] = self.url_to_parse

                self.shelve_obj.close()

                sys.exit(0)

            if mail_response.status_code == 200:
                # self.logger.info(mail_response.text)
                # writing files
                filename_path = self.folder + msg_year_month + '-' + \
                                str(self.counter) + self.file_ext

                if self.write_file(filename_path,
                                   mail_response.text.encode('utf-8')):
                    self.counter += 1

        self.shelve_obj['status'] = 'completed'

        self.shelve_obj.close()

        return True

    def process_folder(self, folder):
        """
        :param folder:
        :return: None
        """

        prefix_folder = 'mailbox/'

        if not folder:
            folder = str(self.year)

        self.meta_file_name = prefix_folder + folder + '/' + 'meta.txt'
        self.folder = prefix_folder + folder + '/'

        if os.path.exists(prefix_folder + folder):

            self.shelve_obj = shelve.open(self.meta_file_name)

            # checking last run state and loading values
            if self.shelve_obj['status'] == 'incomplete':

                self.logger.info('resuming....')
                self.counter = self.shelve_obj['counter']
                self.url_to_parse = self.shelve_obj['url_to_parse']
                self.list_year_month_url = self.shelve_obj['list_year_month_url']

                if self.shelve_obj['resume_function'] == 'parse_year_month_link':
                    self.parse_year_month_link()

                elif self.shelve_obj['resume_function'] == 'parse_main_page':
                    self.parse_main_page()

                elif self.shelve_obj['resume_function'] == 'parse_raw_msg':
                    self.parse_raw_msg()

        else:
            os.makedirs(prefix_folder + folder)
            self.shelve_obj = shelve.open(self.meta_file_name)

            self.folder = prefix_folder + folder + '/'

    def write_file(self, filename, data):
        """
        :param filename:
        :param data:
        :return:
        """

        new_file = open(filename, 'w')   # creating a new file
        new_file.write(data)
        new_file.close()
        self.logger.info('writing {}'.format(filename))
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="mini crawler project .")
    parser.add_argument('-y', '--year', type=int, required=True)
    parser.add_argument('-d', '--folder', type=str)
    args = parser.parse_args()
    # print args

    maven_url = 'http://mail-archives.apache.org/mod_mbox/maven-users/'
    crawler = Crawler(maven_url, args.year, args.folder)
