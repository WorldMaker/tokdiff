#!/usr/bin/env python
# Copyright 2009 Max Battcher <me@worldmaker.net>. Licensed under the MS-PL.
from difflib import SequenceMatcher
from diff_match_patch import diff_match_patch
import argparse
import pygments
import pygments.lexers
import sys

"""
This is a simple diff utility based upon pygments' lexer token streams.
"""

def dmp_diffs(lexer, dmp, a, b):
    diffs = []
    lexa = list(pygments.lex(a, lexer))
    lexb = list(pygments.lex(b, lexer))
    sm = SequenceMatcher(None, lexa, lexb)
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == 'equal':
            diffs.append((dmp.DIFF_EQUAL, 
                ''.join(val for type, val in lexa[a1:a2])))
        elif op == 'replace':
            for line in ''.join(val for type, val
            in lexa[a1:a2]).splitlines(True):
                diffs.append((dmp.DIFF_DELETE, line))
            for line in ''.join(val for type, val
            in lexb[b1:b2]).splitlines(True):
                diffs.append((dmp.DIFF_INSERT, line))
        elif op == 'insert':
            for line in ''.join(val for type, val
            in lexb[b1:b2]).splitlines(True):
                diffs.append((dmp.DIFF_INSERT, line))
        elif op == 'delete':
            for line in ''.join(val for type, val
            in lexb[a1:a2]).splitlines(True):
                diffs.append((dmp.DIFF_DELETE, line))
    return diffs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates tokenized diffs using Pygments")
    parser.add_argument('lexername', help="Pygments lexer to utilize")
    parser.add_argument('file1', type=argparse.FileType('r'))
    parser.add_argument('file2', type=argparse.FileType('r'))
    parser.add_argument('-o', '--out', type=argparse.FileType('w'),
        default=sys.stdout)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', '--verbose', action='store_true',
        help='Verbose tokenization diff')
    group.add_argument('-u', '--unidiff', action='store_true',
        help='Unidiff-like character-based diff (default)')
    group.add_argument('-d', '--delta', action='store_true',
        help='Simplified intermediate delta (unstable)')
    group.add_argument('-c', '--compare', action='store_true',
        help='HTML comparison of tokenized diff to char diffs')
    data = parser.parse_args()

    lexer = pygments.lexers.get_lexer_by_name(data.lexername)

    a = data.file1.read()
    b = data.file2.read()

    data.unidiff = not data.verbose and not data.delta and not data.compare

    if data.verbose:
        lexa = list(pygments.lex(a, lexer))
        lexb = list(pygments.lex(b, lexer))
        sm = SequenceMatcher(None, lexa, lexb)
        for op, a1, a2, b1, b2 in sm.get_opcodes():
            if op == 'equal':
                for item in lexa[a1:a2]:
                    data.out.write("  %s: %s\n" % item)
            elif op == 'replace':
                data.out.write("~~~\n")
                for item in lexa[a1:a2]:
                    data.out.write("- %s: %s\n" % item)
                for item in lexb[b1:b2]:
                    data.out.write("+ %s: %s\n" % item)
                data.out.write("~~~\n")
            elif op == 'insert':
                for item in lexb[b1:b2]:
                    data.out.write("+ %s: %s\n" % item)
            elif op == 'delete':
                for item in lexa[a1:a2]:
                    data.out.write("- %s: %s\n" % item)
            else:
                data.out.write("<<%s>>\n" % op)
    else:
        dmp = diff_match_patch()
        diffs = dmp_diffs(lexer, dmp, a, b)

        if data.unidiff:
            patches = dmp.patch_make(diffs)
            data.out.write(dmp.patch_toText(patches))
        elif data.delta:
            data.out.write(dmp.diff_toDelta(diffs))
        elif data.compare:
            import timeit
            data.out.write("<h1>Token diff</h1><code><pre>")
            data.out.write(dmp.diff_prettyHtml(diffs))
            data.out.write("</pre></code>")
            t = timeit.Timer("dmp_diffs(lexer, dmp, a, b)", "from diff_match_patch import diff_match_patch; from __main__ import dmp_diffs; import pygments; dmp = diff_match_patch(); a = open('%s', 'r').read(); b = open('%s', 'r').read(); lexer = pygments.lexers.get_lexer_by_name('%s')" % (data.file1.name, data.file2.name, data.lexername))
            data.out.write("<p>Average computation time: %.2f usecs</p>" % (
                10 * t.timeit(number=10)/10))

            data.out.write("<h1>Character diff</h1><code><pre>")
            dmpdiffs = dmp.diff_main(a, b)
            data.out.write(dmp.diff_prettyHtml(dmpdiffs))
            data.out.write("</pre></code>")
            t = timeit.Timer("dmp.diff_main(a, b)", "from diff_match_patch import diff_match_patch; dmp = diff_match_patch(); a = open('%s', 'r').read(); b = open('%s', 'r').read()" % (data.file1.name, data.file2.name))
            data.out.write("<p>Average computation time: %.2f usecs</p>" % (
                10 * t.timeit(number=10)/10))

# vim: ai et ts=4 sts=4 sw=4
