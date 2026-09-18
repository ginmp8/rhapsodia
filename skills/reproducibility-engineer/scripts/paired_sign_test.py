#!/usr/bin/env python3
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import json
import math
from pathlib import Path


def p_upper_tail(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    return sum(math.comb(n, k) for k in range(wins, n + 1)) / (2 ** n)


def main() -> int:
    ap = argparse.ArgumentParser(description='Exact one-sided paired sign test for candidate wins vs baseline wins.')
    ap.add_argument('results', help='JSON list or {"pairs": [...]} with outcome candidate|baseline|tie')
    ap.add_argument('--alpha', type=float, default=0.05)
    ap.add_argument('--min-pairs', type=int, default=12)
    ap.add_argument('--json', dest='json_out')
    args = ap.parse_args()

    data = json.loads(Path(args.results).read_text(encoding='utf-8'))
    pairs = data.get('pairs', []) if isinstance(data, dict) else data
    if not isinstance(pairs, list):
        raise SystemExit('results must be a list or an object with pairs list')
    counts = {'candidate':0,'baseline':0,'tie':0}
    invalid = []
    for i, row in enumerate(pairs):
        outcome = row.get('outcome') if isinstance(row, dict) else None
        if outcome not in counts:
            invalid.append(i)
        else:
            counts[outcome] += 1
    if invalid:
        report = {'status':'fail','error':f'invalid outcome rows: {invalid}'}
        text = json.dumps(report, indent=2) + '\n'
        if args.json_out: Path(args.json_out).write_text(text, encoding='utf-8')
        else: print(text, end='')
        return 1

    effective = counts['candidate'] + counts['baseline']
    p = p_upper_tail(counts['candidate'], counts['baseline'])
    powered = effective >= args.min_pairs
    significant = powered and counts['candidate'] > counts['baseline'] and p <= args.alpha
    report = {
        'status':'pass',
        'wins_candidate':counts['candidate'],
        'wins_baseline':counts['baseline'],
        'ties':counts['tie'],
        'effective_pairs':effective,
        'min_pairs':args.min_pairs,
        'underpowered':not powered,
        'p_one_sided':p,
        'alpha':args.alpha,
        'candidate_improvement_supported':significant,
        'note':'This test evaluates paired win/loss direction only; it does not validate grader quality or scenario representativeness.'
    }
    text = json.dumps(report, indent=2) + '\n'
    if args.json_out:
        out = Path(args.json_out); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(text, encoding='utf-8')
    else:
        print(text, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
