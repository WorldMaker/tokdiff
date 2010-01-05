#!/usr/bin/env python
# Copyright 2010 Max Battcher <me@worldmaker.net>. Licensed under the MS-PL.
from diff_match_patch import diff_match_patch
import argparse
import sys

"""
This is a simple patch utility based upon diff-match-patch.
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Applies patches created by diff-match-patch and/or tokdiff.")
    parser.add_argument('input', type=argparse.FileType('r'))
    parser.add_argument('-p', '--patch', type=argparse.FileType('r'),
        default=sys.stdin)
    parser.add_argument('-o', '--out', type=argparse.FileType('w'),
        default=sys.stdout)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u', '--unidiff', action='store_true',
        help='Char-based unidiff-like patch (default)')
    group.add_argument('-d', '--delta', action='store_true',
        help='Simplified intermediate delta (unstable)')
    data = parser.parse_args()

    dmp = diff_match_patch()

    data.unidiff = not data.delta

    if data.unidiff:
        patches = dmp.patch_fromText(data.patch.read())
        result, successes = dmp.patch_apply(patches, data.input.read())
        data.out.write(result)
        if not all(successes):
            sys.stderr.write('WARNING: One or more patches were not applied.')
    elif data.delta:
        inp = data.input.read()
        diffs = dmp.diff_fromDelta(inp, data.patch.read())
        patches = dmp.patch_make(diffs)
        result, successes = dmp.patch_apply(patches, inp)
        data.out.write(result)
        if not all(successes):
            sys.stderr.write('WARNING: One or more patches were not applied.')

# vim: ai et ts=4 sts=4 sw=4
