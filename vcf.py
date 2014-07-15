#!/usr/bin/python

help = """The first argument must be a supported command (or enough of the
begining to unambigously match one.

Current commands:

    validate <file1.vcf>
        Completely parses and validates the file to my silly rules that are
        much stricter in specific ways than VCF in general.

    diff <base.vcf> <subset.vcf>
        Look for anything in <subset.vcf> that does not appear in <base.vcf>,
        BUT NOT THE OTHER WAY AROUND.  If an FN is missing from base, just
        print it, if elements are missing or different, print those.
        Both files must completely validate.

Reads all files from the given location involes the sub programs, and prints
the results.
"""

import sys
import 

all_commands = {}

def cmd_validate(stream):
    print("stream: " + str(stream))
all_commands['validate'] = cmd_validate

def cmd_diff(base, subset):
    print("base: " + str(base) + " subs: " + str(subset))
all_commands['diff'] = cmd_diff


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception('No command given.')
    cmd = sys.argv[1]
    cmdf = None
    for c in all_commands.keys():
        if c.startswith(cmd):
            if cmdf:
                raise Exception('Ambiguous command.')
            else:
                cmdf = all_commands[c]
    if not cmdf:
        raise Exception('Command not found: ' + str(cmd))

    cmdf(*sys.argv[2:])
