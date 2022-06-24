[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/coreyhines/config-tool)

# config-tool

An attempt to recover EOS configuration stanzas that are common amongst a corpus of configs. This output can be used to develop CloudVision Portal configlets, that can be applied at the container level.

## usage:

`./config-tool.py --directory /path/to/configs --mask description --count all`

`--directory /path/to/configs`, specifies the directory where the EOS configuration files are stored

`--mask string` is an optional string that will be removed, and ignored as part of the comparison. This is useful for example when the only element that differs between two or more configs is due to the description

`--count #|all` this option "raises" or "lowers" the bar of what a "common match" means. Higher number here will mean that the stanza must appear at least the number of times specified in `--count`. `--count all` means the stanza must appear in all config files to be counted as a common match.

# confgrabber

An eapi script built with JSON/RPC to pull running-config files from Arista EOS devices. The script relies on a file called switches as an input list. It outputs the running-config to a specified directory. Valid credentials are required.

## usage

`./confgrabber.py --user someuser --passwd 'secret' --file switches --directory ./configs/`

`--user string`, a valid user on the EOS devices

`--passwd string`, a valid password for the user on the EOS devices

`--file string`, specifies the input list of switches

`--directory string`, specifies the directory where the EOS configuration will be written to and stored
