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
"""DESCRIPTION
an attempt to recover EOS configuration stanzas
that are common or distinct amongst a corpus of configs
This tool can be used to help create configlets for
CloudVision Portal
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
    regex_match = re.compile(r"^\s*!!.*", re.M)
    re_match = re.findall(regex_match, line)
    return list(re_match)


def fix_ups(line):
    """ fix any issues with the stanzas
    Example these lines will appear as one stanza:

       hostname superswitch101
       ip name-server vrf mgmt foo.com
       ip name-server vrf mgmt foo2.com
       dns domain bar.com 
    
    If hostname is separated, the following 3 
    lines are likely to be shared among some or 
    all of the configs

       hostname superswitch101
       !
       ip name-server vrf mgmt foo.com
       ip name-server vrf mgmt foo2.com
       dns domain bar.com 
    """   
    regex_match = re.compile(r"^(hostname.*)", re.M)
    re_match = re.sub(regex_match, r"\1\n!", line)
    return str(re_match)
       
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--count",
        type=str,
        default="3",
        choices=[
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "all",
            "none",
        ],
        help="specify min count",
        required=False,
    )
    parser.add_argument(
        "-m",
        "--mask",
        type=str,
        default="",
        help="specify a string to ignore, e.g. 'description'\n to ingnore and replace descriptions",
        required=False,
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default="",
        help="directory that contains EOS configuration files",
        required=False,
    )
    args = parser.parse_args()

    stanzas = []
    device_stanzas = {}
    common_stanzas = []
    comments = []

    home = expanduser("~")
    if args.directory:
        mydir = args.directory
    else:
        mydir = home + "/vs-code/config-tool/configs/"

    num_files = str(
        len(
            [
                name
                for name in os.listdir(mydir)
                if os.path.isfile(mydir + "/" + name)
            ]
        )
    )

    if args.count == "all":
        mincount = num_files
        maxcount = num_files
    elif args.count == "none":
        maxcount = 1
    else:
        mincount = args.count
        maxcount = args.count

    # Series of regex statements to remove extraneous unusable config patterns
    regex_sub_doublebang = re.compile(r"^\s*!!.*|^>.*|^end.*|", re.M)
    regex_sub_command = re.compile(r"^\s.*Command:.*", re.M)
    regex_sub_bang = re.compile(r"(^.\s+)!(.*)", re.M)
    regex_sub_endbang = re.compile(r"(\w)!", re.M)
    regex_sub_boot_system = re.compile(r"^!.*boot\ssystem.*", re.M)
    regex_sub_comments = re.compile(r"(^\s+)#(.*)", re.M)
    regex_sub_rancid = re.compile(r"RANCID-CONTENT-TYPE:\sarista", re.IGNORECASE)


    for path in pathlib.Path(mydir).iterdir():
        if path.is_file():
            current_file = open(path, "r")
            content = current_file.read()
            comments += search_comments(content)
            content = fix_ups(content)
            subcontent = re.sub(regex_sub_doublebang, "", content)
            subcontent = re.sub(regex_sub_rancid, "", subcontent)
            subcontent = re.sub(regex_sub_command, "", subcontent)
            # change any '!' with preceding whitespace to a '#'
            # change any '!' at the end of a word to a '#' 
            # We will change those back at the end
            subcontent = re.sub(regex_sub_bang, r"\1#\2", subcontent)
            subcontent = re.sub(regex_sub_endbang, r"\1#", subcontent)
            subcontent = re.sub(regex_sub_boot_system, "", subcontent)
            if args.mask:
                ignore_mask = args.mask
                regex_sub_mask = re.compile(
                    r"(.*{}).*".format(ignore_mask), re.M | re.IGNORECASE
                )
                subcontent = re.sub(regex_sub_mask, r"\1 MASKED", subcontent)

            stanzas += subcontent.split("!")
            device_stanzas[path] = subcontent.split("!")
            current_file.close()

    # print statements for debugging/testing
    # print(len(stanzas))

    """This loop will print only stanzas
      that were seen 'min_count' or more times
    """
    if int(maxcount) > 1:
        for k, v in sorted(Counter(stanzas).items()):
            #print(f"v is: {v} and k is {k}")
            if v >= int(mincount) and v <= int(num_files):
                # substitute the '  !' back in for the '#'
                # used to trick the split parser earlier
                #print(f"K is: ->{k}<-")
                if k and not str.isspace(k):
                  print(
                      f'\n\n\n\n\n\x1b[6;30;44m ↓ SEEN ->({str(v)}/{num_files})<- TIMES ↓\x1b[0m'
                  )
                  # gah this is hacky stuff to get the "!" in correctly
                  if not re.match("\n#", k):
                    print("!")
                  print(re.sub(regex_sub_comments, r"\1!\2", k).strip())
                  print("!")
                  print(
                      f'\x1b[6;30;44m ↑ SEEN ->({str(v)}/{num_files})<- TIMES ↑\x1b[0m'
                  )
    else:
        for k, v in sorted(Counter(stanzas).items()):
            if v > int(maxcount):
                common_stanzas.append(k)
        for device in device_stanzas:
            _con = []
            for _stanza in device_stanzas[device]:
                specific = True
                for _common in common_stanzas:
                    if _common == _stanza:
                        specific = False
                if specific:
                    _con.append("!")
                    _con.append(_stanza)
            if _con:
                print(
                    f'\n\n\n\n\n\x1b[6;30;44m ↓ Device Specific Config for: {device} ↓\x1b[0m'
                )
                print(re.sub(regex_sub_comments, r"\1!\2", "".join(_con).strip()))
                print(
                    f'!\n\x1b[6;30;44m ↑ Device Specific Config for: {device} ↑\x1b[0m'
                )

    # Coments list for review


    # Coments list for review
    # print(len(comments))
    comments = set(comments)
    print(
        "\n\n##################### COMMENTS  '!!' found in corpus #######################"
    )
    print("\n".join(comments))


if __name__ == "__main__":
    main()
