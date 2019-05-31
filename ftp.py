#!/usr/bin/python

from ftplib import FTP
from os import path
class Ftp():

    def __init__(self, host=None, user=None, password=None, case=None):
        self.host = host
        self.user = user
        self.password = password
        self.case = case
        self.error = None

        if None in (self.host, self.user, self.password):
            self.error = "Invalid input received"
            return None

        self.ftp = FTP()
        try:
            self.ftp.connect(self.host, timeout=20)
        except Exception as error:
            self.error = error
            return None

        try:
            self.ftp.login(user=self.user, passwd=self.password)
        except Exception as error:
            self.error = error
            return None

    def upload(self, file=None):

        if file is None:
            self.error = "No input file received"
            return False

        if not path.exists(file):
            self.error = "Input file not exists"
            return False

        file_name = path.basename(file)

        try:
            with open(file, 'rb') as infile:
                self.ftp.storbinary('STOR '+file_name, infile, 8192)
        except Exception as error:
            self.error = error
            return False
        else:
            return True

    def download(self, file=None, dir=None):

        if file is None:
            self.error = "No file name received to download from the {}".format(self.host)
            return False

        if dir is None:
            dir = '/tmp'

        if not path.exists(dir):
            self.error = "Destination directory {} not exists in local".format(dir)
            return False

        file_path = dir + '/' + file
        try:
            with open(file_path, 'wb') as outfile:
                self.ftp.retrbinary('RETR '+file, outfile.write)
        except Exception as error:
            self.error = error
            return False
        else:
            return True

    def ls(self):
        try:
            list = self.ftp.nlst()
        except Exception as error:
            self.error = error
            return False
        else:
            return list


if __name__ == '__main__':
    ftp = Ftp(host='localhost', user='kannan', password='******')
    if ftp.upload('servers'):
        print("file uploaded")
    else:
        print(ftp.error)

    if ftp.download('config'):
        print('file downloaded')
    else:
        print(ftp.error)
    lists = ftp.ls()
    if lists is not False:
        for list in lists:
            print(list)
    else:
        print(ftp.error)

