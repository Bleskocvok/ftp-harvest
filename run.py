#!/usr/bin/env python3

import os
#import ftplib
#import time
import sys
from dotenv import load_dotenv

from harvester import *


'''
LAUNCH
'''
load_dotenv()

# ftp default values
server = None
port = 21
username = 'anonymous'
password = 'anonymous'

# load ftp variables
server = os.getenv('FTP_SERVER')
port = os.getenv('FTP_PORT', port)
username = os.getenv('FTP_USERNAME', username)
password = os.getenv('FTP_PASSWORD', password)

# file containing list of files to look for
listfile = 'harvestlist.txt'

# files to look for
files = []

if not os.path.isfile(listfile):
    print('ERROR: File \'' + listfile + '\' required, but not found in the current working directory')
    sys.exit(1)

try:
    with open(listfile, 'r') as f:
        for one in f.readlines():
            one = one.strip()
            one = one.split('#')[0]
            if one:  # not empty
                files.append(one)
except IOError as e:
    print('ERROR: File \'' + listfile + '\': ' + str(e))

if server is None:
    print('ERROR: Environment variable {} not specified'.format('FTP_SERVER'))
    sys.exit(1)

print('Connecting to FTP: {}'.format(server))

connection = FTPConnection(server, port, username, password)
harvester = Harvester(connection, files)

#harvester.load()
harvester.save()