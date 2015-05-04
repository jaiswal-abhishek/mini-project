from bs4 import BeautifulSoup
import requests
import re
import urlparse
import sys


def crawler(url, year):
    """

    :param url:
    :param year:
    :return:
    """

    response = requests.get(url)
    pattern = re.compile(r'%s' % year)
    hostname = 'http://' + urlparse.urlparse(url).hostname

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
                year_url = url + list_url_chunks[0]
                bool_next = True
                counter = 0
                fetch_url = url + a_tags['href']

                while bool_next:

                    print fetch_url

                    tag_response = requests.get(fetch_url)
                    tag_soup = BeautifulSoup(tag_response.text)
                    msg_list_table = tag_soup.find(id='msglist')

                    #messages
                    msg_table_rows = msg_list_table.findAll('tr')
                    for table_row in msg_table_rows:
                        counter += 1

                        author = table_row.find('td', {'class': 'author'})
                        subject = table_row.find('a', href=True)
                        date = table_row.find('td', {'class': 'date'})

                        if author:
                            print author.renderContents()

                        if subject:
                            print subject.renderContents()
                            print subject['href']

                        if date:
                            print date.renderContents()
                        print '--------------------------------'
                        """cols = table_row.findAll('td')
                        for td in cols:
                            # print td.renderContents().strip()
                            td.find('')"""

                    th_pages = msg_list_table.find('th', {'class': 'pages'})
                    next_page = th_pages.find('a', href=True, text=re.compile(r'Next'))
                    if next_page:
                        fetch_url = hostname + next_page['href']

                    else:
                        bool_next = False

                print "total message" + str(counter)


crawler('http://mail-archives.apache.org/mod_mbox/maven-users/', 2014)
