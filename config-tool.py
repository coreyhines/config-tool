#!/usr/bin/env python3

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


def search_comments(line):
    """collect the comments

    Args:
        line (string): line of config to search for comments

    Returns:
        list: list of lines with comments
    """
    regex_match = re.compile(r'^\s*!!.*', re.M)
    re_match = re.findall(regex_match, line)
    return list(re_match)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
       "-c", "--count", type=str, default="3", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "all"],
       help="specify min count", required=False)
    parser.add_argument(
        "-m", "--mask", type=str, default="",
        help="specify a string to ignore, e.g. 'description'\n to ingnore and replace descriptions", required=False)
    parser.add_argument(
        "-d", "--directory", type=str, default="",
     help="directory that contains EOS configuration files", required=False)
    args = parser.parse_args()

    stanzas = []
    comments = []

    home = expanduser("~")
    if args.directory:
        mydir = args.directory
    else:
        mydir = home + "/vs-code/config-tool/configs/"

    num_files = str(
        len([name for name in os.listdir(mydir) if os.path.isfile(mydir+'/'+name)]))

    if args.count == "all":
        mincount = num_files
    else:
        mincount = args.count

    # Series of regex statements to remove extraneous unusable config patterns
    regex_sub = re.compile(r'^\s*!!.*|^>.*|^end.*|', re.M)
    regex_sub2 = re.compile(r'^\s.*Command:.*', re.M)
    regex_sub3 = re.compile(r'(^\s+)!(.*)', re.M)
    regex_sub4 = re.compile(r'^!.*boot\ssystem.*', re.M)
    regex_sub5 = re.compile(r'(^\s+)#(.*)', re.M)

    for path in pathlib.Path(mydir).iterdir():
        if path.is_file():
            current_file = open(path, "r")
            content = current_file.read()
            comments += search_comments(content)
            subcontent = re.sub(regex_sub, "", content)
            subcontent = re.sub(regex_sub2, "", subcontent)
            # change any '!' with preceding whitespace to a '#'
            # We will change those back at the end
            subcontent = re.sub(regex_sub3, r"\1#\2", subcontent)
            subcontent = re.sub(regex_sub4, "", subcontent)
            if args.mask:
                ignore_mask = args.mask
                regex_sub6 = re.compile(
                    r'(.*{}).*'.format(ignore_mask), re.M | re.IGNORECASE)
                subcontent = re.sub(regex_sub6, r"\1", subcontent)

            stanzas += subcontent.split('!')
            current_file.close()

    # print statements for debugging/testing
    # print(len(stanzas))

    # This loop will print only stanzas that were seen 'min_count' or more times
    for k, v in sorted(Counter(stanzas).items()):
        if v >= int(mincount) and v <= int(num_files):
            # substitute the '  !' back in for the '#' used to trick the split parser earlier
            print(re.sub(regex_sub5, r"\1!\2", k))
            print('\x1b[6;30;42m' + "↑ SEEN ->(" +
                  str(v) + "/" + num_files + ")<- TIMES ↑" + '\x1b[0m' + "\n")

    # Coments list for review
    # print(len(comments))
    comments = set(comments)
    print("\n\n##################### COMMENTS  '!!' found in corpus #######################")
    print("\n".join(comments))


if __name__ == '__main__':
    main()
