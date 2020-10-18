#!/usr/bin/env python3
#
# Copyright (c) 2020, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  - Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#  - Neither the name of Arista Networks nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# config-tool.py -- this is a very generic name, it may change
#
#    Written by:
#       Corey Hines, Arista Networks
#
"""
DESCRIPTION
an attempt to recover EOS configuration stanzas that are common amongst a corpus of configs
"""

import pathlib
from collections import Counter
import re
import argparse
import os

from os.path import expanduser
home = expanduser("~")

mydir = home + "/vs-code/config-tool/configs/"

# Using Collections Counter seems like it is working better than this method
# def get_dupes(L):
#     seen = set()
#     seen2 = set()
#     seen_add = seen.add
#     seen2_add = seen2.add
#     for item in L:
#         if item in seen:
#             seen2_add(item)
#         else:
#             seen_add(item)
#     return list(seen2)


def search_comments(line):
    regex_match = re.compile(r'^\s*!!.*', re.M)
    re_match = re.findall(regex_match, line)
    return list(re_match)


parser = argparse.ArgumentParser()
parser.add_argument(
    "-c", "--count", type=str, default="3", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "all"],
    help="specify min count", required=False)

args = parser.parse_args()


regex_sub = re.compile(r'^\s*!!.*', re.M)
regex_sub2 = re.compile(r'^>.*', re.M)
regex_sub3 = re.compile(r'^\s.*Command:.*', re.M)
regex_sub4 = re.compile(r'^!.*boot\ssystem.*', re.M)

# ↓↓↓ this is a work in progress
# this will become a feature for a user defined regex based
# on a flag and an argument like --regex 'some_regexi or just a string to ignore'
# This will provide ability to ignore descriptions and other items in regard to
# finding common config stanzas.
# Note: the way this is done will remove the string, so it is destructive
#regex_sub5 = re.compile(r'LEAF[0-9]|SPINE[0-9]$', re.M | re.IGNORECASE)
regex_sub5 = re.compile(r'\s.*description.*', re.M | re.IGNORECASE)

stanzas = []
comments = []
num_files = str(
    len([name for name in os.listdir(mydir) if os.path.isfile(name)]))

if args.count == "all":
    mincount = num_files
else:
    mincount = args.count

for path in pathlib.Path(mydir).iterdir():
    if path.is_file():
        current_file = open(path, "r")
        content = current_file.read()
        comments += search_comments(content)
        subcontent = re.sub(regex_sub, "", content)
        subcontent = re.sub(regex_sub2, "", subcontent)
        subcontent = re.sub(regex_sub3, "", subcontent)
        subcontent = re.sub(regex_sub4, "", subcontent)
        subcontent = re.sub(regex_sub5, "", subcontent)

        stanzas += subcontent.split('!')
        current_file.close()

# these print statements are for debugging/testing
# print(len(stanzas))
# print(len(comments))

comments = set(comments)

# stanzas now contains any stanza seen twice.
# This loop will print only stanzas that were seen 3 or more times
# The idea here is to reduce the noise and produce "universal" configlet material
for k, v in Counter(stanzas).items():
    if v >= int(mincount):
        print(k)
        print('\x1b[6;30;42m' + "↑ SEEN ->(" +
              str(v) + "/" + num_files + ")<- TIMES ↑" + '\x1b[0m' + "\n")

# Coments list for review
print("\n\n##################### COMMENTS  '!!' found in corpus #######################")
print("\n".join(comments))
