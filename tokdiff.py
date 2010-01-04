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
data = parser.parse_args()

lexer = pygments.lexers.get_lexer_by_name(data.lexername)

a = list(pygments.lex(data.file1.read(), lexer))
b = list(pygments.lex(data.file2.read(), lexer))

sm = SequenceMatcher(None, a, b)

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

# vim: ai et ts=4 sts=4 sw=4
