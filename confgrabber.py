#!/usr/bin/env python

from jsonrpclib import Server
import json
import ssl
import argparse
import string
import os


def grabconfig(directory, user, passwd, host):
    device = Server(
        'https://{}:{}@{}/command-api'.format(user, passwd, host))
    result = device.runCmds(
        version=1, cmds=['enable', 'show running-config'], format='text')
    with open(directory + '/' + host + '.txt', mode='wt', encoding='utf-8') as writer:
        for lines in result[1]['output']:
            writer.write(lines)


def main():
     parser = argparse.ArgumentParser()
     parser.add_argument(
         "-u", "--user", type=str, default="",
         help="specify a username", required=True)
     parser.add_argument(
         "-p", "--passwd", type=str, default="",
         help="for passing password interactively", required=True)
     parser.add_argument(
         "-f", "--file", type=str, default="",
         help="specify a file with EOS Devices from which to pull the running-config", required=True)
     parser.add_argument(
         "-d", "--directory", type=str, default=".",
         help="specify a directory to download configs to (note: no trailing '/'", required=False)
     args = parser.parse_args()

     file = args.file
     user = args.user
     passwd = args.passwd
     directory = args.directory

     with open(file, 'r') as current_file:
         hostnames = current_file.readlines()
         current_file.close()
     _create_unverified_https_context = ssl._create_unverified_context
     ssl._create_default_https_context = _create_unverified_https_context

# split the hostnames list array in N parts
# create a thread for each array as a for loop of N subarrays
# run grabconfig() in each thread on subarray of eos devices
# execute threads
     for hostname in hostnames:
         host = hostname.strip()
         response = os.system(f"ping -c 2 {host} > /dev/null 2>&1")
         if response == 0:
             pingstatus = "Network Active"
             try:
                grabconfig(directory, user, passwd, host)
             except Exception as e:
                 print(f"something went wrong, check password\n\n{str(e)}\n")
         else:
           pingstatus = "Network Error"
           print(f"{host} does not respond to ping, moving on..\n")


if __name__ == '__main__':
    main()
