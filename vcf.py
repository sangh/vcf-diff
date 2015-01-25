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
    def compress_large_values(vcf):
        """If any value field is large replace with its MD5."""
        import hashlib
        for ent in vcf.keys():
            for k in vcf[ent].keys():
                if 200 < len(vcf[ent][k]):
                    hmd = hashlib.md5()
                    hmd.update(vcf[ent][k])
                    vcf[ent][k] = "MD5: " + hmd.hexdigest()
        return vcf
    def rm_hyphen_from_tel(vcf):
        """We don't want the hyphen when comparing phone numbers."""
        for ent in vcf.keys():
            for k in vcf[ent].keys():
                if k[0].startswith('TEL'):
                    vcf[ent][k] = vcf[ent][k].replace('-', '')
        return vcf
    base = rm_hyphen_from_tel(compress_large_values(cmd_validate(base_vcf)))
    subset = rm_hyphen_from_tel(compress_large_values(cmd_validate(subset_vcf)))
    base_keys = base.keys()
    for subset_key in subset.keys():
        if not subset_key in base_keys:
            print("-  VCF not in base: " + str(subset_key))
            print("---subset---> " + sprint_card(subset[subset_key]))
            print("")
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
                        if ('PHOTO;JPEG', 'ASCII', 'BASE64') != k:
                            print("-  Diff values: " + str(subset_key) +
                                " => " + str(k) + " (base, subset): (" +
                                str(base[subset_key][k]) + ", " +
                                str(sv[k]) + ").")
                            print_cmp = True
            if print_cmp:
                print("----base----> " + sprint_card(base[subset_key]))
                print("---subset---> " + sprint_card(subset[subset_key]))
                print("")
all_commands['diff'] = cmd_diff

def sprint_card(vc_h):
    """Return a vcard hash in a better format as a string."""
    def get_parts(vc_h, f):
        filtered_parts = [i for i in filter(f, vc_h)]
        if len(filtered_parts) == 0:
            ret = ""
        elif len(filtered_parts) == 1:
            ret = "%s: %s" % (filtered_parts[0], vc_h[filtered_parts[0]])
        else:
            ret = []
            for k in sorted(filtered_parts, key=lambda i: i[0]):
                ret.append("%s: %s" % (k, vc_h[k]))
            ret = "  ".join(ret)
        return ret

    try:
        ret = "\n" + get_parts(vc_h, lambda i: i[0][0:3] == 'TEL') + "\n"
        ret = ret + get_parts(vc_h, 
                lambda i: not i[0] in ('FN', 'N', ) and i[0][0:3] != 'TEL')
        return ret.strip()
    except:
        return str(vc_h).strip()


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
