import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

TOKEN = os.environ["WAKATIME_OAUTH_TOKEN"]
URL = "https://wakatime.com/api/v1/users/current/stats/last_7_days"
README = "README.md"
BAR_WIDTH = 25
LANG_COUNT = 5


def fetch_stats():
    req = urllib.request.Request(URL, headers={"Authorization": f"Bearer {TOKEN}"})
    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    return json.load(resp)["data"]
                print(f"Attempt {attempt}: status {resp.status}, retrying")
        except urllib.error.HTTPError as e:
            print(f"Attempt {attempt}: HTTP {e.code} {e.read().decode()[:200]}")
            if e.code in (401, 403):
                sys.exit("Token rejected: check scope (read_stats) and expiry")
        time.sleep(15 * attempt)
    sys.exit("Could not fetch WakaTime stats")


def bar(percent):
    filled = round(percent / 100 * BAR_WIDTH)
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def build_block(data):
    langs = data.get("languages", [])[:LANG_COUNT]
    lines = [f"Total Time: {data['human_readable_total']}", ""]
    for lang in langs:
        lines.append(
            f"{lang['name']:<12} {lang['text']:<20} {bar(lang['percent'])}   {lang['percent']:05.2f} %"
        )
    return "```txt\n" + "\n".join(lines) + "\n```"


def main():
    data = fetch_stats()
    block = build_block(data)
    with open(README, encoding="utf-8") as f:
        content = f.read()
    pattern = r"(<!--START_SECTION:waka-->)(.*?)(<!--END_SECTION:waka-->)"
    if not re.search(pattern, content, flags=re.S):
        sys.exit("Waka markers not found in README")
    new = re.sub(pattern, lambda m: f"{m.group(1)}\n\n{block}\n\n{m.group(3)}", content, flags=re.S)
    with open(README, "w", encoding="utf-8") as f:
        f.write(new)
    print("README updated")


if __name__ == "__main__":
    main()