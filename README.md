# config-tool
An attempt to recover EOS configuration stanzas that are common amongst a corpus of configs. This output can be used to develop CloudVision Portal configlets, that can be applied at the container level.
usage: 
  `./config-tool --directory /path/to/configs --mask description --count all`

  `--directory some/dir/or/path`, specifies the directory where the EOS configuration files are stored

  `--mask string` is an optional string that will be removed, and ignored as part of the comparison. This is useful for example when the only element that differs between two or more configs is due to the description

  `--count #|all` this option "raises" or "lowers" the bar of what a "common match" means. Higher number here will mean that the stanza must appear at least the number of times specified in "--count". "--count all" means the stanza must appear in all config files to be counted as a common match.
