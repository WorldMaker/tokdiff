#!/usr/bin/env python
from difflib import SequenceMatcher
from diff_match_patch import diff_match_patch
import argparse
import pygments
import pygments.lexers
import sys

"""
This is a simple diff utility based upon pygments' lexer token streams.
"""

parser = argparse.ArgumentParser(description=__file__.__doc__)
parser.add_argument('lexername', help="Pygments lexer to utilize")
parser.add_argument('file1', type=argparse.FileType('r'))
parser.add_argument('file2', type=argparse.FileType('r'))
parser.add_argument('-o', '--out', type=argparse.FileType('w'),
    default=sys.stdout)
group = parser.add_mutually_exclusive_group()
group.add_argument('-v', '--verbose', action='store_true')
group.add_argument('-u', '--unidiff', action='store_true')
data = parser.parse_args()

lexer = pygments.lexers.get_lexer_by_name(data.lexername)

a = list(pygments.lex(data.file1.read(), lexer))
b = list(pygments.lex(data.file2.read(), lexer))

sm = SequenceMatcher(None, a, b)

if data.verbose or not data.unidiff:
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == 'equal':
            for item in a[a1:a2]:
                data.out.write("  %s: %s\n" % item)
        elif op == 'replace':
            data.out.write("~~~\n")
            for item in a[a1:a2]:
                data.out.write("- %s: %s\n" % item)
            for item in b[b1:b2]:
                data.out.write("+ %s: %s\n" % item)
            data.out.write("~~~\n")
        elif op == 'insert':
            for item in b[b1:b2]:
                data.out.write("+ %s: %s\n" % item)
        elif op == 'delete':
            for item in a[a1:a2]:
                data.out.write("- %s: %s\n" % item)
        else:
            data.out.write("<<%s>>\n" % op)
elif data.unidiff:
    dmp = diff_match_patch()
    diffs = []
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op == 'equal':
            diffs.append((dmp.DIFF_EQUAL, 
                ''.join(val for type, val in a[a1:a2])))
        elif op == 'replace':
            for line in ''.join(val for type, val in b[a1:a2]).splitlines(True):
                diffs.append((dmp.DIFF_DELETE, line))
            for line in ''.join(val for type, val in b[b1:b2]).splitlines(True):
                diffs.append((dmp.DIFF_INSERT, line))
        elif op == 'insert':
            for line in ''.join(val for type, val in b[b1:b2]).splitlines(True):
                diffs.append((dmp.DIFF_INSERT, line))
        elif op == 'delete':
            for line in ''.join(val for type, val in b[a1:a2]).splitlines(True):
                diffs.append((dmp.DIFF_DELETE, line))
    patches = dmp.patch_make(diffs)
    data.out.write(dmp.patch_toText(patches))

# vim: ai et ts=4 sts=4 sw=4
