#!/usr/bin/env python3

import os
import time
import sys
import argparse
from dotenv import load_dotenv

from harvester import *


'''
LAUNCH
'''
# ftp default values
server = None
port = 21
username = 'anonymous'
password = 'anonymous'

# load ftp variables
load_dotenv()  # loads environment vars from the '.env' file if present
server = os.getenv('FTP_SERVER')
port = os.getenv('FTP_PORT', port)
username = os.getenv('FTP_USERNAME', username)
password = os.getenv('FTP_PASSWORD', password)

# file names used by this script
listfile = 'harvestlist.txt'
cache_file = '.harvestcache'

# the default interval for backups
default_interval = 5

# list of files to look for
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

parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='\
FTP Harvest.\n\
If no arguments are provided, the default behavior is equivalent to:\n\
{} -lb 5\n\n\
Uses these environment variables:\n\
* FTP_SERVER\n\
* FTP_PORT (=21)\n\
* FTP_USERNAME (=anonymous)\n\
* FTP_PASSWORD (=anonymous)\n\
FTP_SERVER must be specified and be a valid FTP server address'.format(sys.argv[0]))
parser.add_argument('-l', '--load', action='store_true',
        help='loads files specified in {} from the FTP server'.format(listfile))
parser.add_argument('-b', '--backup', type=int, metavar='INTERVAL', default=0,
        help='periodically saves files in {} to the FTP server; INTERVAL is in minutes'.format(listfile))
parser.add_argument('-s', '--save', action='store_true',
        help='sends current files to the FTP server')

result = parser.parse_args(sys.argv[1:])

# default behavior when no arguments are provided
if result.backup == 0 and not result.load and not result.save:
    result.backup = default_interval
    result.load = True
    print('Invoking default behavior')

print('Connecting to FTP: {}'.format(server))

connection = FTPConnection(server, port, username, password)
harvester = Harvester(connection, files)

if result.save:
    print('Sending files to the server...')
    harvester.save()
    print('Sending finished')

if result.load:
    print('Loading from server...')
    harvester.load()
    if result.backup  == 0:
        # caches file modification times so that the when this program is
        # run again with -b it can access this data
        harvester.save_cache(cache_file)
    print('Loading finished')

if result.backup > 0:
    print('Started backup cycle (interval = {} min)'.format(result.backup))
    if not result.load:
        harvester.load_cache(cache_file)
    while True:
        time.sleep(result.backup * 60)
        harvester.save()
