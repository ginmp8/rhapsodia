#!/usr/bin/env python3
"""Compatibility CLI for optional analytics, using logical graph identity."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from graph_analysis import analyze


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',required=True)
    parser.add_argument('--community',choices=['greedy-modularity','none'],default='greedy-modularity')
    parser.add_argument('--pagerank',action='store_true')
    args=parser.parse_args(argv)
    try:
        runs=[]
        if args.community!='none':runs.append(analyze(Path(args.db),'communities','networkx'))
        if args.pagerank:runs.append(analyze(Path(args.db),'pagerank','stdlib'))
        print(json.dumps({'status':'pass','runs':runs},sort_keys=True,indent=2))
        return 0
    except (ValueError,RuntimeError,ImportError,OSError) as exc:
        print(json.dumps({'status':'fail','error':str(exc)},sort_keys=True))
        return 1


if __name__=='__main__':sys.exit(main())
