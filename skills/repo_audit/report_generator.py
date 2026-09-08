"""Generate human readable audit reports from workspace inventory."""

from pathlib import Path
import json


def generate_markdown_report(inventory: dict, output_dir: str):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    with open(output / 'repositories.json', 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    lines = [
        '# Repository Audit Report',
        '',
        f"Workspace: {inventory.get('workspace', '')}",
        '',
        '## Repositories',
        ''
    ]

    for repo in inventory.get('repositories', []):
        lines.extend([
            f"### {Path(repo['path']).name}",
            f"- Path: {repo['path']}",
            f"- Remote: {repo.get('remote', '')}",
            f"- Branch: {repo.get('branch', '')}",
            f"- Commit: {repo.get('commit', '')}",
            f"- Status: {repo.get('status', '')}",
            ''
        ])

    (output / 'repositories.md').write_text('\n'.join(lines), encoding='utf-8')
