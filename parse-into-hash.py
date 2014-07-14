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
    inp = eval(inp[0])
    if not isinstance(inp, list):
        raise Exception('Not a list.')
    for v in inp:
        if not isinstance(v, list):
            raise Exception('Not a list of lists: ' + str(v))
        for s in v:
            if not isinstance(s, str):
                raise Exception('Not a list of lists of strings: ' + str(s))
            if s != s.encode('ascii', 'ignore').strip():
                raise Exception('Not a list of lists of ASCII strings: ' + s)
    # Now we can check the values themselves.
    for vc in inp:
        if 3 >= len(vc):
            raise Exception('Invalid or empty: ' + str(vc))
        else:
            if 'BEGIN:VCARD' != vc[0] or 'END:VCARD' != vc[-1]:
                raise Exception('Bad begin or end: ' + str(vc))
            if 'VERSION:' != vc[1][0:8]:
                raise Exception('Version error: ' + str(vc))
            if vc[1][8:] not in ('2.1', ):
                raise Exception('Unsupported version: ' + str(vc))
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
