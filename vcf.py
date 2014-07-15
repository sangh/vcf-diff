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
import parse_into_vcards
import parse_into_hash

all_commands = {}

def cmd_validate(vcf):
    return parse_into_hash.main(parse_into_vcards.main(open(vcf)), True)
all_commands['validate'] = cmd_validate

def cmd_diff(base_vcf, subset_vcf):
    base = cmd_validate(base_vcf)
    subset = cmd_validate(subset_vcf)
    base_keys = base.keys()
    for subset_key in subset.keys():
        if not subset_key in base_keys:
            print("-  VCF not in base: " + str(subset_key))
            print("---subset---> " + str(subset[subset_key]))
        else:
            bv_keys = base[subset_key].keys()
            sv = subset[subset_key]
            print_cmp = False
            for k in sv.keys():
                if not k in bv_keys:
                    print("-  Field not in base: " + str(subset_key) +
                        " => " + str(k) + ", " + str(sv[k]))
                    print_cmp = True
                else:
                    if base[subset_key][k] != sv[k]:
                        print("-  Diff values: " + str(subset_key) + " => " +
                                str(k) + " (base, subset): (" +
                            str(base[subset_key][k]) + ", " +
                            str(sv[k]) + ").")
                        print_cmp = True
            if print_cmp:
                print("----base----> " + str(base[subset_key]))
                print("---subset---> " + str(subset[subset_key]))
                print("")
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
