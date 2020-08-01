
import ftplib
import time
import os
import ast
from pathlib import Path


class FTPConnection:
    def __init__(self, server, port=21, username='anonymous', password='anonymous'):
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    def load(self, files):
        if not files:
            return
        with ftplib.FTP(self.server, self.username, self.password) as ftp:
            for fname in files:
                dirname = os.path.dirname(fname)
                ls = ftp.nlst(dirname)
                Path(dirname).mkdir(parents=True, exist_ok=True)
                self._load_file(fname, ftp, ls)

    def save(self, files):
        if not files:
            return
        with ftplib.FTP(self.server, self.username, self.password) as ftp:
            for fname in files:
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


class Harvester:
    def __init__(self, connection, files):
        self.con = connection
        self.files = files
        self.mtimes = {}

    def load(self):
        self.con.load(self.files)
        for f in self.files:
            if os.path.isfile(f):
                self.mtimes[f] = self.getmtime(f)

    def save(self):
        print('saving')
        files_to_save = []
        for f in self.files:
            if os.path.isfile(f):
                current = self.getmtime(f)
                if self.mtimes[f] != current or current == 0:
                    self.mtimes[f] = current
                    files_to_save.append(f)
                    print('save {}'.format(f))
                else:
                    print('ignoring {}'.format(f))
        self.con.save(files_to_save)
        print('finished')

    def getmtime(self, filename):
        try:
            return os.path.getmtime(filename)
        except Exception as e:
            print("WARNING: " + str(e))
        return 0

    def save_cache(self, cache_file):
        with open(cache_file, 'w') as f:
            f.write(str(self.mtimes))

    def load_cache(self, cache_file):
        with open(cache_file, 'r') as f:
            self.mtimes = ast.literal_eval(f.read())
