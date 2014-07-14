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

def _parse_one_vc(vc):
    """Takes in a list that represents a single card, returns a hash, or
    throws an exception."""
    if len(vc) < 4:
        raise Exception('Invalid or empty: ' + str(vc))
    else:
        if 'BEGIN:VCARD' != vc[0] or 'END:VCARD' != vc[-1]:
            raise Exception('Bad begin or end: ' + str(vc))
        if 'VERSION:' != vc[1][0:8]:
            raise Exception('Version error: ' + str(vc))
        if not vc[1][8:] in ('2.1', ):
            raise Exception('Unsupported version: ' + str(vc))
    # We go through, if there is a ':' we take it as a [k,v], and if not then
    # it is joined to the line above.
    elements = []
    for elem in vc[2:-1]:
        splits = elem.split(':')
        if len(splits) < 2:
            if len(elements) < 1:
                raise Exception('Invalid first line: ' + str(vc))
            elements[-1][1] = elements[-1][1] + elem
        else:
            elements.append([splits[0], ':'.join(splits[1:])])
    if len(elements) < 1:
        raise Exception('Invalid vc: ' + str(vc))
    ret = {}
    for elem in elements:
        if len(elem) != 2:
            raise Exception('Bad parse: ' + str(elem) + ' from: ' + str(vc))
        key_parts = elem[0].split(';')
        for k in ret.keys():
            if key_parts[0] == k[0] and key_parts[1] == k[1]:
                raise Exception('Mult keys: ' + str(elem) + ' from: ' + str(vc))
        key = [key_parts[0], None, None, None]
        for k in key_parts[1:]:
            if '=' in k:
                CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE
                if 'CHARSET=UTF-8' == k:
                    if key[2]:
                        raise Exception('Mult charsets: ' + str(vc))
                    else:
                        key[2] = 'UTF-8'
                elif 'ENCODING=QUOTED-PRINTABLE' == k:
                    if key[3]:
                        raise Exception('Mult encodings: ' + str(vc))
                    else:
                        key[3] = 'QUOTED-PRINTABLE'
                elif 'ENCODING=BASE64' == k:
                    if key[3]:
                        raise Exception('Mult encodings: ' + str(vc))
                    else:
                        key[3] = 'BASE64'
                else:
                    raise Exception('Unknown modifier: ' + str(vc))
            else:
                if key[1]:
                    raise Exception('Mult sub-categories: ' + str(vc))
                else:
                    key[1] = k
        if not key[1]:
            key[1] = ''
        if not key[2]:
            key[2] = 'ASCII'
        if not key[3]:
            key[3] = 'TEXT'

        ret[tuple(key)] = elem[1]
    return ret

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
    # Build the hashes, keyed off of 'FN'.
    ret = {}
    for vc in inp:
        # This can throw things.
        vc_h = _parse_one_vc(vc)
        # Check for:
        #if not key_parts[0] in ('ADR', 'EMAIL', 'FN', 'N', 'NOTE', 'PHOTO', 'TEL', 'URL', ):
            #raise Exception('Unknown key: ' + str(key_parts[0]) + ' from: ' + str(vc))
        fnkey = None
        nfns = 0
        for k,v in vc_h.items():
            if 'FN' == k[0]:
                nfns = nfns + 1
                fnkey = v
        if 0 == nfns:
            raise Exception('No FN: ' + str(vc) + ' parsed: ' + str(vc_h))
        if nfns > 1:
            raise Exception('Mult FN: ' + str(vc) + ' parsed: ' + str(vc_h))
        if fnkey in ret:
            raise Exception('Mult FN keys ' + str(fnkey) + ': ' + str(vc))
        ret[fnkey] = vc_h

    return ret

if __name__ == "__main__":
    try:
        ret = main(sys.stdin)
    except Exception as e:
        print >> sys.stderr, str(e)
        sys.exit(1)
    print >> sys.stdout, str(ret)
    sys.exit(0)
