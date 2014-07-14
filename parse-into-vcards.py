#!/usr/bin/python

help = """Read from stdin, write to stdout.

Reads a file that should be a vcf and does nothing apart from split into
a list of lists where each list contains the lines from a single vcard.
Means the input much start with a line that is 'BEGIN:VCARD' and end with a
line that is 'END:VCARD', no inter-leving and no extra lines at all (even a
blank line will error out).

The whole thing must fit in memory.

Write out a list of lists (which can be `eval`~ed in python).
"""

import sys
def main(stdin):
    """Read, line by line from stdin, return a list of lists or throw exp."""
    ret = []
    nlines = 0
    incard = False
    for line in stdin:
        nlines = nlines + 1
        # Will raise a Unicode... exception
        line = line.encode('ascii').strip()
        if incard:
            ret[-1].append(line)
            if line == 'END:VCARD':
                incard = False
        else:  # This line must match.
            if line != 'BEGIN:VCARD':
                raise Exception(
                    'Not start of VCARD (line ' + str(nlines) + '): ' + line)
            ret.append([line, ])
            incard = True
    # Done.
    return ret

if __name__ == "__main__":
    try:
        ret = main(sys.stdin)
    except Exception as e:
        print >> sys.stderr, str(e)
        sys.exit(1)
    print >> sys.stdout, str(ret)
    sys.exit(0)
