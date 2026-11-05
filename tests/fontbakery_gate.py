# /// script
# requires-python = ">=3.12"
# ///
"""Fail on any fontbakery FAIL/ERROR/FATAL that isn't on the allowlist. WARNs pass.

    uv run --python 3.13 --with fontbakery==1.1.0 fontbakery check-universal --json fb.json \\
        "fonts/Toffee[SHDW,slnt,wght].ttf" || true
    uv run tests/fontbakery_gate.py fb.json
"""

import json
import re
import sys

# (check id, log code): why it's expected.
ALLOWED = {
    ("family/win_ascent_and_descent", "descent"): "usWinDescent covers the longest shadow, so Windows doesn't clip it",
}


def main(path):
    report = json.load(open(path))
    bad, seen = [], set()
    for section in report["sections"]:
        for check in section["checks"]:
            cid = re.search(r"FontBakeryCheck:([^>]+)>", check["key"][1]).group(1)
            for log in check["logs"]:
                if log["status"] not in ("FAIL", "ERROR", "FATAL"):
                    continue
                msg = log["message"]
                code = msg.get("code") if isinstance(msg, dict) else None
                text = msg.get("message", "") if isinstance(msg, dict) else str(msg)
                if (cid, code) in ALLOWED:
                    seen.add((cid, code))
                    print(f"expected {log['status']} {cid} [{code}]: {ALLOWED[(cid, code)]}")
                else:
                    bad.append(f"{log['status']} {cid} [{code}]: {text[:300]}")
    for key in ALLOWED.keys() - seen:
        print(f"note: allowlisted {key[0]} [{key[1]}] no longer fails; drop it from ALLOWED")
    print("fontbakery totals:", report["result"])
    if bad:
        print("\n".join(bad))
        raise SystemExit(f"{len(bad)} unexpected fontbakery result(s)")
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1])
