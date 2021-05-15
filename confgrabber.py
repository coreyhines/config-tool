#!/usr/bin/env python

from jsonrpclib import Server
import json
import ssl
import argparse
import string
import os
import time
import threading
import multiprocessing
import numpy as np


def grabconfig(hostnames, user, passwd, directory):
    for hostname in hostnames:
       host = hostname.strip()
       _create_unverified_https_context = ssl._create_unverified_context
       ssl._create_default_https_context = _create_unverified_https_context
       response = os.system(f"ping -c 2 {host} > /dev/null 2>&1")
       if response == 0:
           pingstatus = "Network Active"
           #print(f"ping status for {host}: {pingstatus}")
           try:
               device = Server(
                   'https://{}:{}@{}/command-api'.format(user, passwd, host))
               result = device.runCmds(
                   version=1, cmds=['enable', 'show running-config'], format='text')
               with open(directory + '/' + host + '.txt', mode='wt', encoding='utf-8') as writer:
                  for lines in result[1]['output']:
                     writer.write(lines)
              # grabconfig(directory, user, passwd, host)
           except Exception as e:
               print(
                   f"something went wrong on {host}, check password\n\n{str(e)}\n")
       else:
          pingstatus = "Network Error"
          print(f"{pingstatus}: {host} does not respond to ping, moving on..\n")


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

# split the hostnames list array in N parts
# create a thread for each list
# run grabconfig() in each thread on subarray of eos devices
# execute threads
     split = np.array_split(hostnames, 8)
     #create two threads her t1 & t2
     arr1 = list(split[0])
     arr2 = list(split[1])
     arr3 = list(split[2])
     arr4 = list(split[3])
     arr5 = list(split[4])
     arr6 = list(split[5])
     arr7 = list(split[6])
     arr8 = list(split[7])
     t1 = multiprocessing.Process(target=grabconfig, args=(
         arr1, user, passwd, directory))
     t2 = multiprocessing.Process(target=grabconfig, args=(
         arr2, user, passwd, directory))
     t3 = multiprocessing.Process(target=grabconfig, args=(
         arr3, user, passwd, directory))
     t4 = multiprocessing.Process(target=grabconfig, args=(
         arr4, user, passwd, directory))
     t5 = multiprocessing.Process(target=grabconfig, args=(
         arr5, user, passwd, directory))
     t6 = multiprocessing.Process(target=grabconfig, args=(
         arr6, user, passwd, directory))
     t7 = multiprocessing.Process(target=grabconfig, args=(
         arr7, user, passwd, directory))
     t8 = multiprocessing.Process(target=grabconfig, args=(
         arr8, user, passwd, directory))
     #start threads in parallel
     t1.start()
     t2.start()
     t3.start()
     t4.start()
     t5.start()
     t6.start()
     t7.start()
     t8.start()
     # join will wait for functions to finish
     t1.join()
     t2.join()
     t3.join()
     t4.join()
     t5.join()
     t6.join()
     t7.join()
     t8.join()
     print(f"Done!")


if __name__ == '__main__':
    main()
