#!/usr/bin/env python3
"""Run ssot check and classify drift as env_drift vs repo_drift."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub('', text)


def classify_output(output: str, exit_code: int) -> dict[str, object]:
    clean = strip_ansi(output)
    new_count = len(re.findall(r'\bNEW\b', clean))
    mod_count = len(re.findall(r'\bMOD\b', clean))
    del_count = len(re.findall(r'\bDEL\b', clean))

    if exit_code == 0:
        return {
            'classification': 'pass',
            'status': '✅ PASS',
            'exit_code': 0,
            'new': new_count,
            'mod': mod_count,
            'del': del_count,
            'confidence': 0.99,
            'hint': 'No SSOT drift detected.',
        }

    if new_count > 0 and (mod_count > 0 or del_count > 0):
        return {
            'classification': 'mixed_drift',
            'status': '❌ MIXED_DRIFT',
            'exit_code': 6,
            'new': new_count,
            'mod': mod_count,
            'del': del_count,
            'confidence': 0.95,
            'hint': 'Mixed NEW+MOD/DEL drift detected. Treat as repo drift (high risk) until reconciled.',
        }

    if mod_count > 0 or del_count > 0:
        return {
            'classification': 'repo_drift',
            'status': '❌ REPO_DRIFT',
            'exit_code': 6,
            'new': new_count,
            'mod': mod_count,
            'del': del_count,
            'confidence': 0.92,
            'hint': 'Repository drift detected (MOD/DEL). Investigate and reconcile SSOT changes.',
        }

    if new_count > 0:
        return {
            'classification': 'env_drift',
            'status': '⚠️ ENV_DRIFT',
            'exit_code': 0,
            'new': new_count,
            'mod': mod_count,
            'del': del_count,
            'confidence': 0.88,
            'hint': 'Likely home environment drift (~/.egos not synced). Run governance sync in environment.',
        }

    return {
        'classification': 'unknown_fail',
        'status': '❌ UNKNOWN_FAIL',
        'exit_code': 7,
        'new': new_count,
        'mod': mod_count,
        'del': del_count,
        'confidence': 0.40,
        'hint': 'SSOT check failed without recognizable drift markers. Inspect raw output.',
    }


def recommended_actions(classification: str) -> list[dict[str, str]]:
    if classification == 'env_drift':
        return [
            {
                'priority': 'P1',
                'owner': 'infra',
                'action': 'Sync local governance home before rerunning SSOT check.',
                'command': 'bun run governance:sync:local && bun run ssot:check',
            },
            {
                'priority': 'P2',
                'owner': 'qa',
                'action': 'If environment is ephemeral, keep as warning and rely on repo-local checks.',
                'command': 'bun run ssot:diagnostic',
            },
        ]
    if classification == 'repo_drift':
        return [
            {
                'priority': 'P0',
                'owner': 'repo-owner',
                'action': 'Reconcile modified/deleted canonical SSOT files before merge.',
                'command': 'git diff --name-only && bun run governance:check && bun run ssot:check',
            },
        ]
    if classification == 'unknown_fail':
        return [
            {
                'priority': 'P0',
                'owner': 'qa',
                'action': 'Investigate parser/runner issue and escalate with logs if recurring.',
                'command': 'bun run ssot:diagnostic',
            },
        ]
    if classification == 'mixed_drift':
        return [
            {
                'priority': 'P0',
                'owner': 'repo-owner',
                'action': 'Mixed drift means canonical conflict risk. Resolve MOD/DEL first, then NEW entries.',
                'command': 'git diff --name-status && bun run governance:check && bun run ssot:check',
            },
        ]
    return [
        {
            'priority': 'P3',
            'owner': 'none',
            'action': 'No action required.',
            'command': 'true',
        },
    ]


def build_report(command: str, result: dict[str, object], output: str) -> str:
    lines = [
        '# SSOT Check Diagnostic',
        '',
        f"- command: `{command}`",
        f"- classification: **{result['classification']}**",
        f"- status: {result['status']}",
        f"- confidence: **{float(result['confidence']):.2f}**",
        f"- counters: NEW={result['new']} MOD={result['mod']} DEL={result['del']}",
        f"- hint: {result['hint']}",
        '',
        '## Ação recomendada',
        *[f"- [{item['priority']}] ({item['owner']}) {item['action']}" for item in recommended_actions(str(result['classification']))],
        *[f"  - comando: `{item['command']}`" for item in recommended_actions(str(result['classification']))],
        '',
        '## Raw excerpt',
        '```text',
        '\n'.join(strip_ansi(output).splitlines()[:80]),
        '```',
        '',
    ]
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Classify ssot:check failures')
    parser.add_argument('--command', default='sh scripts/governance-sync.sh --check', help='Command to execute')
    parser.add_argument('--output', default='', help='Optional markdown output')
    args = parser.parse_args()

    proc = subprocess.run(args.command, shell=True, capture_output=True, text=True)
    combined = (proc.stdout or '') + (proc.stderr or '')
    result = classify_output(combined, proc.returncode)
    report = build_report(args.command, result, combined)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report)
    else:
        print(report)

    print(f"SSOT_DIAGNOSTIC: {result['classification']}")
    return int(result['exit_code'])


if __name__ == '__main__':
    raise SystemExit(main())
