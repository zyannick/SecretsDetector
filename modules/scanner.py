import argparse
import re
import time
from collections import defaultdict

SECRET_PATTERNS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "github_token": r"ghp_[a-zA-Z0-9]{36}",
    "google_api_key": r"AIza[0-9A-Za-z\-_]{35}",
    "slack_token": r"xox[bp]-[0-9]{12}-[0-9]{13}-[a-zA-Z0-9]{24}",
    "generic_key": r"[a-zA-Z0-9\-_]{20,}"
}

metrics = {
    "files_scanned": 0,
    "secrets_found": 0,
    "scan_duration_seconds": 0.0,
    "findings_by_type": defaultdict(int)
}

def scan_file(filepath):
    print(f"\n[INFO] Scanning {filepath}...")
    found_secrets = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for secret_type, pattern in SECRET_PATTERNS.items():
                    for match in re.finditer(pattern, line):
                        finding = {
                            "file": filepath,
                            "line": line_num,
                            "type": secret_type,
                            "value": match.group(0)
                        }
                        found_secrets.append(finding)
                        metrics["secrets_found"] += 1
                        metrics["findings_by_type"][secret_type] += 1
    except Exception as e:
        print(f"[ERROR] Could not read file {filepath}: {e}")
    return found_secrets
