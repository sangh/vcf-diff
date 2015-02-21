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
        key = [key_parts[0], None, None]
        for k in key_parts[1:]:
            if '=' in k:
                if 'CHARSET=UTF-8' == k:
                    if key[1]:
                        raise Exception('Mult charsets: ' + str(vc))
                    else:
                        key[1] = 'UTF-8'
                elif 'ENCODING=QUOTED-PRINTABLE' == k:
                    if key[2]:
                        raise Exception('Mult encodings: ' + str(vc))
                    else:
                        key[2] = 'QUOTED-PRINTABLE'
                elif 'ENCODING=BASE64' == k:
                    if key[2]:
                        raise Exception('Mult encodings: ' + str(vc))
                    else:
                        key[2] = 'BASE64'
                else:
                    raise Exception('Unknown modifier: ' + str(vc))
            else:
                key[0] = key[0] + ';' + k
        if not key[1]:
            key[1] = 'ASCII'
        if not key[2]:
            key[2] = 'TEXT'
        for k in ret.keys():
            if key[0] == k[0]:
                raise Exception('Mult keys: ' + str(key) + ' from: ' + str(vc))

        ret[tuple(key)] = elem[1]
    return ret

def main(stdin, useDirectly = False):
    """Read, and eval stdin, evil, I know, shut up."""
    if useDirectly:
        inp = stdin
    else:
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

    for k,v in ret.items():
        nnfields = 0
        for i in v:
            if i[0] == 'N':
                nnfields = nnfields + 1
                if v[i] != ";%s;;;" % (k):
                    raise Exception('N key does not match FN: ' + str(v))
                continue
            if i[0] in ('FN', 'NOTE', 'PHOTO;JPEG', 'URL', ):
                continue
            if i[0][0:5] == 'EMAIL':
                if i[0][5:] in (';HOME', ';WORK', ):
                    continue
                raise Exception("Email isn't home|work: " + str(v))
            if i[0][0:4] in ('ADR;', 'ADR', 'TEL;', ):
                if 'PREF' in i[0]:
                    raise Exception('Nothing can be preferred: ' + str(v))
                continue
            raise Exception('Unknown key base: ' + str(i) + ' in: ' + str(v))
        if nnfields != 1:
            raise Exception('Multiple or no N filed(s): ' + str(v))
    return ret

if __name__ == "__main__":
    ret = main(sys.stdin)
    sys.exit(0)
