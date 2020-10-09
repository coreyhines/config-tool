#!/usr/bin/env python3

import pathlib
import collections

from os.path import expanduser
home = expanduser("~")

mydir = home + "/vs-code/config-tool/configs/"


def get_dupes(L):
    seen = set()
    seen2 = set()
    seen_add = seen.add
    seen2_add = seen2.add
    for item in L:
        if item in seen:
          seen2_add(item)
        else:
          seen_add(item)
    return list(seen2)


stanzas = []
comments = []
for path in pathlib.Path(mydir).iterdir():
    if path.is_file():
        current_file = open(path, "r")
        content = current_file.read()
        comments += content.split('!!')
        stanzas += content.split('!')
        current_file.close()

print(len(stanzas))
print(len(comments))
dupes = get_dupes(stanzas)
#print(len(dupes))
#print("\n".join(dupes))
print("##################### COMMENTS #######################")
print("\n".join(comments))
