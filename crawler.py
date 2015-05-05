#!/usr/bin/env
from bs4 import BeautifulSoup
import requests
import re
import urlparse
import argparse
import sys
import traceback
import os
import json


def crawler(maven_url, year, folder_name):
    """

    :param maven_url:
    :param year:
    :param folder_name:
    :return:
    """
    try:

        file_ext = '.txt'
        response = requests.get(maven_url)
        pattern = re.compile(r'%s' % year)
        hostname = 'http://' + urlparse.urlparse(maven_url).hostname

        soup = BeautifulSoup(response.text)

        tables = soup.find('th', text=pattern)

        if not tables:
            print 'given year "{}" not found'.format(year)

        else:
            for table in tables:
                # print table.parent.parent.parent.parent
                table_by_year = table.findParents('table', {'class': 'year'})

                for a_tags in table_by_year[0].find_all('a', href=True, text='Thread'):
                    # print "Found the URL:", a_tags['href']

                    # getting the year_url for fetching message as
                    list_url_chunks = a_tags['href'].split('/')
                    year_url = maven_url + list_url_chunks[0]
                    bool_next = True
                    counter = 0
                    fetch_url = maven_url + a_tags['href']

                    while bool_next:

                        print 'fetch_url ' + fetch_url

                        tag_response = requests.get(fetch_url)
                        tag_soup = BeautifulSoup(tag_response.text)
                        msg_list_table = tag_soup.find(id='msglist')

                        # messages
                        msg_table_rows = msg_list_table.findAll('tr')
                        for table_row in msg_table_rows:

                            # author = table_row.find('td', {'class': 'author'})
                            subject = table_row.find('a', href=True)
                            mail_date = table_row.find('td', {'class': 'date'})

                            if subject:

                                # print year_url + '/raw/' + subject['href'] + '/'
                                mail_response = requests.get(year_url + '/raw/' + subject['href'] + '/')
                                if mail_response.status_code == 200:
                                    # print mail_response.text
                                    # writing files
                                    filename_path = folder_name + year_url[-11:-5] + '-' + str(counter) + file_ext
                                    # for json data uncomment
                                    """
                                    data = {
                                        'mail': mail_response.text.encode('utf-8'),
                                        'mail_url': year_url + '/raw/' + subject['href'] + '/',
                                        'mail_date':  mail_date.renderContents() if mail_date else '',

                                    }"""

                                    if write_file(filename_path, mail_response.text.encode('utf-8')):
                                        counter += 1

                        # for loop end for every msg in list

                        th_pages = msg_list_table.find('th', {'class': 'pages'})
                        next_page = th_pages.find('a', href=True, text=re.compile(r'Next'))
                        if next_page:
                            fetch_url = hostname + next_page['href']

                        else:
                            bool_next = False

                    print "total message" + str(counter)

    except Exception, err:
        print traceback.format_exc()


def process_folder(year, folder):
    """

    :param year:
    :param folder:
    :return: string folder path
    """

    prefix_folder = 'mailbox/'

    try:
        if not folder:
            folder = str(year)

        if os.path.exists(prefix_folder + folder):
            print 'Folder exists try another folder_name'
            sys.exit(0)

        else:
            os.makedirs(prefix_folder + folder)

            return prefix_folder + folder +'/'

    except Exception, err:
        print traceback.format_exc()


def write_file(filename, data):
    """

    :param filename:
    :param data:
    :return: boolean, true if success false if fails
    """

    try:
        new_file = open(filename,'w')   # creating a new file
        new_file.write(data)
        new_file.close()
        print 'writing {}'.format(filename)
        return True

    except Exception, err:
        print traceback.format_exc()
        return False



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="mini crawler project .")
    parser.add_argument('-y', '--year', type=int, required=True)
    parser.add_argument('-d', '--folder', type=str)
    args = parser.parse_args()

    maven_url = 'http://mail-archives.apache.org/mod_mbox/maven-users/'

    # folder checking
    folder_name = process_folder(args.year, args.folder)

    crawler(maven_url, args.year, folder_name)
