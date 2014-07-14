#!/usr/bin/python

help = """Read from stdin, write to stdout.

Reads a stream that should be a list of lists (it checks because using eval
sucks, but I'm lazy and don't want to do it the right way).
Each one should start and end with VCARD, be a supported version, and be
ASCII strings, all.  Anything else throws an exception.

Then does the sanity checking I want, like only the first name is used (b/c
I hate how things chango how what is displayed.  And nothing unexpected is
present (b/c I should upgrade this to do something with it, if I want).

The whole thing must fit in memory.

Write out a hash, normalised format, that can itself be evaled.
"""

import sys
def main(stdin):
    """Read, and eval stdin, evil, I know, shut up."""
    inp = stdin.readlines()
    if 1 != len(inp):
        raise Exception('Not exactly one line of input.')
    inp = inp[0]
    if '[' != inp[0] or ']' != inp[-1]:
        raise Exception('Not a list.')
    if '[' != inp[1] or ']' != inp[-2]:
        raise Exception('Not a list of lists.')
    inp = eval(inp)
    for v in inp:
        if type v == 'list':
            raise Exception('Something is not a list.')

        #line = line.encode('ascii').strip()
            #if line == 'END:VCARD':
            #if line != 'BEGIN:VCARD':
    ret = {}
    return ret

if __name__ == "__main__":
    try:
        ret = main(sys.stdin)
    except Exception as e:
        print >> sys.stderr, str(e)
        sys.exit(1)
    print >> sys.stdout, str(ret)
    sys.exit(0)
