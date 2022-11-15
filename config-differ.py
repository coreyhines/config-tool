#!/usr/bin/env python3

# Copyright (c) 2022, Arista Networks, Inc.
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
# config-differ.py
#
#    Written by:
#       Corey Hines, Arista Networks
#
"""DESCRIPTION
Outputs either the differences, 
or the common stanzas between two configs
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
    """fix any issues with the stanzas
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
        "-t",
        "--type",
        type=str,
        default="diffs",
        choices=[
            "common",
            "diffs",
        ],
        help="specify config output type",
        required=True,
    )
    parser.add_argument(
        "-f",
        "--files",
        type=str,
        nargs="+",
        default="",
        help="directory that contains EOS configuration files",
        required=True,
    )
    args = parser.parse_args()

    stanzas = []
    device_stanzas = {}
    common_stanzas = []
    comments = []

    home = expanduser("~")
    if args.files:
        myfiles = args.files
    else:
        print(f"This didn't work: arg.files is: {arg.files}")

    # num_files = str(
    #     len(
    #         [
    #             name
    #             for name in os.listdir(mydir)
    #             if os.path.isfile(mydir + "/" + name)
    #         ]
    #     )
    # )

    if args.type == "common":
        type = "common"
        mincount = 2
        maxcount = 2
    elif args.type == "diffs":
        maxcount = 1
        type = "diffs"

    # Series of regex statements to remove extraneous unusable config patterns
    regex_sub_doublebang = re.compile(r"^\s*!!.*|^>.*|^end.*|", re.M)
    regex_sub_command = re.compile(r"^\s.*Command:.*", re.M)
    regex_sub_bang = re.compile(r"(^.\s+)!(.*)", re.M)
    regex_sub_endbang = re.compile(r"(\w)!", re.M)
    regex_sub_boot_system = re.compile(r"^!.*boot\ssystem.*", re.M)
    regex_sub_comments = re.compile(r"(^\s+)#(.*)", re.M)
    regex_sub_rancid = re.compile(
        r"RANCID-CONTENT-TYPE:\sarista", re.IGNORECASE
    )

    for file in myfiles:
        if os.path.exists(file):
            current_file = open(file, "r")
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

            stanzas += subcontent.split("!")
            device_stanzas[file] = subcontent.split("!")
            current_file.close()
        else:
            print(f"File '{file}' does not exist, check path")

    # print statements for debugging/testing
    # print(len(stanzas))

    """This loop will print only stanzas
      that were seen 'min_count' or more times
    """
    if type == "common":
        for k, v in sorted(Counter(stanzas).items()):
            if v >= int(mincount) and v <= int(maxcount):
                # substitute the '  !' back in for the '#'
                # used to trick the split parser earlier
                if k and not str.isspace(k):
                    print(re.sub(regex_sub_comments, r"\1!\2", k).strip())
                    print("!")
    elif type == "diffs":
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
                    # _con.append("!")
                    _con.append(_stanza)
            if _con:
                for item in _con:
                    lines = []
                    lines += item.split("\n")
                for _k, _v in sorted(Counter(lines).items()):
                    print(f"_k,_v is: {_k} , {_v}")
                    if _v == 1:
                        print(f"output is: {_k}")
                        # print(
                        #     re.sub(
                        #         regex_sub_comments,
                        #         r"\1!\2",
                        #         "".join(_k).strip(),
                        #     )
                        # )

    # Coments list for review

    # Coments list for review
    # print(len(comments))
    # comments = set(comments)
    # print(
    #     "\n\n##################### COMMENTS  '!!' found in corpus #######################"
    # )
    # print("\n".join(comments))


if __name__ == "__main__":
    main()
