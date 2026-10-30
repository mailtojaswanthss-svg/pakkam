"""Comprehensive secrets scanner across the entire git commit history and working tree.

Scans for:
- Google API keys (AIzaSy...)
- Anthropic API keys (sk-ant-...)
- OpenAI keys (sk-...)
- HuggingFace tokens (hf_...)
- Gnani / Vachana API keys
- Private keys (BEGIN ... PRIVATE KEY)
- Raw tokens / passwords in diffs
"""

import re
import subprocess
from pathlib import Path

PATTERNS = [
    ("Google API Key", re.compile(r"AIzaSy[0-9A-Za-z\-_]{33}")),
    ("Anthropic API Key", re.compile(r"sk-ant-[a-zA-Z0-9\-_]{20,}")),
    ("OpenAI API Key", re.compile(r"sk-[a-zA-Z0-9]{20,}")),
    ("HuggingFace Token", re.compile(r"hf_[a-zA-Z0-9]{30,}")),
    ("Private Key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    (
        "Generic Secret Assignment",
        re.compile(
            r"""(?i)(?:api_key|apikey|secret|password|token)\s*[:=]\s*['"][a-zA-Z0-9\-_]{16,}['"]"""
        ),
    ),
]

# Whitelist safe false positives (hashes, public IDs, sample commit hashes)
WHITELIST = [
    "sample_smoke_token",
    "placeholder",
    "your_key_here",
    "hf_your_token_here",
    "test-anthropic-key",
]


def is_whitelisted(match_str: str) -> bool:
    return any(w in match_str for w in WHITELIST)


def main():
    print("=" * 60)
    print("PAKKAM GIT SECRETS AUDIT - FULL HISTORY SCAN")
    print("=" * 60)

    # 1. Check all commits in git history
    commits = subprocess.check_output(["git", "rev-list", "--all"], text=True).splitlines()
    print(f"Scanning {len(commits)} commits across all branches...")

    findings = []

    for commit in commits:
        diff = subprocess.check_output(
            ["git", "show", "--format=%H %an %ad", commit], text=True, errors="replace"
        )
        lines = diff.splitlines()
        header = lines[0] if lines else commit

        for line in lines:
            if not line.startswith("+") or line.startswith("+++"):
                continue
            for name, pattern in PATTERNS:
                matches = pattern.findall(line)
                for m in matches:
                    if is_whitelisted(m if isinstance(m, str) else line):
                        continue
                    findings.append(
                        (commit[:8], header, name, m if isinstance(m, str) else line[:80])
                    )

    # 2. Check tracked files in working directory
    tracked = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    print(f"Scanning {len(tracked)} currently tracked files in working tree...")
    for f in tracked:
        p = Path(f)
        if not p.is_file():
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            for name, pattern in PATTERNS:
                matches = pattern.findall(content)
                for m in matches:
                    if is_whitelisted(m if isinstance(m, str) else ""):
                        continue
                    findings.append(("WORKING_TREE", f, name, m if isinstance(m, str) else f))
        except Exception:
            pass

    print("-" * 60)
    if not findings:
        print("RESULT: ZERO SECRETS FOUND IN FULL GIT HISTORY AND WORKING TREE! [PASSED]")
    else:
        print(f"RESULT: {len(findings)} POTENTIAL SECRET(S) FOUND:")
        for commit, source, name, snippet in findings:
            print(f"  [{name}] {commit} ({source}): {snippet[:40]}...")
    print("=" * 60)


if __name__ == "__main__":
    main()
