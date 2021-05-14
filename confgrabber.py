#!/usr/bin/env python

from jsonrpclib import Server
import json
import ssl
import argparse
import string


def main():
     parser = argparse.ArgumentParser()
     parser.add_argument(
         "-u", "--user", type=str, default="",
         help="specify a username", required=True)
     parser.add_argument(
         "-f", "--file", type=str, default="",
         help="specify a file with EOS Devices from which to pull the running-config", required=True)
     parser.add_argument(
         "-p", "--passwd", type=str, default="",
         help="for passing password interactively", required=True)
     args = parser.parse_args()

     file = args.file
     user = args.user
     passwd = args.passwd

     with open(file, 'r') as current_file:
         hostnames = current_file.readlines()
         current_file.close()
     _create_unverified_https_context = ssl._create_unverified_context
     ssl._create_default_https_context = _create_unverified_https_context

     for hostname in hostnames:
        # _create_unverified_https_context = ssl._create_unverified_context
        # ssl._create_default_https_context = _create_unverified_https_context
         host = hostname.strip()
         try:
            device = Server(
                'https://{}:{}@{}/command-api'.format(user, passwd, host))
            result = device.runCmds(
                version=1, cmds=['enable', 'show running-config'], format='text')
            with open('./' + host + '.txt', mode='wt', encoding='utf-8') as writer:
               for lines in result[1]['output']:
                   writer.write(lines)
         except Exception as e:
             print("something went wrong, check password\n\n" + str(e))


if __name__ == '__main__':
    main()
