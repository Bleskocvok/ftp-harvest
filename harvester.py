
import ftplib
import time
import os
from pathlib import Path


class FTPConnection:
    def __init__(self, server, port=21, username='anonymous', password='anonymous'):
        self.server = server
        self.port = port
        self.username = username
        self.password = password


class Harvester:
    def __init__(self, connection, files, interval=5):
        self.con = connection
        self.files = files
        self.interval = interval

    def load(self):
        with ftplib.FTP(self.con.server, self.con.username, self.con.password) as ftp:
            for fname in self.files:
                dirname = os.path.dirname(fname)
                ls = ftp.nlst(dirname)
                Path(dirname).mkdir(parents=True, exist_ok=True)
                self._load_file(fname, ftp, ls)

    def save(self):
        with ftplib.FTP(self.con.server, self.con.username, self.con.password) as ftp:
            for fname in self.files:
                self._save_file(fname, ftp)

    def _load_file(self, filename, ftp, ls):
        if filename not in ls:
            return
        with open(filename, 'wb') as f:
            ftp.retrbinary('RETR ' + filename, f.write)

    def _save_file(self, filename, ftp):
        dirname = os.path.dirname(filename)
        dirs = self._get_dirs(dirname)
        for dir in dirs:
            head, tail = os.path.split(dir)
            if dir not in ftp.nlst(head):
                ftp.mkd(dir)
        try:
            with open(filename, 'rb') as f:
                ftp.storbinary('STOR ' + filename, f)
        except:
            pass  # ignore errors when file doesn't exist

    def _get_dirs(self, dirname):
        dirs = []
        last = dirname
        while last:
            dirs.append(last)
            head, _ = os.path.split(last)
            last = head
        dirs.sort()  # sorts by length, so that it creates the dirs in the correct order
        return dirs
