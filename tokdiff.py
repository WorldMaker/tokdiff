#!/usr/bin/env python
from difflib import SequenceMatcher
import pygments
import sys

"""
This is a simple diff utility based upon pygments' lexer token streams.
"""

if len(sys.argv) != 4:
    print "Usage: tokdiff.py lexername file1 file2"
    sys.exit(1)

tool, lexname, f1, f2 = sys.argv

lexer = pygments.get_lexer_by_name(lexname)

a = pygments.lex(file(f1).read(), lexer)
b = pygments.lex(file(f2).read(), lexer)

sm = SequenceMatcher(None, a, b)

for op, a1, a2, b1, b2 in sm.get_opcodes():
    if op == 'equal':
        for item in a[a1:a2]:
            print "  %s" % item
    elif op == 'replace':
        print "~~~"
        for item in a[a1:a2]:
            print "- %s" % item
        for item in b[b1:b2]:
            print "+ %s" % item
        print "~~~"
    elif op == 'insert':
        for item in b[b1:b2]:
            print "+ %s" % item
    elif op == 'delete':
        for item in a[a1:a2]:
            print "- %s" % item
    else:
        print "<<%s>>" % op

# vim: ai et ts=4 sts=4 sw=4
