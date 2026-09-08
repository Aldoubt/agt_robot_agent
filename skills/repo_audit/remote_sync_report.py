"""Local branch synchronization report helper.

Read-only utility to summarize local/remote divergence.
"""


def build_sync_report(repo_status):
    report = []
    for item in repo_status:
        ahead = item.get("ahead", 0)
        behind = item.get("behind", 0)

        if ahead or behind:
            state = "diverged"
            if ahead and not behind:
                state = "local_ahead_not_pushed"
            elif behind and not ahead:
                state = "local_behind"
        else:
            state = "synchronized"

        report.append(
            {
                "path": item.get("path"),
                "ahead": ahead,
                "behind": behind,
                "state": state,
            }
        )

    return report
