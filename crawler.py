#!/usr/bin/env
from bs4 import BeautifulSoup
import requests
import re
import urlparse
import argparse
import sys
import os
import json


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

        self.maven_url = main_url
        self.year = year
        self.folder = self.process_folder(folder)
        self.file_ext = '.txt'
        self.counter = 0

    def parse_main_page(self):
        """
        :return:
        """

        try:
            response = requests.get(self.maven_url, timeout=5)
        except requests.exceptions.RequestException as e:
            print e
            # print 'write meta'
            data = {
                'maven_url': self.maven_url,
            }
            sys.exit(1)

        pattern = re.compile(r'%s' % self.year)

        soup = BeautifulSoup(response.text)

        tables = soup.find('th', text=pattern)

        if not tables:
            print 'given year "{}" not found'.format(self.year)

        else:
            for table in tables:
                # print table.parent.parent.parent.parent
                table_by_year = table.findParents('table', {'class': 'year'})

                for a_tags in table_by_year[0].\
                        find_all('a', href=True, text='Thread'):

                    # print "Found the URL:", a_tags['href']
                    year_month_url = self.maven_url + a_tags['href']
                    self.parse_year_month_link(year_month_url)

    def parse_year_month_link(self, year_month_url):
        """
        :param year_month_url:
        :return:
        """

        bool_next = True
        hostname = 'http://' + urlparse.urlparse(self.maven_url).hostname

        sliced_url = year_month_url.rsplit('/', 1)
        raw_msg_url = sliced_url[0] + '/raw/'
        msg_year_month = sliced_url[0][-11:-5]
        self.counter = 0

        while bool_next:
            print year_month_url
            try:
                tag_response = requests.get(year_month_url, timeout=5)
            except requests.exceptions.RequestException as e:
                print e
                # print 'write meta'
                sys.exit(1)

            tag_soup = BeautifulSoup(tag_response.text)
            msg_list_table = tag_soup.find(id='msglist')

            # messages
            msg_table_rows = msg_list_table.findAll('tr')
            for table_row in msg_table_rows:

                # author = table_row.find('td', {'class': 'author'})
                subject = table_row.find('a', href=True)
                # mail_date = table_row.find('td', {'class': 'date'})

                if subject:
                    # print raw_msg_url + subject['href'] + '/'
                    self.parse_raw_msg(raw_msg_url +
                                       subject['href'] + '/', msg_year_month)

            th_pages = msg_list_table.find('th', {'class': 'pages'})
            next_page = th_pages.find('a', href=True, text=re.compile(r'Next'))
            if next_page:
                year_month_url = hostname + next_page['href']

            else:
                bool_next = False

    def parse_raw_msg(self, url, msg_year_month):
        """
        :param url:
        :param msg_year_month:
        :return:
        """

        try:
            mail_response = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as e:
            print e
            # print 'write meta'
            sys.exit(1)

        if mail_response.status_code == 200:
            # print mail_response.text
            # writing files
            filename_path = self.folder + msg_year_month + '-' + \
                            str(self.counter) + self.file_ext

            if self.write_file(filename_path,
                               mail_response.text.encode('utf-8')):
                self.counter += 1

    def process_folder(self, folder):
        """
        :param folder:
        :return:
        """

        prefix_folder = 'mailbox/'

        if not folder:
            folder = str(self.year)

        if os.path.exists(prefix_folder + folder):
            print 'Folder exists try another folder_name'
            sys.exit(0)

        else:
            os.makedirs(prefix_folder + folder)

            return prefix_folder + folder + '/'

    def write_file(self, filename, data):
        """
        :param filename:
        :param data:
        :return:
        """

        new_file = open(filename, 'w')   # creating a new file
        new_file.write(data)
        new_file.close()
        print 'writing {}'.format(filename)
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="mini crawler project .")
    parser.add_argument('-y', '--year', type=int, required=True)
    parser.add_argument('-d', '--folder', type=str)
    args = parser.parse_args()

    maven_url = 'http://mail-archives.apache.org/mod_mbox/maven-users/'
    crawler = Crawler(maven_url, args.year, args.folder)

    crawler.parse_main_page()
