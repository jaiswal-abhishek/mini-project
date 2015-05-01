import argparse
from datetime import datetime
import sys
import mailbox
import urllib
import os
import shutil
import glob


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
    prefix_folder = 'mailbox/'

    def mailbox_folder_processing(self, year, folder, force):
        """
        Function

        :param year:
        :param folder:
        :param force:
        :return:
        """

        if not folder:
            folder = str(year)

        if os.path.exists(self.prefix_folder + folder):

            if force:
                # print 'force creation'
                shutil.rmtree(self.prefix_folder + folder)
                os.makedirs(self.prefix_folder + folder)
                self.download_mailbox_file(year, 1, self.prefix_folder + folder)

            else:
                # print 'folder exists'
                last_file = max(glob.iglob(self.prefix_folder + folder + '/*'), key=os.path.getctime)
                file_name = os.path.splitext(os.path.basename(last_file))[0]
                self.download_mailbox_file(year, int(file_name[-2:]), self.prefix_folder + folder)

        else:
            os.makedirs(self.prefix_folder + folder)
            self.download_mailbox_file(year, 1, self.prefix_folder + folder)
            # print 'folder created'

    def download_mailbox_file(self, year, month, folder):
        """

        :param year:
        :return:
        """

        for year_month in self.generate_year_month(year, month):
            new_generated_url = self.url + str(year_month) + '.mbox'
            print new_generated_url

            save_as = folder + '/' + str(year_month) + '.mbox'

            mail_file = urllib.URLopener()
            mail_file.retrieve(new_generated_url, save_as)

    def generate_year_month(self, year, month=1):
        """

        :param year:
        :param month:
        :return:
        """

        curr_year = datetime.now().year

        if year > curr_year:
            print 'future date given'
            sys.exit(0)

        elif year == curr_year:
            month = datetime.now().month

        while month <= 12:
            yield str(year) + "%02d" % month
            month += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="mini crawler project .")
    parser.add_argument('-y', '--year', type=int, required=True)
    parser.add_argument('-d', '--folder', type=str)
    parser.add_argument('-f', '--force', const=1, nargs='?')

    args = parser.parse_args()
    # print args

    crawler = Crawler()

    # check folder exists
    crawler.mailbox_folder_processing(args.year, args.folder, args.force)

    os.system('nautilus mailbox/')